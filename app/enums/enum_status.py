from enum import Enum

class StatusEnum:
    SUCCESSFUL = "successful"
    FAILED = "failed"

class TypeStatusEnum(str, Enum):
    SUCCESSFUL = StatusEnum.SUCCESSFUL
    FAILED = StatusEnum.FAILED

class APITypeStatusEnum(str, Enum):
    SUCCESSFUL = StatusEnum.SUCCESSFUL
    FAILED = StatusEnum.FAILED
    ALL = "all"