import selectors


class SocketStream:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.recv_buffer = b""
        self.send_buffer = b""

    def process(self, mask):
        if mask & selectors.EVENT_READ:
            self._read()
        if mask & selectors.EVENT_WRITE:
            self._write()

    def consume_receive_buffer(self, length):
        self.recv_buffer = self.recv_buffer[length:]

    # --------------
    # Helper Methods
    # --------------
    def _read(self):
        try:
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self.recv_buffer += data

    def _write(self):
        if self.send_buffer:
            print(f"Sending {self.send_buffer!r} to {self.addr}")
            try:
                sent = self.sock.send(self.send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self.send_buffer = self.send_buffer[sent:]
