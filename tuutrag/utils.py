from tiktoken.core import Encoding
from tuutrag.types import BatchRequest

def count_batch_request_tokens(enc: Encoding, payload: BatchRequest) -> int:
    total = 0
    for message in payload["body"]["messages"]:
        content = message["content"]
        if isinstance(content, str):
            total += len(enc.encode(content))
        elif isinstance(content, list):
            for block in content:
                if block.get("type") == "text":
                    total += len(enc.encode(block["text"]))
    return total
