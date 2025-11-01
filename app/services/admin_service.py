from app.core.settings import get_settings
from app.models.enums import AccessOption
from pathlib import Path
import re


class AdminService:
    def __init__(self):
        settings = get_settings()
        mode_str = settings.ACCESS_CONTROL_MODE.upper()
        try:
            self.mode = AccessOption[mode_str]
        except KeyError:
            self.mode = AccessOption.DISABLE

        self.whitelist = self._load_list("whitelist.txt")
        self.blacklist = self._load_list("blacklist.txt")

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

    def _save_list(self, list_to_save: set, filename: str):
        file_path = Path(__file__).parent.parent.parent / filename
        with open(file_path, "w") as f:
            for item in list_to_save:
                f.write(f"{item}\n")

    def is_allowed(self, user_id: str) -> bool:
        if self.mode == AccessOption.BLACKLIST:
            return user_id not in self.blacklist

        if self.mode == AccessOption.WHITELIST:
            return user_id in self.whitelist

        return True

    def is_valid_number(self, user_id: str) -> bool:
        return bool(
            re.match(
                r"^55(?:[14689][1-9]|2[12478]|3[1234578]|5[1345]|7[134579])(?:9[0-9]{8}|[2-8][0-9]{7})$",
                user_id,
            )
        )

    def _add_to_list(self, user_ids: list[str], target_list: set, filename: str):
        for user_id in user_ids:
            if self.is_valid_number(user_id):
                target_list.add(user_id)
            else:
                raise ValueError(f"Invalid number specified: {user_id}")
        self._save_list(target_list, filename)

    def _remove_from_list(self, user_id: str, target_list: set, filename: str):
        if user_id in target_list:
            target_list.remove(user_id)
            self._save_list(target_list, filename)
        else:
            raise ValueError("Numero não existente na lista")

    def add_to_whitelist(self, user_ids: list[str]):
        self._add_to_list(user_ids, self.whitelist, "whitelist.txt")

    def remove_from_whitelist(self, user_id: str):
        self._remove_from_list(user_id, self.whitelist, "whitelist.txt")

    def add_to_blacklist(self, user_ids: list[str]):
        self._add_to_list(user_ids, self.blacklist, "blacklist.txt")

    def remove_from_blacklist(self, user_id: str):
        self._remove_from_list(user_id, self.blacklist, "blacklist.txt")

    def get_whitelist(self):
        return self.whitelist

    def get_blacklist(self):
        return self.blacklist

    def set_mode(self, mode: AccessOption):
        if isinstance(mode, AccessOption):
            self.mode = mode
        else:
            raise ValueError("Invalid mode specified")
