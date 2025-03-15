from dataclasses import dataclass

@dataclass
class Department:
    deID: int
    Dep: str
    coID: int

    def validate(self):
        if not self.deID or self.deID <= 0:
            raise ValueError("deID must be a positive integer")
        if not self.Dep:
            raise ValueError("Department name (Dep) is required")