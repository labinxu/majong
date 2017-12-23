from enum import Enum
class ServerStatus(Enum):
    idle = 1
    ready = 2
    playing = 3
    over = 4
