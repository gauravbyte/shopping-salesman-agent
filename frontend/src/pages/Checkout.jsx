import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { useCart } from "../context/CartContext";

export default function Checkout() {
  const { cart, fetchCart } = useCart();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  if (!cart || cart.items.length === 0) {
    navigate("/cart");
    return null;
  }

  async function placeOrder() {
    setLoading(true);
    setError("");
    try {
      const res = await client.post("/orders/");
      await fetchCart();

      const { id, checkout_url } = res.data;

      // If Pine Labs returned a hosted checkout URL, redirect the user there.
      // Otherwise fall back to the order detail page (e.g. credentials not set).
      if (checkout_url) {
        window.location.href = checkout_url;
      } else {
        navigate(`/orders/${id}`);
      }
    } catch (err) {
      setError(err.response?.data?.detail ?? "Failed to place order");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Checkout</h1>
      <div className="border rounded-lg p-6 bg-white mb-6">
        <h2 className="font-semibold text-lg mb-4">Order Summary</h2>
        {cart.items.map((item) => (
          <div key={item.id} className="flex justify-between text-sm py-1.5 border-b last:border-0">
            <span>{item.product.name} × {item.quantity}</span>
            <span>₹{(item.product.price * item.quantity).toFixed(2)}</span>
          </div>
        ))}
        <div className="flex justify-between font-bold text-lg mt-4">
          <span>Total</span>
          <span>₹{cart.total.toFixed(2)}</span>
        </div>
      </div>

      <div className="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-sm text-blue-800">
        <span className="text-lg">🔒</span>
        <p>You'll be redirected to Pine Labs secure payment page to complete your purchase.</p>
      </div>

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
      <button
        onClick={placeOrder}
        disabled={loading}
        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50"
      >
        {loading ? "Preparing payment..." : "Proceed to Payment"}
      </button>
    </div>
  );
}
