import selectors
from request_processor import RequestProcessor


class Protocol:
    def __init__(self, handler, selector, sock, addr):        
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request_processor = RequestProcessor(handler, sock, addr)

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            return self.read()
        if mask & selectors.EVENT_WRITE:
            return self.write()

    def read(self):
        return self.request_processor.process()

    def write(self):
        return True

    def close(self):
        print(f"Closing connection to {self.addr}")        
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"Error: selector.unregister() exception for "
                f"{self.addr}: {e!r}"
            )

        try:
            self.sock.close()
        except OSError as e:
            print(f"Error: socket.close() exception for {self.addr}: {e!r}")
