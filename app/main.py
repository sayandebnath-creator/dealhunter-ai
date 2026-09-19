import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"


def load_products():
    with open(DATA_FILE, "r") as file:
        return json.load(file)


def search_products(
    category=None,
    max_price=None,
    min_ram=None,
):
    products = load_products()

    results = []

    for product in products:
        if category and product["category"] != category:
            continue

        if max_price and product["price"] > max_price:
            continue

        if min_ram and product["ram"] < min_ram:
            continue

        results.append(product)

    return results


if __name__ == "__main__":
    products = search_products(
        category="laptop",
        max_price=70000,
        min_ram=16,
    )

    for product in products:
        print(
            product["name"],
            "₹" + str(product["price"])
        )