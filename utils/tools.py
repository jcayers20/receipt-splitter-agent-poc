"""Tools to be used by agents in the project."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.messages import SystemMessage, HumanMessage
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langsmith import traceable
from tavily import TavilyClient

load_dotenv()


def _get_item_information(item_number: int):
    """
    Get detailed information about an item sold at Costco to support categorization.

    This function performs a web search using the Tavily API to find a detailed
    description of the requested item number. In order to use this function, you
    must have a Tavily API key and set it as the TAVILY_API_KEY environment
    variable (recommendation: do this in a .env file).


    Parameters:
        item_number (int): The Costco item number.

    Returns:
        str: A detailed description of the item.
    """

    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY environment variable is not set.")

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    response = client.search(
        query=f"detailed description Costco item #{item_number}",
        include_answer="basic",
        search_depth="basic",
        include_domains=["warehouserunner.com", "costco.com"],
    )

    return response["answer"]


# @traceable(name="Categorize Item", run_type="tool")
@tool
def categorize_item(item_number: int) -> str:
    """
    Categorize an item sold at Costco given its item number.

    This tool assigns an item to a category by first conducting a web search
    for information about the item using the Tavily API, then using an LLM
    to determine the appropriate category based on the search results.

    Args:
        item_number (int): The Costco item number.

    Returns:
        str: The category that the item belongs to.
    """

    # get item information via web search
    description = _get_item_information(item_number)

    # get category via LLM
    path_to_system_prompt = Path("prompts/categorize_item.md")
    system_prompt = path_to_system_prompt.read_text()
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.2)
    response = llm.invoke(
        input=[
            SystemMessage(content=system_prompt),
            HumanMessage(content=description),
        ]
    )

    return response.content


def _calculate_subtotal(
    original_price: float,
    discount_amount: float = 0.0,
) -> float:
    """
    Calculate the subtotal for an item given its original price and discount amount.

    Args:
        original_price (float): The original price of the item.
        discount_amount (float): The discount amount applied to the item.

    Returns:
        float: The subtotal for the item.
    """
    return original_price - discount_amount


def _calculate_tax_amount(
    subtotal: float,
    tax_class: str,
) -> float:
    """
        Calculate the tax amount for an item given its subtotal and tax class.

        Args:
            subtotal (float): The subtotal for the item.
            tax_class (str): The tax class of the item.
    Returns:
        float: The tax amount for the item.
    """
    tax_rates = {
        "A": 0.09,
        "C": 0.01,
    }
    if tax_class not in tax_rates:
        raise ValueError(f"Received invalid tax class: {tax_class}")

    tax_rate = tax_rates.get(tax_class, 0.0)
    return subtotal * tax_rate


def _calculate_total_amount(
    subtotal: float,
    tax_amount: float,
) -> float:
    """
    Calculate the total amount for an item given its subtotal and tax amount.

    Args:
        subtotal (float): The subtotal for the item.
        tax_amount (float): The tax amount for the item.

    Returns:
        float: The total amount for the item.
    """
    return subtotal + tax_amount


# @traceable(name="Calculate Subtotal, Tax, and Total", run_type="tool")
@tool
def perform_calculations(
    original_price: float,
    discount_amount: float,
    tax_class: str,
) -> dict[str, float]:
    """
    Perform calculations required to accurately fill out the ReceiptItem model.

    Args:
        original_price (float): The original price of the item.
        discount_amount (float): The discount amount applied to the item.
        tax_class (str): The tax class of the item.

    Returns:
        dict[str, float]: A dictionary containing the subtotal, tax amount, and total amount for the item.
    """
    subtotal = _calculate_subtotal(original_price, discount_amount)
    tax_amount = _calculate_tax_amount(subtotal, tax_class)
    total_amount = _calculate_total_amount(subtotal, tax_amount)

    return {
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
    }
