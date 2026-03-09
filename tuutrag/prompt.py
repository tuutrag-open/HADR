from tuutrag.types import BatchRequest


def create_batch_request(
    custom_id: str,
    model: str,
    **kwargs
) -> BatchRequest:
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "messages": [
                {"role": "system", "content": kwargs["system"]},
                {"role": "user", "content": kwargs["user"]},
            ],
            "stream": False,
        },
    }