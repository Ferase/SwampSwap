from dataclasses import dataclass
from enum import Enum, auto



class CrocOperation(Enum):
    IDLE = auto()
    SENDING = auto()
    RECEIVING = auto()

class CrocAction(Enum):
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

@dataclass
class CrocState():
    operation: CrocOperation = CrocOperation.IDLE
    action: CrocAction = CrocAction.NONE