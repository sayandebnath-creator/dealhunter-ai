import json
import re
import asyncio
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"
PREFERENCES_FILE = Path(__file__).parent.parent / "data" / "preferences.json"


def load_preferences():
    with open(PREFERENCES_FILE, "r") as file:
        return json.load(file)


def load_products():
    with open(DATA_FILE, "r") as file:
        return json.load(file)


llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)


def extract_requirements(user_request: str):

    prompt = f"""
        Extract the shopping requirements from this request.

        User request:
        {user_request}

        Return ONLY JSON in exactly this format:

        {{
            "category": "laptop",
            "max_price": 70000,
            "min_ram": 16,
            "prioritize_battery": false,
            "prioritize_performance": false
        }}

        Rules:
        - Price is Indian Rupees.
        - "70k" means 70000.
        - If the user says "under 70000", max_price must be 70000.
        - Do not increase the user's budget.
        - If RAM is not mentioned, use null.
        - If price is not mentioned, use null.
        - If the user asks for best, great, longest, or long battery life,
        set prioritize_battery to true.

        - If the user asks for best performance, powerful performance,
        programming performance, or similar,
        set prioritize_performance to true.

        - These are preferences, NOT hard filters.
        - Set both to false when the user does not express either preference.
        """

    response = llm.invoke(prompt)

    text = response.content.strip()

    # Handle ```json ... ``` if the model adds markdown
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)


def search_products(requirements):

    products = load_products()
    results = []

    for product in products:

        if (
            requirements["category"]
            and product["category"] != requirements["category"]
        ):
            continue

        if (
            requirements["max_price"]
            and product["price"] > requirements["max_price"]
        ):
            continue

        if (
            requirements["min_ram"]
            and product["ram"] < requirements["min_ram"]
        ):
            continue

        results.append(product)

    return results

def get_product_details(product_id):
    products = load_products()

    for product in products:
        if product["id"] == product_id:
            return product

    return None

def compare_products(products):
    comparison = []

    for product in products:
        comparison.append({
            "name": product["name"],
            "price": product["price"],
            "ram": product["ram"],
            "storage": product["storage"],
            "processor": product["processor"],
            "battery_hours": product["battery_hours"],
            "rating": product["rating"],
            "reviews": product["reviews"],
        })

    return comparison


def recommend_products(user_request, products, comparison, preferences, requirements):

    prompt = f"""
        You are an e-commerce shopping assistant.

        User request:
        {user_request}

        Available products:
        {json.dumps(products, indent=2)}

        Product comparison:
        {json.dumps(comparison, indent=2)}

        User preferences:
        {json.dumps(preferences, indent=2)}

        User preferences extracted from the request:
        {json.dumps(requirements, indent=2)}

        Recommend the most suitable products.

        Consider:
        - price
        - RAM
        - processor
        - storage
        - battery life
        - rating
        - number of reviews
        - user preferences

        Important rules:
        - All prices are in Indian Rupees (INR), not RMB.
        - Treat the user's stated budget as a strict maximum budget.
        - Never increase or reinterpret the user's budget.
        - Do not claim a product is the only one within budget unless the data confirms it.
        - Base every factual statement strictly on the provided product data.
        - Do not invent products or specifications.
        - Do not make performance claims that cannot be determined from the provided data.
        - Do not claim one processor is faster or more powerful unless the provided data explicitly supports it.
        - If multiple products match, explain the key differences.
        - Keep the recommendation concise and practical.
        If prioritize_battery is true:
        - Prefer products with higher verified battery life.

        If prioritize_performance is true:
        - Prefer products with stronger verified performance-related specifications.

        Do not invent battery life or performance information.
        Only use values present in the supplied product data.
        - If the user does not explicitly mention a price or budget,
        max_price MUST be null.
        - Never assume ₹70,000 or any other default budget.

        Explain briefly why the recommended product(s) match the user's needs.
    """

    response = llm.invoke(prompt)

    return response.content


def decide_action(user_request, requirements, products):
    if len(products) == 0:
        return {
            "action": "no_results",
            "reason": "No products match the requirements."
        }

    if len(products) == 1:
        return {
            "action": "recommend",
            "reason": "Only one product matches the requirements."
        }

    return {
        "action": "compare",
        "reason": f"{len(products)} products match the requirements."
    }

def decide_next_action(user_request, products):

    prompt = f"""
        You are the decision component of a shopping agent.

        User request:
        {user_request}

        Products found:
        {json.dumps(products, indent=2)}

        Decide whether the available information is enough.

        Return ONLY JSON:

        {{
            "action": "recommend",
            "product_id": null,
            "reason": "..."
        }}

        Allowed actions:
        - "recommend"
        - "inspect"

        If action is "inspect", product_id MUST be the ID
        of the product that needs more information.

        Use "inspect" only if important information is missing.
        Otherwise use "recommend".
        """

    response = llm.invoke(prompt)

    text = response.content.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)

def normalize_web_products(web_products):
    products = []

    for item in web_products:

        name = item.get("name", "")
        url = item.get("url", "")
        snippet = item.get("snippet", "")

        if not name or not url:
            continue

        products.append({
            "name": name,
            "url": url,
            "description": snippet,
            "source": url.split("/")[2]
        })

    return products

