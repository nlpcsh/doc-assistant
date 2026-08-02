import json
from os import path
from datetime import datetime
from enums.Enums import BTStatus

class Helpers:
    @staticmethod
    def parse_date(value, dateformat="%d/%m/%Y"):
        try:
            return datetime.strptime(value or "", dateformat)
        except ValueError:
            return datetime.min