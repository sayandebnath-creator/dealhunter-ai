import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("DealHunter")


DATA_FILE = (
    Path(__file__).parent.parent
    / "backend"
    / "data"
    / "products.json"
)


def load_products():
    with open(DATA_FILE, "r") as file:
        return json.load(file)


@mcp.tool()
def search_products(
    max_price: int = 0,
    min_ram: int = 0,
) -> str:
    """Search laptops by maximum price and minimum RAM."""

    products = load_products()
    results = []

    for product in products:

        if max_price and product["price"] > max_price:
            continue

        if min_ram and product["ram"] < min_ram:
            continue

        results.append(product)

    return json.dumps(results)


@mcp.tool()
def get_product_details(product_id: int) -> str:
    """Get complete details for a product by its ID."""

    products = load_products()

    for product in products:
        if product["id"] == product_id:
            return json.dumps(product)

    return json.dumps({
        "error": "Product not found"
    })


@mcp.tool()
def compare_products(product_ids: list[int]) -> str:
    """Compare multiple products by their IDs."""

    products = load_products()

    selected = [
        product
        for product in products
        if product["id"] in product_ids
    ]

    return json.dumps({
        "products": selected,
        "comparison": {
            "lowest_price": min(
                selected, key=lambda x: x["price"]
            )["name"] if selected else None,

            "best_battery": max(
                selected, key=lambda x: x["battery_hours"]
            )["name"] if selected else None,

            "highest_rating": max(
                selected, key=lambda x: x["rating"]
            )["name"] if selected else None
        }
    })


if __name__ == "__main__":
    mcp.run()