import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { itemCount } = useCart();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <nav className="bg-indigo-600 text-white px-6 py-3 flex items-center gap-6">
      <Link to="/" className="font-bold text-xl tracking-tight">ShopSalesman</Link>
      <Link to="/products" className="hover:text-indigo-200">Products</Link>
      <div className="ml-auto flex items-center gap-4">
        {user ? (
          <>
            <Link to="/cart" className="relative hover:text-indigo-200">
              Cart
              {itemCount > 0 && (
                <span className="ml-1 bg-yellow-400 text-indigo-900 text-xs font-bold rounded-full px-1.5 py-0.5">
                  {itemCount}
                </span>
              )}
            </Link>
            <Link to="/orders" className="hover:text-indigo-200">Orders</Link>
            <span className="text-indigo-300 text-sm">{user.full_name}</span>
            <button onClick={handleLogout} className="bg-indigo-800 px-3 py-1 rounded hover:bg-indigo-700 text-sm">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="hover:text-indigo-200">Login</Link>
            <Link to="/register" className="bg-white text-indigo-600 px-3 py-1 rounded font-medium hover:bg-indigo-50 text-sm">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
