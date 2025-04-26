import requests
import os
from typing import List, Dict

BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")


def load_items() -> List[Dict]:
    """Get all grocery items"""
    response = requests.get(f"{BASE_URL}/api/fulfillment/items")
    return response.json()

def get_item_by_id(item_id: str) -> Dict:
    """Get a single grocery item by ID"""
    response = requests.get(f"{BASE_URL}/api/fulfillment/items/{item_id}")
    if response.status_code == 404:
        return {"error": f"Item {item_id} not found"}
    return response.json()

def create_order(external_customer_id: str, items) -> Dict:
    """Create a new order"""
    order_data = {
        "external_customer_id": external_customer_id,
        "items": items
    }
    response = requests.post(
        f"{BASE_URL}/api/fulfillment/delivery/orders",
        json=order_data
    )
    if response.status_code == 404:
        return {"error": "One or more items not found"}
    return response.json()

def get_order(order_id: str) -> Dict:
    """Get order by ID"""
    response = requests.get(f"{BASE_URL}/api/fulfillment/delivery/orders/{order_id}")
    if response.status_code == 404:
        return {"error": f"Order {order_id} not found"}
    return response.json()

def get_all_orders() -> List[Dict]:
    """Get all orders"""
    response = requests.get(f"{BASE_URL}/api/fulfillment/delivery/orders")
    return response.json()

# # Example usage:
# if __name__ == "__main__":
#     # Get all items
#     print("Getting all items:")
#     items = load_items()
#     print(items)
    
#     # Get a specific item
#     if items:
#         item_id = items[0]["upc"]
#         print(f"\nGetting item {item_id}:")
#         item = get_item_by_id(item_id)
#         print(item)
    
#     # Create an order
#     print("\nCreating an order:")
#     order = create_order(
#         external_customer_id="customer123",
#         items=[
#             {"item_id": "041190000019", "quantity": 2},
#             {"item_id": "036632015465", "quantity": 1}
#         ]
#     )
#     print(order)
    
#     if "order_id" in order:
#         # Get the order by ID
#         print(f"\nGetting order {order['order_id']}:")
#         retrieved_order = get_order(order["order_id"])
#         print(retrieved_order)
    
#     # Get all orders
#     print("\nGetting all orders:")
#     all_orders = get_all_orders()
#     print(all_orders)
