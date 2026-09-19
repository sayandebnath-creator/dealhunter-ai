import json
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict


DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"


class AgentState(TypedDict):
    user_request: str
    requirements: dict
    products: list


def load_products():
    with open(DATA_FILE, "r") as file:
        return json.load(file)


llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)


def understand_request(state: AgentState):
    prompt = f"""
Extract the shopping requirements from this request.

Request:
{state["user_request"]}

Return ONLY valid JSON:

{{
  "category": "...",
  "max_price": null,
  "min_ram": null
}}

If something is not mentioned, use null.
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    requirements = json.loads(response.content)

    return {
        "requirements": requirements
    }


def search_products_node(state: AgentState):
    requirements = state["requirements"]
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

    return {
        "products": results
    }


graph = StateGraph(AgentState)

graph.add_node("understand_request", understand_request)
graph.add_node("search_products", search_products_node)

graph.add_edge(START, "understand_request")
graph.add_edge("understand_request", "search_products")
graph.add_edge("search_products", END)

agent = graph.compile()


if __name__ == "__main__":

    request = input("What are you looking for? ")

    result = agent.invoke({
        "user_request": request,
        "requirements": {},
        "products": [],
    })

    print("\nRequirements:")
    print(result["requirements"])

    print("\nProducts:")

    for product in result["products"]:
        print(
            f'{product["name"]} - ₹{product["price"]} '
            f'- {product["ram"]}GB RAM - ⭐ {product["rating"]}'
        )