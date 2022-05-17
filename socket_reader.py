class SocketReader:
    def __init__(self, sock, addr):        
        self.sock = sock
        self.addr = addr
        self.recv_buffer = b""
        self.is_connected = True

    def read(self):
        try:
            data = self.sock.recv(4096)
            if data:
                self.recv_buffer += data
            else:
                self.recv_buffer = data
                self.is_connected = False

        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass

        return self.recv_buffer

    def consume_receive_buffer(self, length):
        self.recv_buffer = self.recv_buffer[length:]
        return self.recv_buffer

    def is_empty(self):
        return len(self.recv_buffer) == 0
