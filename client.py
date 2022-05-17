import sys
import socket
import struct
import utils

HOST = "127.0.0.1"
PORT = 65432


def create_message():
    content = {"A": 1, "B": 2}
    content_type = "text/json"
    content_encoding = "utf-8"
    content_bytes = utils.encode_json_to_bytes(content, content_encoding)
    headers = {
        "byteorder": sys.byteorder,
        "content-type": content_type,
        "content-encoding": content_encoding,
        "content-length": len(content_bytes),
    }
    jsonheader_bytes = utils.encode_json_to_bytes(headers, "utf-8")
    message_hdr = struct.pack(">H", len(jsonheader_bytes))    
    message = message_hdr + jsonheader_bytes + content_bytes
    return message

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    message = create_message()    
    s.sendall(message)
    input("Hit enter to exit")
