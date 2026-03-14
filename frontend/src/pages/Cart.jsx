import { Link, useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";

export default function Cart() {
  const { cart, updateItem, removeItem, clearCart } = useCart();
  const navigate = useNavigate();

  if (!cart || cart.items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Your Cart is Empty</h1>
        <Link to="/products" className="text-indigo-600 hover:underline">Browse products</Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Your Cart</h1>
      <div className="space-y-4">
        {cart.items.map((item) => (
          <div key={item.id} className="flex items-center gap-4 border rounded-lg p-4 bg-white">
            <img
              src={item.product.image_url || "https://placehold.co/80x80?text=P"}
              alt={item.product.name}
              className="w-20 h-20 object-cover rounded"
            />
            <div className="flex-1">
              <Link to={`/products/₹{item.product.id}`} className="font-semibold text-gray-900 hover:text-indigo-600">
                {item.product.name}
              </Link>
              <p className="text-gray-500 text-sm">₹{item.product.price.toFixed(2)} each</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => updateItem(item.id, Math.max(1, item.quantity - 1))}
                className="w-7 h-7 rounded border flex items-center justify-center hover:bg-gray-100"
              >−</button>
              <span className="w-8 text-center">{item.quantity}</span>
              <button
                onClick={() => updateItem(item.id, item.quantity + 1)}
                className="w-7 h-7 rounded border flex items-center justify-center hover:bg-gray-100"
              >+</button>
            </div>
            <p className="w-20 text-right font-semibold">₹{(item.product.price * item.quantity).toFixed(2)}</p>
            <button onClick={() => removeItem(item.id)} className="text-red-400 hover:text-red-600 text-sm">Remove</button>
          </div>
        ))}
      </div>
      <div className="mt-8 flex items-center justify-between">
        <button onClick={clearCart} className="text-gray-500 hover:text-red-500 text-sm underline">Clear cart</button>
        <div className="text-right">
          <p className="text-xl font-bold text-gray-900 mb-3">Total: ₹{cart.total.toFixed(2)}</p>
          <button
            onClick={() => navigate("/checkout")}
            className="bg-indigo-600 text-white px-8 py-2.5 rounded-lg font-semibold hover:bg-indigo-700"
          >
            Checkout
          </button>
        </div>
      </div>
    </div>
  );
}
