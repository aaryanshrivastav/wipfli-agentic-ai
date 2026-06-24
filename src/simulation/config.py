from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    """
    Global simulation configuration.
    """

    # Suppliers
    NUM_SUPPLIERS: int = 40

    # Distribution Centers
    NUM_DCS: int = 4

    # Inventory
    MIN_DAYS_OF_COVER: int = 35
    MAX_DAYS_OF_COVER: int = 40

    # Supplier Risk
    MIN_RISK_SCORE: float = 0.05
    MAX_RISK_SCORE: float = 0.95

    # Lead Times
    MIN_LEAD_TIME_DAYS: int = 3
    MAX_LEAD_TIME_DAYS: int = 14

    # Disruptions
    DISRUPTION_RATE: float = 0.04

    # DC Capacity
    DC_CAPACITY_UNITS: int = 500_000


SUPPLIER_CATEGORIES = [
    "FOODS",
    "HOUSEHOLD",
    "HOBBIES"
]

DCS = [
    ("DC_EAST", "East Distribution Center"),
    ("DC_WEST", "West Distribution Center"),
    ("DC_CENTRAL", "Central Distribution Center"),
    ("DC_SOUTH", "South Distribution Center")
]