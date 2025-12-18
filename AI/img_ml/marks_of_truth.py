from enum import Enum

class Marks(Enum):
    VERIFYABLE = "verifyable"
    UNVERIFYABLE = "unverifyable"
    INSUFFICIENT = "insufficient"
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PENDING = "pending"
    AI = "ai"
    NONAI = "nonai"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
