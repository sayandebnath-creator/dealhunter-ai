import json
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import create_agent


DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"


def load_products():
    with open(DATA_FILE, "r") as file:
        return json.load(file)


@tool
def search_products(
    category: str = "",
    max_price: int = 0,
    min_ram: int = 0,
) -> str:
    """
    Search products based on category, maximum price and minimum RAM.
    """

    products = load_products()
    results = []

    for product in products:

        if category and product["category"].lower() != category.lower():
            continue

        if max_price and product["price"] > max_price:
            continue

        if min_ram and product["ram"] < min_ram:
            continue

        results.append(product)

    return json.dumps(results)


llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)


agent = create_agent(
    model=llm,
    tools=[search_products],
    system_prompt="""
You are DealHunter, an e-commerce shopping assistant.

You have access to a product search tool.

Rules:
- Product prices are in Indian Rupees (INR).
- If the user says "under 70000", use max_price=70000.
- If the user says "70k", use max_price=70000.
- If the user asks for 16GB RAM or more, use min_ram=16.
- If the user asks for a laptop, use category="laptop".
- Always use the search_products tool before recommending products.
- Never say that products are unavailable without searching first.
- After receiving search results, recommend suitable products.
"""
)


if __name__ == "__main__":

    request = input("What are you looking for? ")

    result = agent.invoke({
        "messages": [
            (
                "user",
                f"""
You are a shopping assistant.

Help the user find suitable products.

User request:
{request}

Use the search_products tool when you need product information.
After getting the results, recommend suitable products and explain briefly why.
"""
            )
        ]
    })

    print("\n--- Agent Response ---\n")

    print(result["messages"][-1].content)