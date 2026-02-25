import json
import tiktoken
from concurrent.futures import ThreadPoolExecutor


# Join all the data files into one big file, fix size chunk them, and create new id for branches

sup_data = "data/supplemental_uuid_mapping.json"
updated_sup_data = "data/updated_supplemental_uuid_mapping.json"
req_map = "data/requirement_uuid_mapping.json"
req_data = "data/requirements.json"
updated_req_data = "data/updated_requirements.json"
test_map = "data/test_uuid_mapping.json"
test_data = "data/tests.json"
updated_test_data = "data/updated_tests.json"
all_results = "data/all_extracted_results.json"
updated_results = "data/updated_all_extracted_results.json"
fixed_size_chunks = "data/fixed_size_chunks.json"


# Function gets all batch data files with uuid, creates a list of their contents, and returns the list
def get_all_results() -> list:
    map_results = {}
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    results_list = []
    with open(all_results, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {all_results}: {e}")
            return

        for element in data:
            content = element.get("content")
            uuid = element.get("uuid")
            if uuid in map_results:
                current_content = map_results[uuid]
                map_results[uuid] = current_content + "" + content
            else:
                map_results[uuid] = content

        for uuid, content in map_results.items():
            count = 0
            element_tokens = encoding.encode(str(content))

            while len(element_tokens) > 0:
                results = {}

                count += 1
                if len(element_tokens) > 512:
                    chunk = encoding.decode(element_tokens[:512])
                    element_tokens = element_tokens[512:]
                else:
                    chunk = encoding.decode(element_tokens)
                    element_tokens = []
                results["uuid"] = f"{uuid}.{count}"
                results["chunk"] = chunk
                results_list.append(results)

    print(f"Total chunks created: {len(results_list)}")

    return results_list


# Function retrieves test data with uuid, creates a list of the contents, and returns the list
def tests() -> list:
    """Join the test data files into one big file."""
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    local_tests_list = []
    map_test = {}

    with open(test_map, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {test_map}: {e}")
            return

        for element in data:
            uuid = element.get("uuid")
            test = element.get("test case")
            map_test[test] = uuid

    with open(test_data, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {test_data}: {e}")
            return

        for element in data:
            count = 0
            test = element.split("\n", 2)[1]
            if test in map_test:
                uuid = map_test[test]
                context = element
                tokens = encoding.encode(str(context))

                while len(tokens) > 0:
                    tests = {}

                    count += 1
                    if len(tokens) > 512:
                        chunk = encoding.decode(tokens[:512])
                        tokens = tokens[512:]
                    else:
                        chunk = encoding.decode(tokens)
                        tokens = []
                    tests["uuid"] = f"{uuid}.{count}"
                    tests["chunk"] = chunk
                    tests["test case"] = test
                    local_tests_list.append(tests)
            else:
                print(f"Test not found in mapping: {test}")
    print(f"Total chunks created: {len(local_tests_list)}")

    return local_tests_list


# Function retrieves requirement data with uuid, creates a list of the contents, and returns the list
def requirements() -> list:
    """Join the requirements data files into one big file."""
    local_requirements_list = []
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")

    mapping_requirements = {}

    with open(req_map, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {req_map}: {e}")
            return

        for element in data:
            uuid = element.get("uuid")
            req = element.get("requirement")
            mapping_requirements[req] = uuid

    with open(req_data, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {req_data}: {e}")
            return

        for element in data:
            requirements = {}
            count = 0
            req = element["requirement"].split("\n")[4]
            if req in mapping_requirements:
                context = element["requirement"]
                tokens = encoding.encode(str(context))

                while len(tokens) > 0:
                    count += 1
                    if len(tokens) > 512:
                        chunk = encoding.decode(tokens[:512])
                        tokens = tokens[512:]
                    else:
                        chunk = encoding.decode(tokens)
                        tokens = []
                    requirements["uuid"] = f"{mapping_requirements[req]}.{count}"
                    requirements["chunk"] = chunk
                    requirements["requirement"] = req
                    local_requirements_list.append(requirements)
            else:
                print(f"Requirement not found in mapping: {req}")

    print(f"Total chunks created: {len(local_requirements_list)}")

    return local_requirements_list


# Function gets all supplemental data files with uuid, creates a list of their contents, and returns the list
def supplemental(path) -> list:
    """Join the supplemental data files into one big file."""
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    count = 0
    uuid = supplemental_map.get(path)
    local_supplemental_list = []

    if path.endswith(".html"):
        with open(path, "r", encoding="utf-8") as f:
            try:
                file_data = f.read()

                file_data_tokens = encoding.encode(str(file_data))

                while len(file_data_tokens) > 0:
                    file_dict = {}

                    if len(file_data_tokens) > 512:
                        count += 1
                        chunk = encoding.decode(file_data_tokens[:512])
                        file_dict["uuid"] = f"{uuid}.{count}"
                        file_dict["chunk"] = chunk
                        file_dict["path"] = path
                        file_data_tokens = file_data_tokens[512:]
                    else:
                        count += 1
                        chunk = encoding.decode(file_data_tokens)
                        file_dict["uuid"] = f"{uuid}.{count}"
                        file_dict["chunk"] = chunk
                        file_dict["path"] = path
                        file_data_tokens = []
                    local_supplemental_list.append(file_dict)

            except Exception as e:
                print(f"Error reading file {path}: {e}")

    else:
        with open(path, "r", encoding="utf-8") as f:
            try:
                file_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file {path}: {e}")

            file_data_tokens = encoding.encode(str(file_data))

            while len(file_data_tokens) > 0:
                file_dict = {}

                if len(file_data_tokens) > 512:
                    count += 1
                    chunk = encoding.decode(file_data_tokens[:512])
                    file_dict["uuid"] = f"{uuid}.{count}"
                    file_dict["chunk"] = chunk
                    file_dict["path"] = path
                    file_data_tokens = file_data_tokens[512:]
                else:
                    count += 1
                    chunk = encoding.decode(file_data_tokens)
                    file_dict["uuid"] = f"{uuid}.{count}"
                    file_dict["chunk"] = chunk
                    file_dict["path"] = path
                    file_data_tokens = []
                local_supplemental_list.append(file_dict)

    print(f"Total chunks created: {len(local_supplemental_list)}")
    return local_supplemental_list


supplemental_map = {}
path_list = []


# Creates a list of paths for all supplemental files and a mapping of their uuids, then returns the list of paths
def sup_files() -> list:
    """Get a list of all files in the supplemental directory."""
    with open(sup_data, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {sup_data}: {e}")
            return

        for element in data:
            uuid = element.get("uuid")
            path = "data/supplemental/artifacts/" + element.get("file")
            path_list.append(path)
            supplemental_map[path] = uuid
        return path_list


if __name__ == "__main__":
    supplemental_list = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        files = sup_files()
        results = executor.map(supplemental, files)
    for result in results:
        supplemental_list.extend(result)
    requirements_list = requirements()
    test_list = tests()
    results_list = get_all_results()

    all_lists = supplemental_list + requirements_list + test_list + results_list

    # Write the combined list of all chunks to a new JSON file
    with open(fixed_size_chunks, "w", encoding="utf-8") as f:
        json.dump(all_lists, f, ensure_ascii=False, indent=2)

    print(f"Total chunks created: {len(all_lists)} from all lists")
