"""Models used to define structured outputs from LLM's."""

from typing import Literal

from pydantic import BaseModel, Field


class ReceiptItem(BaseModel):
    """A single line item on a receipt."""

    item_number: int = Field(description="The Costco item number.")
    name: str = Field(description="The name of the item as shown on the receipt.")
    category: str = Field(description="The category of the item.")
    quantity: int = Field(description="The quantity of the item purchased.")
    original_price: float = Field(description="The original price of the item.")
    discount_amount: float = Field(
        description="The discount amount applied to the item."
    )
    subtotal: float = Field(description="The subtotal for the item.")
    tax_class: Literal["A", "C"] = Field(description="The tax class of the item.")
    tax_amount: float = Field(description="The tax amount for the item.")
    total_amount: float = Field(description="The total amount for the item.")


class Receipt(BaseModel):
    """A receipt containing information about the warehouse and items purchased."""

    warehouse_number: int = Field(description="The Costco warehouse number.")
    warehouse_street_address: str = Field(
        description="The street address of the Costco warehouse. Likely presented in all caps on the receipt; please convert to title case."
    )
    warehouse_city: str = Field(
        description="The city where the Costco warehouse is located. Likely presented in all caps on the receipt; please convert to title case."
    )
    warehouse_state: str = Field(
        description="The state where the Costco warehouse is located."
    )
    warehouse_zip_code: int = Field(description="The zip code of the Costco warehouse.")
    receipt_date: str = Field(
        description="The date on the receipt. Expected format: YYYY-MM-DD."
    )
    item_list: list[ReceiptItem] = Field(description="The list of items purchased.")
