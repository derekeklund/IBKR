from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue
from ibapi.utils import iswrapper
from threading import Thread
from datetime import datetime
import time

''' 
*** Only 50 results per scan code can be completed 

This scan finds stocks that meet the following criteria:
1. Highest option volumes (most traded)
2. Market Cap above 100 billion
3. Max PE ratio of 30

Refer to chapter 9 (Scanning for Securities)
- pages 190 - 197 for codes

'''

class StockScanner(EWrapper, EClient):
    ''' Serves as the client and the wrapper '''

    def __init__(self, addr, port, client_id):
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        # Connect to TWS
        self.connect(addr, port, client_id)
        self.count = 0

        # Launch the client thread
        thread = Thread(target=self.run)
        thread.start()

    @iswrapper
    def scannerData(self, reqId, rank, details, distance, benchmark, projection, legsStr):
        # Print the symbols in the returned results
        print('{}: {}'.format(rank, details.contract.symbol))

        self.count += 1

    @iswrapper
    def scannerDataEnd(self, reqId):
        # Print the number of results
        print('Number of results: {}'.format(self.count))

    @iswrapper
    def error(self, reqId, code, msg):
        print('Error {}: {}'.format(code, msg))

def main():

    print("Scanning for options...")

    # Create the client and connect to TWS
    client = StockScanner('127.0.0.1', 7497, 0)
    time.sleep(0.5)

    # Create the ScannerSubscription object
    ss = ScannerSubscription()
    ss.instrument = 'STK'
    ss.locationCode = 'STK.US.MAJOR'
    ss.scanCode = 'OPT_VOLUME_MOST_ACTIVE'
    # ss.belowPrice = 100.0

    # Set additional filter criteria
    tagvalues = []
    tagvalues.append(TagValue('maxPeRatio', '30'))
    tagvalues.append(TagValue('marketCapAbove1e6', '100000')) # ie6 = 1mil

    # Request the scanner subscription
    client.reqScannerSubscription(0, ss, [], tagvalues)

    # Sleep while the request is processed
    time.sleep(5)
    client.disconnect()


if __name__ == '__main__':
    main()
