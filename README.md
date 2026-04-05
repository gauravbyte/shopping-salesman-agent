# Shopping Salesman Agent Hackathon Project

An AI-powered ecommerce platform where Claude can autonomously browse products, manage a cart, and place orders via MCP (Model Context Protocol).

---

## Problem

Modern ecommerce platforms are built for human users — point-and-click interfaces that AI agents cannot interact with natively. Integrating an AI shopping assistant typically requires either scraping the UI (fragile) or building a custom API wrapper from scratch (expensive). There was also no standard way for an AI model like Claude to securely authenticate, browse a catalogue, and complete a purchase end-to-end without human intervention at every step.

Additionally, payment integration with Indian gateways (Pine Labs PinePG) requires handling a multi-step hosted checkout flow — token generation, order creation, redirect, callback — which needed to work correctly for both human users and AI-initiated orders.

---

## Solution

A full-stack ecommerce app built with a **service-layer architecture** that serves both a React frontend (for human users) and an MCP server (for AI agents) — sharing the same backend without duplication.

### Architecture

```
Claude Desktop
     │
     ▼
MCP Server (mcp/shopping_agent.py)
     │  14 tools: list_products, add_to_cart, place_order, ...
     ▼
FastAPI Backend (port 8001)
     │
     ├── SQLite Database (products, cart, orders, users)
     └── Pine Labs PinePG (hosted checkout, status sync, refunds)

React + Vite Frontend (port 5173)
     │  for human users
     └── same FastAPI backend via /api proxy
```

### Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy, SQLite |
| Frontend | React, Vite, Tailwind CSS |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Payments | Pine Labs PinePG hosted checkout |
| AI Integration | Anthropic MCP (Model Context Protocol) |
| Deployment | AWS EC2 (backend) + S3 + CloudFront (frontend) |

---

## Key Design Decisions

**1. Service layer as the integration point**
Business logic lives in `backend/app/services/` — not in routers. Both the HTTP API and the MCP tools call the same service functions directly. No HTTP round-trips from agent to API.

**2. MCP server with no-auth interface**
The MCP server handles JWT authentication transparently using env vars. Claude never needs to call a `login` tool — it just uses shopping tools directly. Tokens auto-refresh on expiry.

**3. Pine Labs return URL handled by backend**
Pine Labs POSTs form data to the return URL after payment. Since a React SPA cannot receive POST requests, the backend has a `POST /payments/return` endpoint that receives the callback, updates the order status, and redirects the browser to the frontend with query params.

**4. Python 3.9 compatibility**
AWS EC2 (Amazon Linux 2023) ships with Python 3.9. All type hints use `from __future__ import annotations` and `Optional[str]` from `typing` instead of the `str | None` union syntax introduced in Python 3.10.

---

## MCP Tools

Claude can autonomously perform the full shopping journey:

| Tool | Description |
|------|-------------|
| `list_products` | Browse with filters (category, search, price range) |
| `get_product` | Product details by ID |
| `list_categories` | All available categories |
| `add_to_cart` | Add item (increments if already in cart) |
| `view_cart` | Cart contents with line totals |
| `update_cart_item` | Change quantity |
| `remove_from_cart` | Remove specific item |
| `clear_cart` | Empty the cart |
| `place_order` | Checkout — returns `checkout_url` for payment |
| `list_orders` | Order history |
| `get_order` | Order details with line items |
| `sync_payment_status` | Poll Pine Labs for payment result |
| `buy_product` | One-shot: add + order |
| `search_and_buy` | Search by keyword + buy best match |

---

## Running Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env          # fill in Pine Labs credentials
uvicorn app.main:app --reload --port 8001
python seed.py                # seed sample products

# Frontend
cd frontend
npm install
npm run dev -- --port 5173

# MCP Inspector (test tools interactively)
cd mcp
mcp dev shopping_agent.py --with requests --with typer
```

## Deployment

- **Backend**: AWS EC2 (t2.micro, Amazon Linux 2023), systemd service, nginx reverse proxy
- **Frontend**: AWS S3 static hosting + CloudFront CDN
- **Live URLs**:
  - Frontend: `https://d8vkyoklx592p.cloudfront.net`
  - Backend: `http://54.160.176.125:8000`

## Claude Desktop Setup

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "shopping": {
      "command": "python3",
      "args": ["/path/to/mcp/shopping_agent.py"],
      "env": {
        "SHOP_API_URL": "http://localhost:8001",
        "SHOP_EMAIL": "admin@example.com",
        "SHOP_PASSWORD": "123"
      }
    }
  }
}
```

Restart Claude Desktop. Then ask Claude:
> *"Search for headphones and buy the cheapest one"*
