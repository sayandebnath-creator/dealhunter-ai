import json
from pathlib import Path
from ddgs import DDGS
import httpx
from bs4 import BeautifulSoup

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

@mcp.tool()
def search_web_products(query: str) -> str:
    """Search the web for products matching a shopping query."""

    results = []

    with DDGS() as ddgs:
        search_results = ddgs.text(
            query,
            max_results=8
        )

        for result in search_results:
            results.append({
                "name": result.get("title"),
                "url": result.get("href"),
                "snippet": result.get("body")
            })

    return json.dumps(results)

@mcp.tool()
def extract_web_products(search_results: str) -> str:
    """Extract structured product information from web search results."""

    return search_results

@mcp.tool()
def fetch_product_page(url: str) -> str:
    """Fetch a publicly accessible product or listing page."""

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = httpx.get(
            url,
            headers=headers,
            timeout=10,
            follow_redirects=True
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "noscript"
        ]):
            tag.decompose()

        text = soup.get_text(
            " ",
            strip=True
        )

        return json.dumps({
            "url": url,
            "title": soup.title.string if soup.title else "",
            "content": text[:12000]
        })

    except Exception as e:

        return json.dumps({
            "url": url,
            "error": str(e)
        })


if __name__ == "__main__":
    mcp.run()