import sys
import yaml
import json

def load_yaml(file_path):
    """Load YAML file into a dictionary."""
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except Exception:
        return None  # File might not exist (first version)

def compare_contracts(old_contract, new_contract):
    
    old_columns = {col["name"]: col for col in old_contract["models"][0]["columns"]}
    new_columns = {col["name"]: col for col in new_contract["models"][0]["columns"]}

    breaking_changes = []
    minor_changes = []
    patch_changes = []
    
    for column in old_columns:
        if column not in new_columns:
            breaking_changes.append(f"Column removed: {column}")
        elif old_columns[column]["data_type"] != new_columns[column]["data_type"]:
            breaking_changes.append(f"Data type changed for column: {column}")
        elif old_columns[column]["description"] != new_columns[column]["description"]:
            patch_changes.append(f"Description changed for column {column}")


    for column in new_columns:
        if column not in old_columns:
            minor_changes.append(f"New column added: {column}")

    if breaking_changes:
        return "major", breaking_changes
    elif minor_changes:
        return "minor", minor_changes
    else:
        return "patch", patch_changes
        
def increment_version(version, change_type):
    """Increment the version based on the change type."""
    if version == 2:
        version = "1.0.0"
    major, minor, patch = map(int, str(version).split("."))

    if change_type == "major":
        return f"{major + 1}.0.0"
    elif change_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif change_type == "patch":
        return f"{major}.{minor}.{patch + 1}"

if __name__ == "__main__":
    old_contract = load_yaml(sys.argv[1])
    new_contract = load_yaml(sys.argv[2])
    if not old_contract:
        response = {
            "status": "new_schema",
            "change_type": "patch",
            "changes": ["Initial schema creation"]
        }
        print(json.dumps(response))
        # return json.dumps(response)
    current_version = old_contract.get("version", "1.0.0")
    
    change_type, changes = compare_contracts(old_contract, new_contract)
    if changes:
        response = {
            "status": "updated",
            "change_type": change_type,
            "changes": changes
        }
    else:
        response = {
            "status": "unchanged",
            "change_type": "patch",
            "changes": []
        }
    print(json.dumps(response))
    # return json.dumps(response)
    # if changes:
    #     print(f"Detected {change_type} changes:")
    #     for change in changes:
    #         print(f"- {change}")

    #     if change_type == "major":
    #         print("This is a breaking change!")
    #         sys.exit(1)  # Fail workflow if breaking change is detected
