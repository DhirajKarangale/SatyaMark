from enum import Enum

class Marks(Enum):
    CORRECT = "Correct"
    INCORRECT = "Incorrect"
    AI_GENERATED = "AI-Generated"
    PENDING = "Pending"
    SUBJECTIVE = "subjective"
    INSUFFICIENT = "Insufficient"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