def extract_web_product_data(page):
    import re

    content = page.get("content", "")
    url = page.get("url", "")
    title = page.get("title", "")

    products = []

    # ============================================================
    # AMAZON
    # ============================================================

    if "amazon." in url.lower():

        # Amazon product listings follow this pattern:
        #
        # Product Name
        # 4.1 4.1 out of 5 stars (100)
        # Price, product page ₹61,990
        #
        # Split around "Price, product page" so each section
        # represents one product.

        sections = content.split("Price, product page")

        for section in sections:

            # Product name + rating
            product_match = re.search(
                r"(?P<name>"
                r"(?:Amazon's Choice for .*?\s+)?"
                r"(?:Acer|ASUS|Lenovo|HP|Dell|Apple|MSI|"
                r"Samsung|Microsoft|Primebook|Huawei|LG)"
                r".*?)"
                r"\s+"
                r"(?P<rating>\d(?:\.\d)?)"
                r"\s+"
                r"\d(?:\.\d)?\s+out of 5 stars"
                r"(?:\s+\((?P<reviews>[\d,]+)\))?",
                section,
                re.IGNORECASE
            )

            if not product_match:
                continue

            name = product_match.group("name").strip()

            # Remove Amazon promotional text
            name = re.sub(
                r"^Amazon's Choice for .*?\s+",
                "",
                name,
                flags=re.IGNORECASE
            )

            # Price
            price_match = re.search(
                r"₹\s*([\d,]+)",
                section.split("Price, product page", 1)[-1]
            )

            if not price_match:
                continue

            price = int(
                price_match.group(1).replace(",", "")
            )

            # Ignore clearly invalid prices
            if price < 5000 or price > 500000:
                continue

            # RAM
            ram_match = re.search(
                r"(\d+)\s*GB(?:\s+(?:DDR\d|LPDDR\dX?))?"
                r"\s*(?:RAM|Memory|Unified Memory)",
                name,
                re.IGNORECASE
            )

            ram = (
                int(ram_match.group(1))
                if ram_match
                else None
            )

            # Storage
            storage_match = re.search(
                r"(\d+)\s*(?:GB|TB)"
                r"\s*(?:SSD|Storage|UFS)",
                name,
                re.IGNORECASE
            )

            storage = (
                storage_match.group(0)
                if storage_match
                else None
            )

            # Processor
            processor_match = re.search(
                r"((?:Intel|AMD|Apple|Qualcomm|Snapdragon|"
                r"MediaTek|Ryzen|Core|M\d)[^|,()]*)",
                name,
                re.IGNORECASE
            )

            processor = (
                processor_match.group(1).strip()
                if processor_match
                else None
            )

            # Battery information
            battery_match = re.search(
                r"(\d+(?:\.\d+)?)\s*(?:hrs?|hours?)"
                r"(?:\s+Battery)?",
                name,
                re.IGNORECASE
            )

            battery_hours = (
                float(battery_match.group(1))
                if battery_match
                else None
            )

            # Qualitative battery information
            battery_text = None

            if re.search(
                r"Multi-Day Battery",
                name,
                re.IGNORECASE
            ):
                battery_text = "Multi-Day Battery"

            elif re.search(
                r"Long Battery Life",
                name,
                re.IGNORECASE
            ):
                battery_text = "Long Battery Life"

            products.append({
                "name": name,
                "price": price,
                "currency": "INR",
                "ram": ram,
                "storage": storage,
                "processor": processor,
                "battery_hours": battery_hours,
                "battery_text": battery_text,
                "rating": float(product_match.group("rating")),
                "reviews": (
                    int(
                        product_match.group("reviews")
                        .replace(",", "")
                    )
                    if product_match.group("reviews")
                    else None
                ),
                "url": url,
                "source": title
            })

        return products

    # ============================================================
    # FLIPKART
    # ============================================================

    chunks = re.split(
        r"(?=Add to Compare)",
        content
    )

    for chunk in chunks:

        if not re.search(
            r"(Laptop|Chromebook|MacBook|IdeaPad|ThinkPad|"
            r"Pavilion|Vivobook|VivoBook|Aspire|Inspiron|"
            r"ExpertBook|Galaxy Book|Modern \d+|Victus|TUF)",
            chunk,
            re.IGNORECASE
        ):
            continue

        prices = re.findall(
            r"₹\s*([\d,]+)",
            chunk
        )

        if not prices:
            continue

        price = None

        for value in prices:
            candidate = int(
                value.replace(",", "")
            )

            if 10000 <= candidate <= 200000:
                price = candidate

        if price is None or price > 70000:
            continue

        # RAM
        ram_match = re.search(
            r"(\d+)\s*GB\s*"
            r"(?:DDR\d|LPDDR\dX?)?\s*RAM",
            chunk,
            re.IGNORECASE
        )

        ram = (
            int(ram_match.group(1))
            if ram_match
            else None
        )

        # Storage
        storage_match = re.search(
            r"(\d+)\s*GB\s*(?:SSD|EMMC|eMMC)",
            chunk,
            re.IGNORECASE
        )

        storage = (
            storage_match.group(1)
            if storage_match
            else None
        )

        # Processor
        processor_match = re.search(
            r"((?:Intel|AMD|Apple|MediaTek|Snapdragon)"
            r"[^()]{0,100}"
            r"(?:Processor|Ryzen|Core|Snapdragon|M\d)[^()]*)",
            chunk,
            re.IGNORECASE
        )

        processor = (
            processor_match.group(1).strip()
            if processor_match
            else None
        )

        # Rating
        rating_match = re.search(
            r"(\d(?:\.\d)?)\s+[\d,]+\s+Ratings",
            chunk,
            re.IGNORECASE
        )

        rating = (
            float(rating_match.group(1))
            if rating_match
            else None
        )

        # Reviews
        reviews_match = re.search(
            r"Ratings\s*&\s*([\d,]+)\s+Reviews",
            chunk,
            re.IGNORECASE
        )

        reviews = (
            int(
                reviews_match.group(1)
                .replace(",", "")
            )
            if reviews_match
            else None
        )

        # Product name
        name_match = re.search(
            r"Add to Compare\s+(.+?)"
            r"\s+\d(?:\.\d)?\s+[\d,]+\s+Ratings",
            chunk,
            re.IGNORECASE
        )

        if not name_match:
            continue

        name = name_match.group(1).strip()

        products.append({
            "name": name,
            "price": price,
            "currency": "INR",
            "ram": ram,
            "storage": storage,
            "processor": processor,
            "battery_hours": None,
            "battery_text": None,
            "rating": rating,
            "reviews": reviews,
            "url": url,
            "source": title
        })

    return products

