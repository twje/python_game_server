import struct
import utils
from socket_reader import SocketReader


__all__ = ["RequestProcessor"]


# ------
# States
# ------
class ProtocolHeader:
    def __init__(self, processor):
        self.processor = processor
        self.jsonheader_length = None

    def update(self, recv_buffer):
        """Parse fixed-length header."""
        hdrlen = 2
        if len(recv_buffer) < hdrlen:
            return 0

        self.jsonheader_length = struct.unpack(
            ">H",
            recv_buffer[:hdrlen]
        )[0]
        return hdrlen

    def transition(self):
        self.processor.state = Header(self.processor, self.jsonheader_length)


class Header:
    def __init__(self, processor, length):
        self.processor = processor
        self.length = length
        self.jsonheader = None

    def update(self, recv_buffer):
        """Parse headers."""
        if len(recv_buffer) < self.length:
            return 0

        self.jsonheader = utils.decode_json_from_bytes(
            recv_buffer[:self.length], "utf-8"
        )
        self.validate()
        return self.length

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
        self.processor.state = Payload(self.processor, self.jsonheader)


class Payload:
    def __init__(self, processor, jsonheader):
        self.processor = processor
        self.jsonheader = jsonheader
        self.payload = None

    def update(self, recv_buffer):
        """Parse payload."""
        content_len = self.jsonheader["content-length"]
        if len(recv_buffer) < content_len:
            return 0

        data = recv_buffer[:content_len]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.payload = utils.decode_json_from_bytes(data, encoding)
        else:
            self.payload = data

        return content_len

    def transition(self):
        self.processor.state = ProtocolHeader(self.processor)


# -------------
# State Manager
# -------------
class RequestProcessor:
    def __init__(self, client_sock, addr):
        self.socket_stream = SocketReader(client_sock, addr)
        self.state = ProtocolHeader(self)

    def process(self):
        payloads = []
        recv_buffer = self.socket_stream.read()

        while recv_buffer:
            length = self.state.update(recv_buffer)
            if length == 0:
                break
            recv_buffer = self.socket_stream.consume_receive_buffer(length)

            if isinstance(self.state, Payload):
                payload = self.state.payload
                payloads.append(payload)

            self.state.transition()

        return payloads

    def is_connected(self):
        return self.socket_stream.is_connected