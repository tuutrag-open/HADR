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


def test_uuid(test_file: str, uuid_file: str) -> None:
    """Generate a UUID for a given file path."""
    global collision_count

    print("Generating UUID for data")
    update_count = 0
    tests = []

    with open(test_file, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"Error reading JSON from file: {test_file}")
            return

        for element in data:
            test = element.split("\n", 2)[1]
            uuid = generate_uuid()

            if uuid in collision_check:
                print(f"Collision detected for UUID: {uuid}")
                collision_count += 1
            else:
                collision_check[uuid] = True
                update_count += 1
                test_dict = {"uuid": uuid, "test case": test}
                tests.append(test_dict)

            print(f"Generated UUIDs for {update_count} / {len(data)} elements")

    with open(uuid_file, "w", encoding="utf-8") as file:
        json.dump(tests, file, ensure_ascii=False, indent=4)

    print(f"Finished generating UUIDs. Total collisions: {collision_count}")


if __name__ == "__main__":
    test_file = Path(__file__).parent.parent / "data" / "tests.json"
    new_file = Path(__file__).parent.parent / "data" / "test_uuid_mapping.json"

    test_uuid(test_file, new_file)
