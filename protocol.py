import selectors
from request_processor import RequestProcessor


class Protocol:
    def __init__(self, selector, client_sock, addr):
        self.request_processor = RequestProcessor(selector, client_sock, addr)
        self.response = None

    def process_events(self, mask):        
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):        
        payloads = self.request_processor.process()
        for payload in payloads:        
            print(payload)

    def write(self):
        pass
