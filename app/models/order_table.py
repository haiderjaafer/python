from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class OrderTable:
    orderNo: Optional[str] = None
    orderYear: Optional[str] = None
    orderDate: Optional[date] = None
    orderType: Optional[str] = None
    coID: Optional[int] = None
    deID: Optional[int] = None
    materialName: Optional[str] = None
    estimatorID: Optional[int] = None
    procedureID: Optional[int] = None
    orderStatus: Optional[str] = None
    notes: Optional[str] = None
    achievedOrderDate: Optional[date] = None
    priceRequestedDestination: Optional[str] = None
    finalPrice: Optional[str] = None
    currencyType: Optional[str] = None
    cunnrentDate: Optional[date] = None
    color: Optional[str] = None
    checkOrderLink: Optional[bool] = None
    userID: Optional[int] = None

    def validate(self):
        if not self.orderNo:
            raise ValueError("Order number is required")
        if not self.orderYear:
            raise ValueError("Order year is required")
        if not self.orderDate:
            raise ValueError("Order date is required")
        if not isinstance(self.orderDate, date):
            raise ValueError("Order date must be a valid date")
        




# app/models/order_details.py


@dataclass
class OrderDetails:
    """Extends OrderTable with joined fields from other tables"""
    # All original OrderTable fields
    orderNo: Optional[str] = None
    orderYear: Optional[str] = None
    orderDate: Optional[date] = None
    orderType: Optional[str] = None
    coID: Optional[int] = None
    deID: Optional[int] = None
    materialName: Optional[str] = None
    estimatorID: Optional[int] = None
    procedureID: Optional[int] = None
    orderStatus: Optional[str] = None
    notes: Optional[str] = None
    achievedOrderDate: Optional[date] = None
    priceRequestedDestination: Optional[str] = None
    finalPrice: Optional[str] = None
    currencyType: Optional[str] = None
    cunnrentDate: Optional[date] = None
    color: Optional[str] = None
    checkOrderLink: Optional[bool] = None
    userID: Optional[int] = None
    
    # New joined fields
    procedureName: Optional[str] = None  # From proceduresTable
    committee: Optional[str] = None      # From ComTB (ISNULL as 'no com')
    department: Optional[str] = None     # From DepTB (ISNULL as 'no dep')
    username: Optional[str] = None       # From users table