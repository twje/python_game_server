import struct
import utils
from socket_read_stream import SocketReadStream


__all__ = ["Request"]


# ------
# States
# ------
class ProtocolHeader:
    def __init__(self, request):
        self.request = request
        self.socket_stream = self.request.socket_stream
        self.jsonheader_length = None

    def update(self):
        """Parse fixed-length header."""
        hdrlen = 2
        recv_buffer = self.socket_stream.read()
        if len(recv_buffer) < hdrlen:
            return False

        self.jsonheader_length = struct.unpack(
            ">H",
            recv_buffer[:hdrlen]
        )[0]
        self.socket_stream.consume_receive_buffer(hdrlen)
        return True

    def transition(self):
        self.request.state = Header(self.request, self.jsonheader_length)


class Header:
    def __init__(self, request, length):
        self.request = request
        self.socket_stream = self.request.socket_stream
        self.length = length
        self.jsonheader = None

    def update(self):
        """Parse headers."""
        recv_buffer = self.socket_stream.read()
        if len(recv_buffer) < self.length:
            return False

        self.jsonheader = utils.decode_json_from_bytes(
            recv_buffer[:self.length], "utf-8"
        )
        self.socket_stream.consume_receive_buffer(self.length)
        self.validate()
        return True

    def validate(self):
        for reqhdr in (
            "byteorder",
            "content-length",
            "content-type",
            "content-encoding",
        ):
            if reqhdr not in self.jsonheader:
                raise ValueError(f"Missing required header '{reqhdr}'.")

    def transition(self):
        self.request.state = Payload(self.request, self.jsonheader)


class Payload:
    def __init__(self, request, jsonheader):
        self.request = request
        self.socket_stream = self.request.socket_stream
        self.jsonheader = jsonheader
        self.payload = None

    def update(self):
        """Parse payload."""
        recv_buffer = self.socket_stream.read()
        content_len = self.jsonheader["content-length"]
        if len(recv_buffer) < content_len:
            return False

        data = recv_buffer[:content_len]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.payload = utils.decode_json_from_bytes(data, encoding)
        else:
            self.payload = data

        self.socket_stream.consume_receive_buffer(content_len)
        return True

    def transition(self):
        pass


# -------------
# State Manager
# -------------
class RequestProcessor:
    def __init__(self, selector, client_sock, addr):
        self.socket_stream = SocketReadStream(selector, client_sock, addr)
        self.state = ProtocolHeader(self)

    def process(self):
        payloads = []
        while True:
            self.parse_massage()

            if self.is_message_parsed():
                payload = self.reset_parser()
                payloads.append(payload)

            if self.are_all_messages_parsed():
                break

        return payloads

    def reset_parser(self):
        payload = self.state.payload
        self.state = ProtocolHeader(self)
        return payload

    def parse_massage(self):
        while self.state.update():
            self.state.transition()

    def is_message_parsed(self):
        return isinstance(self.state, Payload)

    def are_all_messages_parsed(self):
        return self.socket_stream.is_empty()
