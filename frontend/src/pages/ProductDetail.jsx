import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [qty, setQty] = useState(1);
  const [added, setAdded] = useState(false);
  const { user } = useAuth();
  const { addItem } = useCart();
  const navigate = useNavigate();

  useEffect(() => {
    client.get(`/products/${id}`).then((r) => setProduct(r.data)).catch(() => navigate("/products"));
  }, [id, navigate]);

  async function handleAdd() {
    if (!user) { navigate("/login"); return; }
    await addItem(product.id, qty);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  }

  if (!product) return <div className="p-8 text-center text-gray-400">Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <div className="border rounded-lg p-6 bg-white">
        <p className="text-sm text-indigo-500 font-semibold uppercase mb-2">
          {product.category?.name ?? "Uncategorized"}
        </p>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.name}</h1>
        <p className="text-gray-600 mb-6">{product.description}</p>
        <p className="text-2xl font-bold text-indigo-700 mb-2">₹{product.price.toFixed(2)}</p>
        <p className="text-sm text-gray-500 mb-6">
          {product.stock > 0 ? `${product.stock} in stock` : <span className="text-red-500">Out of stock</span>}
        </p>
        <div className="flex items-center gap-4">
          <input
            type="number"
            min={1}
            max={product.stock}
            value={qty}
            onChange={(e) => setQty(Math.max(1, parseInt(e.target.value) || 1))}
            className="border rounded w-20 px-3 py-2 text-center focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <button
            onClick={handleAdd}
            disabled={product.stock === 0}
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed font-semibold"
          >
            {added ? "Added!" : "Add to Cart"}
          </button>
        </div>
      </div>
    </div>
  );
}
