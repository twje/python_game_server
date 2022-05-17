class SocketReadStream:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.recv_buffer = b""

    def read(self):
        try:
            data = self.sock.recv(4096)
            if data:
                self.recv_buffer += data
            else:                
                self.recv_buffer = data
                self.close()

        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass

        return self.recv_buffer

    def consume_receive_buffer(self, length):
        self.recv_buffer = self.recv_buffer[length:]
        return self.recv_buffer

    def is_empty(self):
        return len(self.recv_buffer) == 0

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