async def get_mcp_tools():
    client = MultiServerMCPClient(
        {
            "dealhunter": {
                "command": "python3",
                "args": [
                    str(
                        Path(__file__).parent.parent.parent
                        / "mcp_server"
                        / "server.py"
                    )
                ],
                "transport": "stdio",
            }
        }
    )

    tools = await client.get_tools()

    return tools


async def run_agent(request):
    tools = await get_mcp_tools()
    # print("\nAvailable MCP tools:")
    # for tool in tools:
    #     print("-", tool.name)

    search_tool = next(
        tool for tool in tools
        if tool.name == "search_products"
    )

    compare_tool = next(
        tool for tool in tools
        if tool.name == "compare_products"
    )

    web_search_tool = next(
        tool for tool in tools
        if tool.name == "search_web_products"
    )

    fetch_page_tool = next(
        tool for tool in tools
        if tool.name == "fetch_product_page"
    )

    # Step 1: Ask LLM to extract requirements
    requirements = extract_requirements(request)

    print("\nRequirements:")
    print(json.dumps(requirements, indent=2))

    # Step 2: Search through MCP
    search_result = await search_tool.ainvoke({
        "max_price": requirements["max_price"] or 0,
        "min_ram": requirements["min_ram"] or 0,
    })

    web_query = f"{request} Amazon India Flipkart"

    web_result = await web_search_tool.ainvoke({
        "query": web_query
    })

    web_products = json.loads(web_result[0]["text"])

    # live_products = normalize_web_products(web_products)
    # Fetch a few relevant web pages
    live_products = []

    for item in web_products:

        url = item.get("url")

        if not url:
            continue

        page_result = await fetch_page_tool.ainvoke({
            "url": url
        })

        page_data = json.loads(page_result[0]["text"])

        if "error" in page_data:
            continue

        live_products.append(page_data)

    # print("\nFetched Live Product Pages:")
    # print(json.dumps(live_products, indent=2))

    structured_live_products = []

    for page in live_products:
        products = extract_web_product_data(page)
        print(f"Parsed {len(products)} products from {page.get('url')}")
        structured_live_products.extend(products)

    print("\nStructured Live Products:")
    print(json.dumps(structured_live_products, indent=2))

    # Keep only products that satisfy the user's requirements
    filtered_live_products = []

    for product in structured_live_products:

        price = product.get("price")
        ram = product.get("ram")

        if requirements["max_price"] is not None:
            if price is None or price > requirements["max_price"]:
                continue

        if requirements["min_ram"] is not None:
            if ram is None or ram < requirements["min_ram"]:
                continue

        filtered_live_products.append(product)

    print("\nFiltered Live Products:")
    print(json.dumps(filtered_live_products, indent=2))

    print("\nNormalized Live Products:")
    print(json.dumps(live_products, indent=2))

    print(f"\nLive web search found {len(web_products)} results.")

    # print("\nLive Products:")
    # print(json.dumps(web_products, indent=2))

    products = filtered_live_products

    print(f"\nMCP Search found {len(products)} products.")

    if not products:
        return "I couldn't find any verified products matching your requirements."

    comparison = products

    print("\nLive Product Comparison ready.")
    preferences = load_preferences()

    recommendation = recommend_products(
        request,
        products,
        comparison,
        preferences,
        requirements
    )

    return recommendation
if __name__ == "__main__":

    request = input("What are you looking for?\n")

    result = asyncio.run(run_agent(request))

    print("\n--- DealHunter Agent ---\n")
    print(result)