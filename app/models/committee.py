from dataclasses import dataclass

@dataclass
class Committee:
    coID: str
    Com: str

    def validate(self):
        if not self.coID:
            raise ValueError("coID is required")
        if not self.Com:
            raise ValueError("Committee name (Com) is required")