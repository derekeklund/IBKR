from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition
from ibapi.order import *
from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue
from ibapi.utils import iswrapper
from threading import Thread
from datetime import datetime
import time

'''
This script creates bracket order to...
1. buy IBM using the IBKR API's adaptive algorithm (main order)
2. a sell limit order (profit taking) for if the stock rises to 170 (first child)
3. a sell stop order (stop loss) if it falls to 120 (second child)

* This algo has a volume condition. Play around with this (Chapter 10)
** Note the main_order and 1st child have .transmit set to False and the 2nd child has .transmit set to True. Follow up on this and test it.
*** For my debit spread algo, I'll probably be looking at PriceCondition, PercentChangeCondition and possibly TimeCondition
'''

class AdvOrder(EWrapper, EClient):
    ''' Serves as the client and the wrapper '''

    def __init__(self, addr, port, client_id):
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        # Connect to TWS
        self.connect(addr, port, client_id)
        self.order_id = 0
        self.con_id = 0
        self.exch = ''

        # Launch the client thread
        thread = Thread(target=self.run)
        thread.start()

    @iswrapper
    def contractDetails(self, reqId, details):
        ''' Obtain details for the contract '''
        self.con_id = details.contract.conId
        self.exch = details.contract.exchange

    @iswrapper
    def nextValidId(self, order_id):
        ''' Obtain an ID for the order '''
        self.order_id = order_id

    @iswrapper
    def orderStatus(self, order_id, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        ''' Check the status of the submitted order '''
        print('Order status: {}'.format(status))

    @iswrapper
    def error(self, req_id, code, msg):
        print('Error {}: {}'.format(code, msg))

def main():
    client = AdvOrder('127.0.0.1', 7497, 0)
    time.sleep(0.5)

    # Define the contract
    con = Contract()
    con.symbol = 'IBM'
    con.secType = 'STK'
    con.currency = 'USD'
    con.exchange = 'SMART'

    # Get unique ID for contract
    client.reqContractDetails(0, con)
    time.sleep(3)

    # Create a volume condition
    vol_condition = Create(OrderCondition.Volume)
    vol_condition.conId = client.con_id
    vol_condition.exchange = client.exch
    vol_condition.isMore = True
    vol_condition.volume = 20000

    # Obtain an ID for the main order
    client.reqIds(1000)
    time.sleep(2)

    # Create the bracket order
    main_order = Order()
    main_order.orderId = client.order_id
    main_order.action = 'BUY'
    main_order.orderType = 'MKT'
    main_order.totalQuantity = 100
    main_order.transmit = False
    main_order.eTradeOnly = False
    main_order.firmQuoteOnly = False
    main_order.conditions.append(vol_condition)

    # Set the algorithm for the order
    main_order.algoStrategy = 'Adaptive'
    main_order.algoParams = []
    main_order.algoParams.append(TagValue('adaptivePriority', 'Patient'))

    # First child order - limit order
    first_child = Order()
    first_child.orderId = client.order_id + 1
    first_child.action = 'SELL'
    first_child.orderType = 'LMT'
    first_child.totalQuantity = 100
    first_child.lmtPrice = 170
    first_child.parentId = client.order_id
    first_child.transmit = False
    first_child.eTradeOnly = False
    first_child.firmQuoteOnly = False

    # Stop order child
    second_child = Order()
    second_child.orderId = client.order_id + 2
    second_child.action = 'SELL'
    second_child.orderType = 'STP'
    second_child.totalQuantity = 100
    second_child.auxPrice = 120
    second_child.parentId = client.order_id
    second_child.transmit = True
    second_child.eTradeOnly = False
    second_child.firmQuoteOnly = False

    # Submit each order
    client.placeOrder(client.order_id, con, main_order)
    client.placeOrder(client.order_id + 1, con, first_child)
    client.placeOrder(client.order_id + 2, con, second_child)

    # Sleep while the request is processed
    time.sleep(5)
    client.disconnect()

if __name__ == '__main__':
    main()
