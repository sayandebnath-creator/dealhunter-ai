import json
from pathlib import Path

from langchain_ollama import ChatOllama


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

        Do not invent products or specifications.

        Explain briefly why the recommended products match the user's needs.
        """

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":

    request = input("What are you looking for? \n")

    requirements = extract_requirements(request)

    print("\nRequirements:")
    print(json.dumps(requirements, indent=2))

    products = search_products(requirements)

    print(f"\nFound {len(products)} products.")

    preferences = load_preferences()
    print("\nUser Preferences:")
    print(json.dumps(preferences,indent=2))

    comparison = compare_products(products)

    recommendation = recommend_products(
        request,
        products,
        comparison,
        preferences
    )

    print("\n--- DealHunter Recommendation ---\n")
    print(recommendation)