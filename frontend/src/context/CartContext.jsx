import { createContext, useContext, useState, useEffect, useCallback } from "react";
import client from "../api/client";
import { useAuth } from "./AuthContext";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState(null);

  const fetchCart = useCallback(async () => {
    if (!user) { setCart(null); return; }
    try {
      const res = await client.get("/cart/");
      setCart(res.data);
    } catch {
      setCart(null);
    }
  }, [user]);

  useEffect(() => { fetchCart(); }, [fetchCart]);

  async function addItem(product_id, quantity = 1) {
    const res = await client.post("/cart/items", { product_id, quantity });
    setCart(res.data);
  }

  async function updateItem(item_id, quantity) {
    const res = await client.put(`/cart/items/${item_id}`, { quantity });
    setCart(res.data);
  }

  async function removeItem(item_id) {
    const res = await client.delete(`/cart/items/${item_id}`);
    setCart(res.data);
  }

  async function clearCart() {
    const res = await client.delete("/cart/");
    setCart(res.data);
  }

  const itemCount = cart?.items.reduce((sum, i) => sum + i.quantity, 0) ?? 0;

  return (
    <CartContext.Provider value={{ cart, addItem, updateItem, removeItem, clearCart, fetchCart, itemCount }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}
