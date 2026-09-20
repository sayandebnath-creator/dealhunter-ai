import json
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
            "min_ram": 16
        }}

        Rules:
        - Price is Indian Rupees.
        - "70k" means 70000.
        - If the user says "under 70000", max_price must be 70000.
        - Do not increase the user's budget.
        - If RAM is not mentioned, use null.
        - If price is not mentioned, use null.
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


def recommend_products(user_request, products, comparison, preferences):

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

    search_tool = next(
        tool for tool in tools
        if tool.name == "search_products"
    )

    compare_tool = next(
        tool for tool in tools
        if tool.name == "compare_products"
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

    products = json.loads(search_result[0]["text"])

    print(f"\nMCP Search found {len(products)} products.")

    # Step 3: Compare when multiple products exist
    comparison = []

    if len(products) > 1:

        product_ids = [
            product["id"]
            for product in products
        ]

        comparison_result = await compare_tool.ainvoke({
            "product_ids": product_ids
        })

        comparison = json.loads(comparison_result[0]["text"])

        print("\nMCP Comparison completed.")

    # Step 4: Let LLM make the final recommendation
    # prompt = f"""
    #     You are DealHunter, an e-commerce shopping assistant.

    #     User request:
    #     {request}

    #     Matching products:
    #     {json.dumps(products, indent=2)}

    #     Comparison:
    #     {json.dumps(comparison, indent=2)}

    #     Recommend the most suitable laptop.

    #     Consider:
    #     - user's budget
    #     - RAM
    #     - processor performance
    #     - battery life
    #     - rating
    #     - reviews

    #     Never invent specifications.

    #     Explain briefly why your recommendation fits the user's requirements.
    #     """

    # response = llm.invoke(prompt)

    # return response.content
    preferences = load_preferences()

    recommendation = recommend_products(
        request,
        products,
        comparison,
        preferences
    )

    return recommendation
if __name__ == "__main__":

    request = input("What are you looking for?\n")

    result = asyncio.run(run_agent(request))

    print("\n--- DealHunter Agent ---\n")
    print(result)