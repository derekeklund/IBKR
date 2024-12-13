from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from ibapi.utils import iswrapper
from threading import Thread
from datetime import datetime
import time
import numpy as np
from collections import deque
import matplotlib.pyplot as plt

'''
Compare MSTR to BTC by the hour for the last week
'''

class PairsTrade(EWrapper, EClient):
    ''' Client & Wrapper '''

    def __init__(self, addr, port, client_id):
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        # Connect to TWS
        self.connect(addr, port, client_id)

        # Launch the client thread
        thread = Thread(target=self.run)
        thread.start()

        self.btc_prices = []
        self.mstr_prices = []
        self.difference = []

    @iswrapper
    def historicalData(self, reqId, bar):

        # Append the prices to the lists
        self.btc_prices.append(bar.close)
        self.mstr_prices.append(bar.close)

    @iswrapper
    def historicalDataEnd(self, reqId, start, end):
        print("Complete")


def main():
    client = PairsTrade('127.0.0.1', 7497, 0)
    time.sleep(0.5)

    # Create a BTC contract
    btc_contract = Contract()
    btc_contract.symbol = 'ETH'
    btc_contract.secType = 'CRYPTO'
    btc_contract.exchange = 'PAXOS'
    btc_contract.currency = 'USD'

    # Create am MSTR contract
    mstr_contract = Contract()
    mstr_contract.symbol = 'MSTR'
    mstr_contract.secType = 'STK'
    mstr_contract.exchange = 'SMART'
    mstr_contract.currency = 'USD'

    time.sleep(0.5)

    # Request historical bars
    now = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    client.reqHistoricalData(3, btc_contract, now, '1 w', '1 min', 'MIDPOINT', False, 1, False, [])

    time.sleep(5)
    client.disconnect()

    plt.figure(figsize=(10, 5))

    # Plot btc and mstr
    plt.plot(client.btc_prices, label='btc price')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
