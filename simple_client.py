from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper
from threading import Thread
from datetime import datetime
import time

class SimpleClient(EWrapper, EClient):
    ''' Serves as the client and the wrapper '''

    def __init__(self, addr, port, client_id):
        EWrapper.__init__
        EClient.__init__(self, self)

        # Connect to TWS
        self.connect(addr, port, client_id)

        # Launch the client thread
        thread = Thread(target=self.run)
        thread.start()

    @iswrapper # helps distinguish b/w EWrapper methods and other methods. This is a callback method for the reqCurrentTime method
    def currentTime(self, cur_time):
        t = datetime.fromtimestamp(cur_time)
        print('Current time: {}'.format(t))

    @iswrapper
    def error(self, req_id, code, msg):
        print('Error {}: {}'.format(code, msg))


def main():

    # Create the client instance and connect to TWS
    client = SimpleClient('127.0.0.1', 7497, 0)

    # Request the current time
    client.reqCurrentTime()

    # Sleep while the request is processed
    time.sleep(0.5)

    # Disconnect from TWS
    client.disconnect()


if __name__ == "__main__":
    main()
