from dataclasses import dataclass

@dataclass
class Estimator:
    estimatorID: int
    estimatorName: str

    def validate(self):
        if not self.estimatorID or self.estimatorID <= 0:
            raise ValueError("estimatorID must be a positive integer")
        if not self.estimatorName:
            raise ValueError("estimatorName is required")