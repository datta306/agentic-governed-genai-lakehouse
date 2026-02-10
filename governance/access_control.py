import yaml
from pathlib import Path

# Project root = folder that contains docker-compose.yml
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROLES_PATH = PROJECT_ROOT / "config" / "roles.yaml"


def load_roles():
    if not ROLES_PATH.exists():
        raise FileNotFoundError(
            f"roles.yaml not found at: {ROLES_PATH}\n"
            "Fix: Create config/roles.yaml (exact name) in your project root."
        )
    with open(ROLES_PATH, "r") as f:
        return yaml.safe_load(f)


def is_tool_allowed(user_role: str, tool_name: str) -> bool:
    data = load_roles()
    roles = data.get("roles", {})
    role_info = roles.get(user_role, {})
    allowed = role_info.get("allowed_tools", [])
    return tool_name in allowed


def require_tool_allowed(user_role: str, tool_name: str):
    if not is_tool_allowed(user_role, tool_name):
        raise PermissionError(f"Role '{user_role}' is NOT allowed to use tool '{tool_name}'.")
