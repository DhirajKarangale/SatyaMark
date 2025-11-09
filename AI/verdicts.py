from enum import Enum

class Verdict(Enum):
    CORRECT = "Correct"
    INCORRECT = "Incorrect"
    FIRST_TIME = "First-Time"
    AI_GENERATED = "AI-Generated"
    PENDING = "Pending"
    UNVERIFIABLE = "Unverifiable"

    def __str__(self):
        return self.name
