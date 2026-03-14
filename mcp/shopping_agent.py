"""
Shopping Salesman MCP Server

Exposes tools so Claude can autonomously browse products,
manage the cart, and place orders on the shopping site.

Usage (Claude Desktop config):
  {
    "mcpServers": {
      "shopping": {
        "command": "python3",
        "args": ["/absolute/path/to/mcp/shopping_agent.py"],
        "env": {
          "SHOP_API_URL": "http://localhost:8001",
          "SHOP_EMAIL": "you@example.com",
          "SHOP_PASSWORD": "yourpassword"
        }
      }
    }
  }
"""

import os
import requests
from mcp.server.fastmcp import FastMCP

API_URL = os.getenv("SHOP_API_URL", "http://localhost:8001")
DEFAULT_EMAIL = os.getenv("SHOP_EMAIL", "")
DEFAULT_PASSWORD = os.getenv("SHOP_PASSWORD", "")

mcp = FastMCP("Shopping Salesman")

# ---------------------------------------------------------------------------
# Internal HTTP helpers
# ---------------------------------------------------------------------------

_token: str = ""


def _login(email: str, password: str) -> str:
    """Authenticate and cache the JWT token."""
    global _token
    resp = requests.post(
        f"{API_URL}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    resp.raise_for_status()
    _token = resp.json()["access_token"]
    return _token


def _headers() -> dict:
    """Return auth headers, auto-logging in with env credentials if needed."""
    global _token
    if not _token and DEFAULT_EMAIL and DEFAULT_PASSWORD:
        _login(DEFAULT_EMAIL, DEFAULT_PASSWORD)
    return {"Authorization": f"Bearer {_token}"} if _token else {}


def _get(path: str, params: dict = None) -> dict | list:
    r = requests.get(f"{API_URL}{path}", headers=_headers(), params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def _post(path: str, json: dict = None, data: dict = None) -> dict:
    r = requests.post(f"{API_URL}{path}", headers=_headers(), json=json, data=data, timeout=10)
    r.raise_for_status()
    return r.json()


def _put(path: str, json: dict) -> dict:
    r = requests.put(f"{API_URL}{path}", headers=_headers(), json=json, timeout=10)
    r.raise_for_status()
    return r.json()


def _delete(path: str) -> None:
    r = requests.delete(f"{API_URL}{path}", headers=_headers(), timeout=10)
    r.raise_for_status()


# ---------------------------------------------------------------------------
# Auth tools
# ---------------------------------------------------------------------------

@mcp.tool()
def login(email: str, password: str) -> str:
    """
    Log in to the shopping site with email and password.
    Must be called before any cart or order operations.
    Returns a confirmation message.
    """
    _login(email, password)
    return f"Logged in as {email} successfully."


@mcp.tool()
def get_current_user() -> dict:
    """Return the currently logged-in user's profile."""
    return _get("/auth/me")


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
        category: Category slug to filter by (e.g. 'electronics', 'clothing').
        search:   Keyword to search in product name/description.
        min_price: Minimum price filter (0 = no limit).
        max_price: Maximum price filter (0 = no limit).
        limit:    Max number of results (default 20).

    Returns a list of products with id, name, description, price, stock.
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
    """
    Get full details for a single product by its ID.
    Returns name, description, price, stock, category.
    """
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
    View the current user's shopping cart.
    Returns cart items with product details, quantities, and line totals.
    """
    cart = _get("/cart")
    # Annotate with line totals for convenience
    items = cart.get("items", [])
    for item in items:
        item["line_total"] = round(item["quantity"] * item["product"]["price"], 2)
    cart["item_count"] = sum(i["quantity"] for i in items)
    cart["grand_total"] = round(sum(i["line_total"] for i in items), 2)
    return cart


@mcp.tool()
def add_to_cart(product_id: int, quantity: int = 1) -> dict:
    """
    Add a product to the cart (or increase its quantity if already there).

    Args:
        product_id: The ID of the product to add.
        quantity:   How many units to add (default 1).
    """
    return _post("/cart/items", json={"product_id": product_id, "quantity": quantity})


@mcp.tool()
def update_cart_item(item_id: int, quantity: int) -> dict:
    """
    Update the quantity of a specific cart item.

    Args:
        item_id:  The cart item ID (from view_cart).
        quantity: New quantity (set to 0 to remove).
    """
    return _put(f"/cart/items/{item_id}", json={"quantity": quantity})


@mcp.tool()
def remove_from_cart(item_id: int) -> str:
    """
    Remove a specific item from the cart entirely.

    Args:
        item_id: The cart item ID (from view_cart).
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
    Place an order for everything currently in the cart.
    Validates stock, snapshots prices, clears the cart.
    Returns the created order including a checkout_url for payment.
    If checkout_url is present, the user must visit it to complete payment.
    """
    order = _post("/orders")
    if order.get("checkout_url"):
        order["_note"] = (
            f"Payment required. Direct the user to: {order['checkout_url']}"
        )
    return order


@mcp.tool()
def list_orders() -> list:
    """List all orders placed by the current user, newest first."""
    orders = _get("/orders")
    return sorted(orders, key=lambda o: o["id"], reverse=True)


@mcp.tool()
def get_order(order_id: int) -> dict:
    """
    Get full details for a specific order including all line items.

    Args:
        order_id: The order ID.
    """
    return _get(f"/orders/{order_id}")


@mcp.tool()
def sync_payment_status(order_id: int) -> dict:
    """
    Poll Pine Labs for the latest payment status of an order and update it.
    Use this after the user returns from the payment page.

    Args:
        order_id: The order ID to sync.
    """
    return _post(f"/orders/{order_id}/sync-payment")


# ---------------------------------------------------------------------------
# Convenience / agentic helpers
# ---------------------------------------------------------------------------

@mcp.tool()
def buy_product(product_id: int, quantity: int = 1) -> dict:
    """
    One-shot: add a product to the cart and immediately place an order.
    Equivalent to calling add_to_cart then place_order.

    Args:
        product_id: Product to buy.
        quantity:   How many units (default 1).

    Returns the created order with checkout_url for payment.
    """
    add_to_cart(product_id, quantity)
    return place_order()


@mcp.tool()
def search_and_buy(
    search: str,
    quantity: int = 1,
    max_price: float = 0,
) -> dict:
    """
    Search for a product by keyword and buy the first matching result.

    Args:
        search:    Search term (e.g. 'headphones', 'yoga mat').
        quantity:  How many to buy (default 1).
        max_price: Optional price ceiling.

    Returns the created order, or an error if no products found.
    """
    results = list_products(search=search, max_price=max_price, limit=5)
    if not results:
        return {"error": f"No products found matching '{search}'."}
    product = results[0]
    if product["stock"] < quantity:
        return {"error": f"Insufficient stock for '{product['name']}'. Available: {product['stock']}"}
    add_to_cart(product["id"], quantity)
    order = place_order()
    order["_bought_product"] = product
    return order


if __name__ == "__main__":
    mcp.run()
