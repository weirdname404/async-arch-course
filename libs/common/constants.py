from enum import IntEnum, Enum


class TaskStatus(IntEnum):
    OPEN = 0
    CLOSED = 1


class UserRole(Enum):
    DEV = 'dev'
    ADMIN = 'admin'
    MANAGER = 'manager'
