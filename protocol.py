import selectors
from request_processor import RequestProcessor


class Protocol:
    def __init__(self, handler, selector, sock, addr):
        self.handler = handler
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request_processor = RequestProcessor(sock, addr)

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            return self.read()
        if mask & selectors.EVENT_WRITE:
            return self.write()

    def read(self):
        payloads = self.request_processor.process()
        for payload in payloads:
            print(payload)

        return self.request_processor.is_connected()

    def write(self):
        return True

    def close(self):
        print(f"Closing connection to {self.addr}")
        self.is_connected = False
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
