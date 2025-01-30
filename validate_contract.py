import sys
import yaml

def load_yaml(file_path):
    """Load YAML file into a dictionary."""
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except Exception:
        return None  # File might not exist (first version)

def compare_contracts(old_contract, new_contract):
    """Compare old and new contract versions to detect changes."""
    if not old_contract:
        return "new", ["New contract added"]

    old_columns = {col["name"]: col for col in old_contract["models"][0]["columns"]}
    new_columns = {col["name"]: col for col in new_contract["models"][0]["columns"]}

    breaking_changes = []
    minor_changes = []

    for column in old_columns:
        if column not in new_columns:
            breaking_changes.append(f"Column removed: {column}")
        elif old_columns[column]["data_type"] != new_columns[column]["data_type"]:
            breaking_changes.append(f"Data type changed for column: {column}")

    for column in new_columns:
        if column not in old_columns:
            minor_changes.append(f"New column added: {column}")

    if breaking_changes:
        return "major", breaking_changes
    elif minor_changes:
        return "minor", minor_changes
    else:
        return "patch", []

if __name__ == "__main__":
    old_contract = load_yaml(sys.argv[1])
    new_contract = load_yaml(sys.argv[2])

    change_type, changes = compare_contracts(old_contract, new_contract)

    if changes:
        print(f"Detected {change_type} changes:")
        for change in changes:
            print(f"- {change}")

        if change_type == "major":
            print("This is a breaking change!")
            sys.exit(1)  # Fail workflow if breaking change is detected
