import os
import json
import uuid
from pathlib import Path


def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


collision_check = {}
collision_count = 0


def req_uuid(new_file: str, file_path: str) -> None:
    global collision_count
    """Generate a UUID for a given file path."""
    print("Generating UUID for Requiremenets")
    update_count = 0
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
            length = len(data)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file {file_path}")
            return None
        for element in data:
            uuid = generate_uuid()
            if uuid in collision_check:
                print(f"Collision detected for UUID: {uuid}")
                collision_count += 1
            else:
                element["uuid"] = uuid
                collision_check[uuid] = True
                update_count += 1
                print(f"Generated UUIDs for {update_count} / {length} elements")

    with open(new_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Finished generating UUIDs. Total collisions: {collision_count}")


if __name__ == "__main__":
    new_result_file = Path(__file__).parent.parent / "data" / "results_with_uuid.json"
    req_path = Path(__file__).parent.parent / "data" / "requirements.json"

    req_uuid(new_result_file, req_path)
