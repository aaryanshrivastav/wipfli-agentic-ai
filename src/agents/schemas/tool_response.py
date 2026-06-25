from dataclasses import dataclass


@dataclass
class InventoryRiskResponse:
    product_key: int
    store_key: int

    inventory_qty: float

    forecast_7d: float
    forecast_14d: float
    forecast_30d: float

    projected_days_to_stockout: float

    risk_level: str


@dataclass
class SupplierRiskResponse:
    supplier_key: int

    supplier_risk_score: float

    reliability_score: float

    lead_time_days: int

    risk_level: str


@dataclass
class ForecastResponse:
    product_key: int
    store_key: int

    forecast_7d: float
    forecast_14d: float
    forecast_30d: float


@dataclass
class RecommendationResponse:
    recommendation_type: str

    urgency_score: float

    recommendation_reason: str

    recommended_order_qty: float


@dataclass
class PurchaseOrderResponse:
    supplier_key: int

    open_po_count: int