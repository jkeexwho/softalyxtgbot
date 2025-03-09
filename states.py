from enum import Enum, auto

class ConversationState(Enum):
    NAME = auto()
    EMAIL = auto()
    CONTACT_PREFERENCE = auto()
    REQUEST = auto()
    PRIVACY_POLICY = auto() 