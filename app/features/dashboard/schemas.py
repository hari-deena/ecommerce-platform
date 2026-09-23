from decimal import Decimal

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_users: int
    total_orders: int
    total_sales: Decimal
    total_products: int
    low_stock_products: int
    pending_orders: int
