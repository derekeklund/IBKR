from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract, ComboLeg
from ibapi.utils import iswrapper
from threading import Thread
from datetime import datetime
import time

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
    def contractDetails(self, reqID, contractDetails):
        print('Long name: {}'.format(contractDetails.longName))
        print('Symbol: {}'.format(contractDetails.contract.symbol))
        print('Category: {}'.format(contractDetails.category))
        print('Subcategory: {}'.format(contractDetails.subcategory))
        print('Contract ID: {}'.format(contractDetails.contract.conId))
        print('Strike: {}'.format(contractDetails.contract.strike))
        print('Right: {}'.format(contractDetails.contract.right))
        print('Expiration: {}'.format(contractDetails.contract.lastTradeDateOrContractMonth))
        print('Multiplier: {}\n'.format(contractDetails.contract.multiplier))
        

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

    # Define the combo contract
    contract = Contract()
    contract.symbol = 'AMZN'
    contract.secType = 'BAG' # BAG is the security type for combo orders (multi-leg orders)
    contract.currency = 'USD'
    contract.exchange = 'SMART'

    # First leg of combo
    leg1 = ComboLeg()
    leg1.conId = 3691937 # Contract ID for the first leg
    leg1.ratio = 1
    leg1.action = 'BUY'

    # Second leg of combo
    leg2 = ComboLeg()
    leg2.conId = 3691938 # Contract ID for the second leg
    leg2.ratio = 1
    leg2.action = 'SELL'

    # Add the legs to the combo contract
    contract.comboLegs = []
    contract.comboLegs.append(leg1)
    contract.comboLegs.append(leg2)

    
    # contract.lastTradeDateOrContractMonth = '20241213'
    # contract.right = 'C'
    client.reqContractDetails(1, contract)

    # Sleep while the request is processed
    time.sleep(3)

    # Disconnect from TWS
    client.disconnect()


if __name__ == "__main__":
    main()
