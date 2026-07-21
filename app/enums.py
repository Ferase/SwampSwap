from dataclasses import dataclass
from enum import Enum, StrEnum, auto



class CrocOperation(Enum):
    """Enum for CrocWorker operation mode."""

    IDLE = auto()
    SENDING = auto()
    RECEIVING = auto()

class CrocAction(Enum):
    """Enum for CrocWorker action state."""

    NONE = ("⚫️ state:idle",)

    WAIT_FOR_PEER = ("🔵 state:wait_peer",)
    SEND_IN_PROGRESS = ("🔵 state:sending",)

    CONNECTING_TO_PEER = ("🔵 state:connect_peer",)
    WAIT_FOR_APPROVAL = ("🔵 state:await_approval",)
    RECEIVE_IN_PROGRESS = ("🔵 state:receiving",)
    
    COMPLETED = ("🟢 state:completed",)
    CANCELLED = ("🔴 state:cancelled",)
    ERROR = ("🔴 generic:error",)

    def __init__(self, text: str):
        self.text = text

class CrocWAV(StrEnum):
    START = "start"
    ERROR = "error"
    CANCEL = "cancel"
    AWAITING_APPROVAL = "awaiting_approval"
    SENDING = "sending"
    RECEIVING = "receiving"
    COMPLETE = "complete"

@dataclass
class CrocState():
    """Dataclass housing the current operation and action states of CrocWorker."""

    operation: CrocOperation = CrocOperation.IDLE
    action: CrocAction = CrocAction.NONE