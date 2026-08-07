from enum import Enum

class BTStatus(Enum):
    GENERATED = 1
    ONGOING = 2
    READY_TO_REPORT = 3
    PL_REPORTED = 4
    REPORTED = 5

class CCStatus(Enum):
    GENERATED = 1
    ONGOING = 2
    READY_TO_REPORT = 3
    REPORTED = 4