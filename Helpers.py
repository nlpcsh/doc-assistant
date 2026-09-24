import platform
import shutil
from os import path, makedirs
from datetime import datetime
from tkinter import messagebox

class Helpers:
    @staticmethod
    def build_common_export_payload(document_id, project_id, status, extra_fields=None):
        payload = {
            "project_id": project_id,
            "doc_date_and_ids_identifier": document_id,
            "status": status,
        }
        if extra_fields:
            payload.update(extra_fields)
        return payload

    @staticmethod
    def parse_date(value, dateformat=None):
        if value is None:
            return datetime.min

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return datetime.min

            candidates = []
            if dateformat:
                candidates.append(dateformat)
            candidates.extend(["%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"])
            for candidate in candidates:
                try:
                    return datetime.strptime(value, candidate)
                except ValueError:
                    continue

            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return datetime.min

        return datetime.min

    @staticmethod
    def normalize_date(value, output_format="%d.%m.%Y"):
        parsed = Helpers.parse_date(value)
        if parsed == datetime.min:
            return ""
        return parsed.strftime(output_format)

    @staticmethod
    def get_current_date_str(dateformat="%d.%m.%Y"):
        return datetime.now().strftime(dateformat)

    @staticmethod
    def copy_files_to_folder(file_paths, destination_folder):
        destination_folder = path.abspath(destination_folder)
        makedirs(destination_folder, exist_ok=True)

        copied_files = []
        for file_path in file_paths or []:
            if not file_path:
                continue
            source_path = path.abspath(file_path)
            if not path.exists(source_path) or path.isdir(source_path):
                continue
            target_path = path.join(destination_folder, path.basename(source_path))
            shutil.copy2(source_path, target_path)
            copied_files.append(target_path)
        return copied_files

    @staticmethod
    def get_preferences(preferences_file_path=None):
        if hasattr(Helpers, 'preferences'):
            return Helpers.preferences
        if not preferences_file_path:
            preferences_file_path = path.join(path.dirname(path.abspath(__file__)), "settings", "preferences.json")
        if not path.exists(preferences_file_path):
            return {}
        with open(preferences_file_path, 'r', encoding='utf-8') as f:
            import json
            preferences = json.load(f)
            Helpers.preferences = preferences
            return preferences

    @staticmethod
    def get_font_preferences(preferences_file_path=None):
        if preferences_file_path is None:
            preferences_file_path = path.join(path.dirname(path.abspath(__file__)), "settings", "preferences.json")
        return Helpers.get_preferences(preferences_file_path).get("font", {})

    @staticmethod
    def get_ui_font(preferences_file_path=None, size_key="body_size", bold=False):
        font_settings = Helpers.get_font_preferences(preferences_file_path)
        family = None
        if platform.system() == "Linux":
            family = font_settings.get("Linux_family")
        elif platform.system() == "Windows":
            family = font_settings.get("Windows_family")

        if not family:
            family = font_settings.get("Windows_family") or font_settings.get("Linux_family") or "Arial"

        size = font_settings.get(size_key, 11)
        if bold:
            return (family, int(size), "bold")
        return (family, int(size), "normal")

    @staticmethod
    def get_countries(root, countries_file_path=None):
        try:
            import json
            if countries_file_path is None:
                countries_file_path = path.join(path.dirname(path.abspath(__file__)), "settings", "countries.json")

            with open(countries_file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror(
                "Error",
                "Error occurred while loading countries.json."
            )
            root.destroy()
            return {}
