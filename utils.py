import io
import json

def decode_json_from_bytes(json_bytes, encoding):
    tiow = io.TextIOWrapper(
        buffer=io.BytesIO(json_bytes), 
        encoding=encoding, 
        newline=""
    )
    obj = json.load(tiow)
    tiow.close()
    return obj


def encode_json_to_bytes(obj, encoding):
    return json.dumps(obj, ensure_ascii=False).encode(encoding)
