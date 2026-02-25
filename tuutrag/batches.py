import os
import json

from typing import Dict, Any, Union
from pathlib import Path


def create_request(
        text: str,
        uuid: Union[str, Any],
) -> Dict[str, Any]:
    req: Dict[str, Any] = {
        "key": uuid,
        "request": {
            "content": [
                {
                    "parts": [
                        {
                            "text": text,
                        }
                    ]
                }
            ]
        }
    }
    return req

def write_jsonl(
        requests: list[Dict[str, Any]],
        file_name: str,
) -> None:
    output_path = os.path.abspath(Path(__file__).parent.parent / f"data/gemini_batches/{file_name}.jsonl")

    with open(output_path, "w", encoding="utf-8") as f:
        for req in requests:
            f.write(json.dumps(req, ensure_ascii=False) + "\n")

    print(f"Wrote {len(requests)} request(s) → {output_path}")