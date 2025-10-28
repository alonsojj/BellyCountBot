import os
from pathlib import Path


class AccessControlService:
    def __init__(self):
        self.mode = os.getenv("ACCESS_CONTROL_MODE", "DISABLED").upper()
        self.whitelist = self._load_list("whitelist.txt")
        self.blacklist = self._load_list("blacklist.txt")

        if self.mode not in ["WHITELIST", "BLACKLIST", "DISABLED"]:
            self.mode = "DISABLED"

    def _load_list(self, filename: str) -> set:
        file_path = Path(__file__).parent.parent.parent / filename
        if not file_path.exists():
            return set()
        try:
            with open(file_path, "r") as f:
                lines = f.read().splitlines()
                return {line.strip() for line in lines if line.strip()}
        except IOError as e:
            print(f"Error loading {filename}: {e}")
            return set()

    def is_allowed(self, user_id: str) -> bool:
        if self.mode == "BLACKLIST":
            if user_id in self.blacklist:
                return False
            return True

        if self.mode == "WHITELIST":
            if user_id in self.whitelist:
                return True
            return False

        return True
