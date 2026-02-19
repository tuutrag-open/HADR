import os
import json
import uuid
from pathlib import Path


def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


collision_check = {}
collision_count = 0


def req_uuid(directory: str) -> None:
    """Generate a UUID for a given file path."""
    global collision_count

    print("Generating UUID for Supplemental Data")
    update_count = 0

    for file in os.listdir(directory):
        if file.endswith(".JSON"):
            file_path = os.path.join(directory, file)

            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file {file_path}")
                    return None

                uuid = generate_uuid()
                if uuid in collision_check:
                    print(f"Collision detected for UUID: {uuid}")
                    collision_count += 1
                else:
                    collision_check[uuid] = True
                    update_count += 1
                    if "uuid" not in data[0]["dataDictionary"]:
                        data[0]["dataDictionary"] = {
                            "uuid": uuid,
                            **data[0]["dataDictionary"],
                        }
                    print(
                        f"Generated UUIDs for {update_count} / {len(os.listdir(directory))} elements"
                    )

                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Finished generating UUIDs. Total collisions: {collision_count}")


if __name__ == "__main__":
    # new_result_file = Path(__file__).parent.parent / "data" / "results_with_uuid.json"
    # req_path = Path(__file__).parent.parent / "data" / "requirements.json"
    directory = Path(__file__).parent.parent / "data" / "supplemental" / "artifacts"

    req_uuid(directory)
