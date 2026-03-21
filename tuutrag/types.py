from typing import Literal, TypedDict


class BranchChunk(TypedDict):
    uuid: str
    chunk: str
    path: str
    type: str

class BranchSummary(TypedDict):
    uuid: str
    text: str

class LocalRelation(TypedDict):
    uuid: str
    chunk: str
    entities: list[str]

class TextContent(TypedDict):
    type: Literal["text"]
    text: str


class Message(TypedDict):
    role: Literal["system", "user"]
    content: str | list[TextContent]


class RequestBody(TypedDict):
    model: str
    messages: list[Message]
    stream: Literal[False]


class BatchRequest(TypedDict):
    custom_id: str
    method: Literal["POST"]
    url: Literal["/v1/chat/completions"]
    body: RequestBody