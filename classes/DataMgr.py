import base64
import hashlib
import json
import os
import re
from datetime import datetime
from os import path

from argon2 import Type, low_level

try:
    import keyring
except ImportError:  # pragma: no cover - optional dependency
    keyring = None

try:
    import sqlcipher3
except ImportError:  # pragma: no cover - this project requires SQLCipher
    sqlcipher3 = None

from Helpers import Helpers
from enums.Enums import BTStatus


class DataMgr:
    """Manage app records in a SQLCipher database stored under the data folder."""

    PERSISTED_COLLECTIONS = ("projects", "co_workers", "civil_contracts", "business_trips")
    DB_FILE_NAME = "doc_assistant.db"
    KEYCHAIN_SERVICE = "doc-assistant"
    KEYCHAIN_KEY = "db-password"

    def __init__(self, base_dir=None, password=None):
        self.base_dir = base_dir or os.getcwd()
        self.data_dir = path.join(self.base_dir, "data")
        self.db_path = path.join(self.data_dir, self.DB_FILE_NAME)
        self.legacy_data_path = path.join(self.data_dir, "data.json")
        self.preferences_path = path.join(self.base_dir, "settings", "preferences.json")

        self.labels = self._load_json(path.join(self.base_dir, "settings", "labels.json"), default={})

        self._ensure_directories()
        self.app_password = self._resolve_password(password)
        self.db_key = self._derive_db_key(self.app_password)

        self.preferences = self._load_json(self.preferences_path, default={})
        self.preferences.setdefault("common", {})
        self.preferences.setdefault("output_folders", {})

        self.data = self._load_data()
        self.data.setdefault("common", self.preferences.get("common", {}))
        self.data.setdefault("output_folders", self.preferences.get("output_folders", {}))
        self._sync_preferences_from_data()

    def _ensure_directories(self):
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(path.dirname(self.preferences_path), exist_ok=True)

    def _load_json(self, file_path, default=None):
        if not file_path or not path.exists(file_path):
            return default if default is not None else {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (TypeError, ValueError):
            return default if default is not None else {}

    def _label(self, section, key, default=""):
        return self.labels.get(section, {}).get(key, default)

    def _validate_password(self, password):
        if not isinstance(password, str):
            return False

        password = password.strip()
        if len(password) < 6:
            return False

        return bool(
            re.search(r"[A-Z]", password)
            and re.search(r"[a-z]", password)
            and re.search(r"\d", password)
            and re.search(r"[^A-Za-z0-9]", password)
        )

    def _password_error_message(self):
        return self._label(
            "database",
            "pass_rules",
            "Password must be at least 6 characters long and contain an uppercase letter, lowercase letter, number, and special character.",
        )

    def _prompt_for_password(self, is_new_db):
        required_message = self._label("database", "pass_required", "Database password is required.")
        prompt_message = self._label("database", "pass_prompt", "Enter the database password:")
        prompt_description = self._label("database", "pass_prompt_description", "Enter the database password:")
        invalid_message = self._label("database", "invalid_pass", "Invalid password. Please try again.")

        try:
            import tkinter as tk
            from tkinter import simpledialog
        except Exception:
            raise ValueError(required_message)

        root = tk.Tk()
        root.withdraw()
        if is_new_db:
            while True:
                password = simpledialog.askstring(prompt_message, prompt_description, show='*', parent=root)
                if not password:
                    raise ValueError(required_message)
                if not self._validate_password(password):
                    root.update_idletasks()
                    from tkinter import messagebox
                    messagebox.showerror(self._label("messages", "error_title", "Error"), self._password_error_message())
                    continue
                confirm = simpledialog.askstring(prompt_message, prompt_description, show='*', parent=root)
                if password == confirm:
                    root.destroy()
                    return password
                root.update_idletasks()
                from tkinter import messagebox
                messagebox.showerror(self._label("messages", "error_title", "Error"), invalid_message)
        password = simpledialog.askstring(prompt_message, prompt_description, show='*', parent=root)
        root.destroy()
        if not password:
            raise ValueError(required_message)
        return password

    def _resolve_password(self, password):
        if password and password.strip():
            normalized_password = password.strip()
            if not path.exists(self.db_path) and not self._validate_password(normalized_password):
                raise ValueError(self._password_error_message())
            return normalized_password

        if path.exists(self.db_path):
            return self._prompt_for_password(is_new_db=False)

        return self._prompt_for_password(is_new_db=True)

    def _store_password_in_keychain(self, password):
        if keyring is not None:
            try:
                keyring.set_password(self.KEYCHAIN_SERVICE, self.KEYCHAIN_KEY, password)
                return
            except Exception:
                pass

    def _derive_db_key(self, password):
        salt = hashlib.sha256(self.data_dir.encode("utf-8")).digest()
        derived = low_level.hash_secret_raw(
            password.encode("utf-8"),
            salt,
            time_cost=3,
            memory_cost=65536,
            parallelism=1,
            hash_len=32,
            type=Type.ID,
        )
        return base64.b64encode(derived).decode("utf-8")

    def _connect_db(self):
        if sqlcipher3 is None:
            raise RuntimeError("SQLCipher is required for encrypted database access.")

        connection = sqlcipher3.connect(self.db_path)
        connection.execute("PRAGMA key = '{}';".format(self.db_key.replace("'", "''")))
        connection.execute("PRAGMA cipher_compatibility = 4")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _read_database_data(self):
        if not path.exists(self.db_path):
            return {}

        try:
            with self._connect_db() as connection:
                connection.execute("SELECT count(*) FROM sqlite_master")
                rows = connection.execute("SELECT collection, payload FROM app_data").fetchall()
        except Exception as exc:
            message = self._label("database", "db_file_encryption_error", "Incorrect database password or corrupted database.")
            raise ValueError(message) from exc

        data = {}
        for collection, payload in rows:
            if not isinstance(collection, str):
                continue
            try:
                data[collection] = json.loads(payload)
            except (TypeError, ValueError):
                data[collection] = {}
        return data

    def _write_database_data(self, source_data):
        self._ensure_directories()
        self._store_password_in_keychain(self.app_password)
        with self._connect_db() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS app_data (collection TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )
            for collection in self.PERSISTED_COLLECTIONS:
                payload = json.dumps(source_data.get(collection, {}), ensure_ascii=False)
                connection.execute(
                    "INSERT INTO app_data (collection, payload) VALUES (?, ?) "
                    "ON CONFLICT(collection) DO UPDATE SET payload = excluded.payload",
                    (collection, payload),
                )
            connection.commit()

    def _read_legacy_json_data(self):
        if not path.exists(self.legacy_data_path):
            return {}
        try:
            with open(self.legacy_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (TypeError, ValueError):
            return {}

    def _load_data(self):
        database_data = self._read_database_data()
        if database_data:
            data = {key: value for key, value in database_data.items()}
        else:
            legacy_data = self._read_legacy_json_data()
            if legacy_data:
                data = {key: legacy_data.get(key, {}) for key in self.PERSISTED_COLLECTIONS}
                self._write_database_data(data)
            else:
                data = {key: {} for key in self.PERSISTED_COLLECTIONS}
                self._write_database_data(data)

        for collection in self.PERSISTED_COLLECTIONS:
            data.setdefault(collection, {})

        if 'common' not in data:
            data['common'] = self.preferences.get('common', {})
        if 'output_folders' not in data:
            data['output_folders'] = self.preferences.get('output_folders', {})
        return data

    def _sync_preferences_from_data(self):
        if 'common' in self.data:
            self.preferences['common'] = self.data.get('common', {})
        if 'output_folders' in self.data:
            self.preferences['output_folders'] = self.data.get('output_folders', {})

    def _write_preferences(self):
        self._ensure_directories()
        with open(self.preferences_path, 'w', encoding='utf-8') as f:
            json.dump(self.preferences, f, indent=4, ensure_ascii=False)

    def get_base_dir(self):
        return self.base_dir

    def get_labels(self):
        return self.labels

    def get_project_by_id(self, project_id):
        for p_id in self.data.get('projects', {}):
            if p_id == project_id:
                return self.data['projects'][p_id]
        return None

    def get_coworker_by_id(self, coworker_id):
        for c_id in self.data.get('co_workers', {}):
            if c_id == coworker_id:
                return self.data['co_workers'][c_id]
        return None

    def get_all_projects(self):
        return list(self.data.get('projects', {}).keys())

    def get_output_folders(self):
        return self.preferences.get('output_folders', {})

    def save_new_bussiness_trip(self, new_bussiness_trip):
        if 'business_trips' not in self.data:
            self.data['business_trips'] = {}
        self.data['business_trips'].update(new_bussiness_trip)
        self.save_data()

    def save_new_civil_contract(self, new_civil_contract):
        if 'civil_contracts' not in self.data:
            self.data['civil_contracts'] = {}
        self.data['civil_contracts'].update(new_civil_contract)
        self.save_data()

    def get_all_bussiness_trips_by_status(self, status):
        """Return business trips whose status matches any supplied status."""
        statuses = status if isinstance(status, (list, tuple, set, frozenset)) else [status]
        expected_statuses = set()
        for candidate in statuses:
            status_value = getattr(candidate, 'value', candidate)
            expected_statuses.update({
                candidate,
                status_value,
                str(status_value),
                getattr(candidate, 'name', candidate),
            })

        return {
            k: v for k, v in self.data.get('business_trips', {}).items()
            if v.get('status') in expected_statuses
        }

    def save_data(self):
        self.data['common'] = self.preferences.get('common', self.data.get('common', {}))
        self.data['output_folders'] = self.preferences.get('output_folders', self.data.get('output_folders', {}))
        self._sync_preferences_from_data()
        self._write_preferences()

        persisted_data = {
            key: self.data.get(key, {})
            for key in self.PERSISTED_COLLECTIONS
        }
        self._write_database_data(persisted_data)

    def update_business_trip_statuses(self):
        if 'business_trips' not in self.data:
            self.data['business_trips'] = {}
        all_bt = self.data['business_trips']
        bt_to_update = {}
        for key, value in all_bt.items():
            if value.get('status') in [BTStatus.GENERATED.name, BTStatus.ONGOING.name]:
                value['status'] = BTStatus.GENERATED.name
                bt_to_update[key] = value
        for bt_id, bt in bt_to_update.items():
            current_date = datetime.now().date()
            bt_start_date = Helpers.parse_date(bt.get('start_date')).date()
            bt_end_date = Helpers.parse_date(bt.get('end_date')).date()
            if current_date > bt_start_date and current_date <= bt_end_date:
                bt['status'] = BTStatus.ONGOING.name
            elif current_date > bt_end_date:
                bt['status'] = BTStatus.READY_TO_REPORT.name

        self.save_data()
    # end def
