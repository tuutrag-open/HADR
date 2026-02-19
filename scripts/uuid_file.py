from importlib.metadata import files
import os
import json
import uuid
from pathlib import Path


def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


collision_check = {}
collision_count = 0


def uuid_file(directory: str, uuid_file: str) -> None:
    """Generate a UUID for a given file path."""
    global collision_count

    print("Generating UUID for data")
    update_count = 0
    files = []

    for file in os.listdir(directory):
        file_dict = {}

        uuid = generate_uuid()
        if uuid in collision_check:
            print(f"Collision detected for UUID: {uuid}")
            collision_count += 1
        else:
            collision_check[uuid] = True
            update_count += 1

            file_dict["uuid"] = uuid
            file_dict["file"] = file
            files.append(file_dict)

            print(
                f"Generated UUIDs for {update_count} / {len(os.listdir(directory))} elements"
            )

    with open(uuid_file, "w", encoding="utf-8") as file:
        json.dump(files, file, ensure_ascii=False, indent=4)

    print(f"Finished generating UUIDs. Total collisions: {collision_count}")


if __name__ == "__main__":
    directory = Path(__file__).parent.parent / "data" / "supplemental" / "artifacts"
    new_file = Path(__file__).parent.parent / "data" / "file_uuid_mapping.json"

    uuid_file(directory, new_file)
