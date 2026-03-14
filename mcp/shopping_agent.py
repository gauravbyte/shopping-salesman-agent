"""
Shopping Salesman MCP Server (no-auth interface)

Claude can browse products, manage the cart, and place orders.
Authentication is handled transparently via env vars — no login tool needed.

Claude Desktop config:
  {
    "mcpServers": {
      "shopping": {
        "command": "python3",
        "args": ["/absolute/path/to/mcp/shopping_agent.py"],
        "env": {
          "SHOP_API_URL": "http://localhost:8001",
          "SHOP_EMAIL": "admin@example.com",
          "SHOP_PASSWORD": "admin123"
        }
      }
    }
  }
"""

import os
import requests
from mcp.server.fastmcp import FastMCP

API_URL = os.getenv("SHOP_API_URL", "http://localhost:8001")
SHOP_EMAIL = os.getenv("SHOP_EMAIL", "admin@example.com")
SHOP_PASSWORD = os.getenv("SHOP_PASSWORD", "admin123")

mcp = FastMCP("Shopping Salesman")

# ---------------------------------------------------------------------------
# Internal auth — fully transparent, never exposed as a tool
# ---------------------------------------------------------------------------

_token: str = ""


def _refresh_token() -> str:
    global _token
    resp = requests.post(
        f"{API_URL}/auth/login",
        data={"username": SHOP_EMAIL, "password": SHOP_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    resp.raise_for_status()
    _token = resp.json()["access_token"]
    return _token


def _headers() -> dict:
    global _token
    if not _token:
        _refresh_token()
    return {"Authorization": f"Bearer {_token}"}


def _get(path: str, params: dict = None):
    r = requests.get(f"{API_URL}{path}", headers=_headers(), params=params, timeout=10)
    if r.status_code == 401:
        _refresh_token()
        r = requests.get(f"{API_URL}{path}", headers=_headers(), params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def _post(path: str, json: dict = None):
    r = requests.post(f"{API_URL}{path}", headers=_headers(), json=json, timeout=10)
    if r.status_code == 401:
        _refresh_token()
        r = requests.post(f"{API_URL}{path}", headers=_headers(), json=json, timeout=10)
    r.raise_for_status()
    return r.json()


def _put(path: str, json: dict):
    r = requests.put(f"{API_URL}{path}", headers=_headers(), json=json, timeout=10)
    if r.status_code == 401:
        _refresh_token()
        r = requests.put(f"{API_URL}{path}", headers=_headers(), json=json, timeout=10)
    r.raise_for_status()
    return r.json()


def _delete(path: str):
    r = requests.delete(f"{API_URL}{path}", headers=_headers(), timeout=10)
    if r.status_code == 401:
        _refresh_token()
        r = requests.delete(f"{API_URL}{path}", headers=_headers(), timeout=10)
    r.raise_for_status()


# ---------------------------------------------------------------------------
# Product tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_products(
    category: str = "",
    search: str = "",
    min_price: float = 0,
    max_price: float = 0,
    limit: int = 20,
) -> list:
    """
    Browse products with optional filters.

    Args:
        category:  Category slug (e.g. 'electronics', 'clothing', 'books', 'home').
        search:    Keyword to search in product name/description.
        min_price: Minimum price (0 = no limit).
        max_price: Maximum price (0 = no limit).
        limit:     Max results (default 20).
    """
    params: dict = {"limit": limit}
    if category:
        params["category"] = category
    if search:
        params["search"] = search
    if min_price > 0:
        params["min_price"] = min_price
    if max_price > 0:
        params["max_price"] = max_price
    return _get("/products", params=params)


@mcp.tool()
def get_product(product_id: int) -> dict:
    """Get full details for a product by ID (name, price, stock, description)."""
    return _get(f"/products/{product_id}")


@mcp.tool()
def list_categories() -> list:
    """List all available product categories (id, name, slug)."""
    return _get("/categories")


# ---------------------------------------------------------------------------
# Cart tools
# ---------------------------------------------------------------------------

@mcp.tool()
def view_cart() -> dict:
    """
    View the shopping cart with items, quantities, and totals.
    Returns item_count and grand_total for convenience.
    """
    cart = _get("/cart")
    items = cart.get("items", [])
    for item in items:
        item["line_total"] = round(item["quantity"] * item["product"]["price"], 2)
    cart["item_count"] = sum(i["quantity"] for i in items)
    cart["grand_total"] = round(sum(i["line_total"] for i in items), 2)
    return cart


@mcp.tool()
def add_to_cart(product_id: int, quantity: int = 1) -> dict:
    """
    Add a product to the cart (increments if already present).

    Args:
        product_id: ID of the product to add.
        quantity:   Units to add (default 1).
    """
    return _post("/cart/items", json={"product_id": product_id, "quantity": quantity})


@mcp.tool()
def update_cart_item(item_id: int, quantity: int) -> dict:
    """
    Update the quantity of a cart item.

    Args:
        item_id:  Cart item ID (from view_cart).
        quantity: New quantity.
    """
    return _put(f"/cart/items/{item_id}", json={"quantity": quantity})


@mcp.tool()
def remove_from_cart(item_id: int) -> str:
    """
    Remove an item from the cart.

    Args:
        item_id: Cart item ID (from view_cart).
    """
    _delete(f"/cart/items/{item_id}")
    return f"Item {item_id} removed from cart."


@mcp.tool()
def clear_cart() -> str:
    """Remove all items from the cart."""
    _delete("/cart")
    return "Cart cleared."


# ---------------------------------------------------------------------------
# Order tools
# ---------------------------------------------------------------------------

@mcp.tool()
def place_order() -> dict:
    """
    Place an order for everything in the cart.
    Validates stock, locks prices, clears the cart.
    Returns the order with a checkout_url — share this URL with the user to complete payment.
    """
    order = _post("/orders")
    if order.get("checkout_url"):
        order["_action"] = f"Send user to checkout: {order['checkout_url']}"
    return order


@mcp.tool()
def list_orders() -> list:
    """List all orders, newest first."""
    orders = _get("/orders")
    return sorted(orders, key=lambda o: o["id"], reverse=True)


@mcp.tool()
def get_order(order_id: int) -> dict:
    """
    Get full order details including all line items.

    Args:
        order_id: The order ID.
    """
    return _get(f"/orders/{order_id}")


@mcp.tool()
def sync_payment_status(order_id: int) -> dict:
    """
    Fetch the latest payment status from Pine Labs and update the order.
    Call this after the user returns from the checkout URL.

    Args:
        order_id: The order ID to sync.
    """
    return _post(f"/orders/{order_id}/sync-payment")


# ---------------------------------------------------------------------------
# Agentic one-shot helpers
# ---------------------------------------------------------------------------

@mcp.tool()
def buy_product(product_id: int, quantity: int = 1) -> dict:
    """
    Add a product to cart and immediately place an order (one step).

    Args:
        product_id: Product to purchase.
        quantity:   Units to buy (default 1).
    """
    add_to_cart(product_id, quantity)
    return place_order()


@mcp.tool()
def search_and_buy(search: str, quantity: int = 1, max_price: float = 0) -> dict:
    """
    Search for a product by keyword and buy the best match automatically.

    Args:
        search:    Search term (e.g. 'headphones', 'yoga mat').
        quantity:  How many to buy (default 1).
        max_price: Optional price ceiling (0 = no limit).
    """
    results = list_products(search=search, max_price=max_price, limit=5)
    if not results:
        return {"error": f"No products found matching '{search}'."}
    product = results[0]
    if product["stock"] < quantity:
        return {"error": f"Only {product['stock']} units of '{product['name']}' available."}
    add_to_cart(product["id"], quantity)
    order = place_order()
    order["_bought_product"] = product
    return order


if __name__ == "__main__":
    mcp.run()
