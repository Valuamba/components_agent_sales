from enum import Enum


class AgentType(Enum):
    ClassifyRequest = 1
    ClassifyIntents = 2
    PricingManager = 3
    PurchasingManager = 4
    SalesManager = 5