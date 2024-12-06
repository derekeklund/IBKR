from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.utils import iswrapper
from threading import Thread
from datetime import datetime
import time

''' Important! TWS throttles requests so you might have to wait a bit in between requests '''

class ContractReader(EWrapper, EClient):
    ''' Serves as the client and the wrapper '''

    def __init__(self, addr, port, client_id):
        EWrapper.__init__
        EClient.__init__(self, self)

        # Connect to TWS
        self.connect(addr, port, client_id)

        # Launch the client thread
        thread = Thread(target=self.run)
        thread.start()

    @iswrapper
    def symbolSamples(self, reqID, descs):

        # Print the symbols in returned results
        print('Number of descriptions: {}'.format(len(descs)))
        for desc in descs:
            print('Symbol: {}'.format(desc.contract.symbol))

        # Choose the first symbol
        self.symbol = descs[0].contract.symbol

    @iswrapper
    def contractDetails(self, reqID, contractDetails):
        print('Long name: {}'.format(contractDetails.longName))
        print('Category: {}'.format(contractDetails.category))
        print('Subcategory: {}'.format(contractDetails.subcategory))
        print('Contract ID: {}\n'.format(contractDetails.contract.conId))

    @iswrapper
    def contractDetailsEnd(self, reqId):
        print('The End')

    @iswrapper
    def error(self, req_id, code, msg):
        print('Error {}: {}'.format(code, msg))


def main():

    # Create the client instance and connect to TWS
    client = ContractReader('127.0.0.1', 7497, 0)
    time.sleep(0.5)

    # Request descriptions of contracts related to cheescake
    client.reqMatchingSymbols(0, 'Cheesecake')
    time.sleep(3)

    # Request details for the stock
    contract = Contract()
    contract.symbol = client.symbol
    contract.secType = 'OPT'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    client.reqContractDetails(1, contract)

    # Sleep while the request is processed
    time.sleep(3)

    # Disconnect from TWS
    client.disconnect()


if __name__ == "__main__":
    main()
