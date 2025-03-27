from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Estimator:
   
    estimatorName: str
    startDate : Optional[date] = None
    endDate : Optional[date] = None
    estimatorStatus : Optional[bool]= None
    coID : Optional[int]= None
    deID : Optional[int]= None

    

    def validate(self):
        if not self.estimatorName or not isinstance(self.estimatorName, str):
            raise ValueError("Valid estimatorName is required")
            
        if self.startDate and self.endDate and self.startDate > self.endDate:
            raise ValueError("startDate cannot be after endDate")
            
        if self.coID is not None and self.coID <= 0:
            raise ValueError("coID must be positive")
            
        if self.deID is not None and self.deID <= 0:
            raise ValueError("deID must be positive")