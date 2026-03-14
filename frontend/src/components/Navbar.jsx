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
    <nav className="bg-[#1b1730] text-[#f3eeff] border-b border-[#4b3f6f] px-6 py-3 flex items-center gap-6">
      <Link to="/" className="flex items-center gap-3 font-bold tracking-tight">
        <span className="w-8 h-8 rounded border border-[#6b5b98] bg-[#2f2750] text-[#e2c6ff] grid place-items-center text-sm">SS</span>
        <span className="text-lg">Shop Salesman</span>
      </Link>
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
            <Link to="/register" className="bg-indigo-600 text-white px-3 py-1 rounded font-medium hover:bg-indigo-700 text-sm border">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
