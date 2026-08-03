import json
import shutil
from os import path, makedirs
from datetime import datetime
from enums.Enums import BTStatus

class Helpers:
    @staticmethod
    def parse_date(value, dateformat="%d/%m/%Y"):
        try:
            return datetime.strptime(value or "", dateformat)
        except ValueError:
            return datetime.min

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