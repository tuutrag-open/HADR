from qdrant_client import QdrantClient
from tuutrag.utils import log_timestamp
from pathlib import Path

IMAGE = "qdrant/qdrant:latest"


class VectorDB():
    def __init__(self, port: int, host: str):
        self.client = self.connect(port, host)

    def connect(self, port: int, host: str):
        port = int(port)
        host = str(host)
        storage = str(Path(__file__).parent / "data/qdrant")

        try:
            client = QdrantClient(port=port, host=host, timeout=50, https=False)
            log_timestamp(f"Connected to http://{host}:{port}/dashboard")
            log_timestamp(f"Storage will be at {storage}")
            return client
        except Exception as e:
            raise RuntimeError(f"Error connecting to Qdrant server: {e}")

    def create_collection(self, collection_name, vector_params) -> None:
        if self.client.collection_exists(collection_name=collection_name):
            return

        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=vector_params
            )
            log_timestamp(f"Collection '{collection_name}' created")
        except Exception as e:
            log_timestamp(f"Error {e}")

    def upsert(self, collection_name: str, point) -> None:
        if not self.client.collection_exists(collection_name=collection_name):
            raise f"Collection '{collection_name}' does not exists"

        self.client.upsert(
            collection_name=collection_name,
            points=point,
            wait=True
        )