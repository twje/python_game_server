
import socket
import selectors
from message_emitter import MessageEmitter
from protocol import Protocol


class Server:
    def __init__(self, host, port):
        self.selector = selectors.DefaultSelector()
        self.sock = self.create_server_socket(host, port)
        self.handler = MessageEmitter()

    def create_server_socket(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen()
        print(f"Listening on {(host, port)}")
        sock.setblocking(False)
        self.selector.register(sock, selectors.EVENT_READ, data=None)
        return sock

    def accept_client_connection(self, client_sock):
        conn, addr = client_sock.accept()
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        protocol = Protocol(self.handler, self.selector, conn, addr)
        mask = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, mask, data=protocol)

    def process_client_request(self, key, mask):
        protocol = key.data
        is_connected = protocol.process_events(mask)
        if not is_connected:
            protocol.close()

    def subscribe(self, event_type, observer):
        return self.handler.subscribe(event_type, observer)

    def unsubscribe(self, event_type, observer):
        return self.handler.unsubscribe(event_type, observer)

    def update(self):
        events = self.selector.select(timeout=0)
        for key, mask in events:
            if key.data is None:
                self.accept_client_connection(key.fileobj)
            else:
                self.process_client_request(key, mask)


class TestMessageHandler():
    def notify(self, event_type, message):
        print(event_type, message.data)


if __name__ == "__main__":
    server = Server("127.0.0.1", 65432)

    # init subscribers
    server.handler.subscribe("foo", TestMessageHandler())

    while True:
        server.update()
