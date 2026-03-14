import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function ProductCard({ product }) {
  const { user } = useAuth();
  const { addItem } = useCart();

  async function handleAdd() {
    if (!user) { window.location.href = "/login"; return; }
    await addItem(product.id, 1);
  }

  return (
    <div className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow bg-white">
      <div className="p-4">
        <div className="flex items-center justify-between gap-2 mb-2">
          <p className="text-xs text-indigo-500 uppercase font-semibold">
            {product.category?.name ?? "Uncategorized"}
          </p>
          <span className="text-xs text-gray-500">Stock: {product.stock}</span>
        </div>
        <Link to={`/products/${product.id}`}>
          <h3 className="font-semibold text-gray-900 hover:text-indigo-600 line-clamp-2">{product.name}</h3>
        </Link>
        <div className="mt-3 flex items-center justify-between">
          <span className="text-lg font-bold text-gray-900">₹{product.price.toFixed(2)}</span>
          <button
            onClick={handleAdd}
            disabled={product.stock === 0}
            className="bg-indigo-600 text-white text-sm px-3 py-1.5 rounded hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {product.stock === 0 ? "Out of stock" : "Add to cart"}
          </button>
        </div>
      </div>
    </div>
  );
}
