import json
from typing import List
from exports import export
from neo4j import GraphDatabase


@export
class MemgraphConnection:
    obj_name = "MemgraphConnection"
    workspace = "kg"

    def __init__(self, port: int, frontend_port: int, host: str) -> None:
        self.driver = self.__connect(port, frontend_port, host)

    def __connect(
        self, port: int, frontend_port: int, host: str
    ) -> GraphDatabase.driver:
        """Establishes a connection to the Memgraph database and verifies connectivity."""

        port = int(port)
        frontend_port = int(frontend_port)
        host = str(host)
        URI = f"bolt://{host}:{port}"

        frontend_connection_string = f"Creating Memgraph UI connection at {host}:{frontend_port}, view at: http://{host}:{frontend_port}/"
        backend_connection_string = f"Creating Memgraph Backend connection at {host}:{port}, view at: http://{host}:{port}/"
        try:
            driver = GraphDatabase.driver(URI, auth=("", ""))
            driver.verify_connectivity()
            print(frontend_connection_string)
            print(backend_connection_string)
            return driver
        except Exception as e:
            print(f"Error connecting to Memgraph at {URI}: {e}")
            raise

    def read_data(self, file_path: str) -> List:
        """Reads data from a JSONL file and extracts the relevant parts for upserting into Memgraph."""

        parts = []

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                for line in f:
                    data = json.loads(line)
                    text = data["text"]
                    content = text.split("<|>")[1]
                    part = [item.strip() for item in content.split(",")]
                    if len(part) == 3:
                        parts.append(part)
                    else:
                        print(f"Skipping malformed line: {line}")
            except Exception as e:
                print(f"Error reading entity_relationships.jsonl: {e}")

        return parts

    def upsert(self, data: List) -> None:
        """Upserts entity relationships into Memgraph from a JSONL file."""

        parts = data

        with self.driver.session() as session:
            for i, part in enumerate(parts):
                session.run(
                    """
                    MERGE (source:Entity {name: $source})
                    MERGE (target:Entity {name: $target})
                    MERGE (source)-[r:RELATIONSHIP]->(target)
                    SET r.type = $relationship
                    """,
                    source=part[0],
                    relationship=part[1],
                    target=part[2],
                )
                print(
                    f"upserted relationship {i+1}/{len(parts)}: {part[0]} -[{part[1]}]-> {part[2]}"
                )

    def upsert_global(self, data: List, batch_size: int = 5000) -> None:
        """Upserts global entity relationships into Memgraph with scope='global' in batches."""

        total = len(data)
        upserted = 0

        with self.driver.session() as session:
            for i in range(0, total, batch_size):
                batch = data[i : i + batch_size]

                params = [
                    {"source": part[0], "relationship": part[1], "target": part[2]}
                    for part in batch
                    if len(part) == 3 and all(part)
                ]

                session.run(
                    """
                    UNWIND $batch AS row
                    MERGE (source:Entity {name: row.source})
                    MERGE (target:Entity {name: row.target})
                    MERGE (source)-[r:RELATIONSHIP {type: row.relationship}]->(target)
                    SET r.scope = 'global'
                    """,
                    batch=params,
                )

                upserted += len(params)
                print(
                    f"  Batch {i // batch_size + 1}: {upserted:,} / {total:,} upserted"
                )

        print(f"\nDone — {upserted:,} global relations upserted")

    def upsert_universal(self, data: List, batch_size: int = 5000) -> None:
        """Upserts universal entity relationships into Memgraph with scope='universal' in batches."""

        total = len(data)
        upserted = 0

        with self.driver.session() as session:
            for i in range(0, total, batch_size):
                batch = data[i : i + batch_size]

                params = [
                    {"source": part[0], "relationship": part[1], "target": part[2]}
                    for part in batch
                    if len(part) == 3 and all(part)
                ]

                session.run(
                    """
                    UNWIND $batch AS row
                    MERGE (source:Entity {name: row.source})
                    MERGE (target:Entity {name: row.target})
                    MERGE (source)-[r:RELATIONSHIP {type: row.relationship}]->(target)
                    SET r.scope = 'universal'
                    """,
                    batch=params,
                )

                upserted += len(params)
                print(
                    f"  Batch {i // batch_size + 1}: {upserted:,} / {total:,} upserted"
                )

        print(f"\nDone — {upserted:,} universal relations upserted")
