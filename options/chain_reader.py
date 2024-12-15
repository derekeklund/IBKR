from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from ibapi.utils import iswrapper
from threading import Thread
from datetime import datetime
import time


'''
Read options chain for a ticker

'''

### callback functions for read_option_chain ###

@iswrapper
def contractDetails(self, reqId, desc):
    ''' Obtain contract ID '''
    self.conid = desc.contract.conId

@iswrapper
def tickByTickMidPoint(self, reqId, time, midpoint):
    ''' Obtain current price '''
    self.current_price = midpoint

@iswrapper
def securityDefinitionOptionParameter(self, reqId, exchange, underlyingConId, tradingClass, multiplier, expirations, strikes):
    ''' Provide strike prices and expiration dates '''

    # Save expiration dates and strike prices
    self.exchange = exchange
    self.expirations = expirations
    self.strikes = strikes

@iswrapper
def securityDefinitionOptionParameterEnd(self, reqId):
    ''' Process data after receiving strikes/expirations '''

    # Find strike price closest to current price
    self.strikes = sorted(self.strikes)
    min_dist = 99999.0
    for i, strike in enumerate(self.strikes):
        if strike - self.current_price < min_dist:
            min_dist = abs(strike - self.current_price)
            self.atm_index = i
    self.atm_price = self.strikes[self.atm_index]

    print('ATM price: {}'.format(self.atm_price))

    # Limit strike prices to +7/-7 around ATM
    front = self.atm_index - 7
    back = len(self.strikes) - (self.atm_index + 7)
    if front > 0:
        del self.strikes[:front]
    if back > 0:
        del self.strikes[-(back-1):]

    # Find an expiration date just over a month away
    self.expirations = sorted(self.expirations) 
    for date in self.expirations:
        exp_date = datetime.strptime(date, '%Y%m%d')
        current_date = datetime.now()
        interval = exp_date - current_date
        if interval.days > 21:
            self.expiration = date
            print('Expiration: {}'.format(self.expiration))
            break

@iswrapper
def tickPrice(self, req_id, field, price, attribs):
    print("tickPrice (bid/ask price)")
    ''' Provide option's ask price/bid price '''

    if (field != 1 and field != 2) or price == -1.0:
        return

    # Determine the strike price and right
    strike = self.strikes[(req_id - 3)//2]
    right = 'C' if req_id & 1 else 'P' # DAFUK

    # Update the option chain
    if field == 1:
        self.chain[strike][right]['bid_price'] = price
    elif field == 2:
        self.chain[strike][right]['ask_price'] = price

@iswrapper
def tickSize(self, req_id, field, size):
    print("tickSize (bid/ask size)")
    ''' Provide option's ask size/bid size '''

    if (field != 0 and field != 3) or size == 0:
        return
    
    # Determine the strike price and right
    strike = self.strikes[(req_id - 3)//2]
    right = 'C' if req_id & 1 else 'P'

    # Update the option chain
    if field == 0:
        self.chain[strike][right]['bid_size'] = size
    elif field == 3:
        self.chain[strike][right]['ask_size'] = size

### function ###

def read_option_chain(client, ticker):

    # Define a contract for the underlying stock
    contract = Contract()
    contract.symbol = ticker
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    client.reqContractDetails(0, contract)
    time.sleep()

    # Get the current price of the stock
    client.reqTickByTickData(1, contract, "MidPoint", 1, True)
    time.sleep(4)

    # Request strike prices and expirations
    if client.conid:
        client.reqSecDefOptParams(2, ticker, '', 'STK', client.conid)
        time.sleep(2)

    else:
        print('Failed to obtain contract identifier.')
        exit()

    # Create contract for stock option
    req_id = 3
    if client.strikes:
        for strike in client.strikes:
            client.chain[strike] = {}
            for right in ['C', 'P']:

                # Add to the option chain
                client.chain[strike][right] = {}

                # Define the option contract
                contract.secType = 'OPT'
                contract.right = right
                contract.strike = strike
                contract.exchange = client.exchange
                contract.lastTradeDateOrContractMonth = client.expiration

                # Request option data
                client.reqMktData(req_id, contract, '100', False, False, [])
                req_id += 1
                time.sleep(1)

    else:
        print('Failed to access strike prices')
        exit()
        
    time.sleep(5)

    # Remove empty elements
    for strike in client.chain:
        if client.chain[strike]['C'] == {} or client.chain[strike]['P'] == {}:
            client.chain.pop(strike)

    return client.chain, client.atm_price
