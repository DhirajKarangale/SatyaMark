from enum import Enum

class Marks(Enum):
    CORRECT = "Correct"
    INCORRECT = "Incorrect"
    FIRST_TIME = "First-Time"
    AI_GENERATED = "AI-Generated"
    PENDING = "Pending"
    UNVERIFIABLE = "Unverifiable"

    def __str__(self):
        return self.value  

    def __repr__(self):
        return self.value  
