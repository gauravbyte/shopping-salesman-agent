import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./pages/Home";
import Products from "./pages/Products";
import ProductDetail from "./pages/ProductDetail";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import { OrderList, OrderDetail } from "./pages/Orders";
import Login from "./pages/Login";
import Register from "./pages/Register";
import PaymentReturn from "./pages/PaymentReturn";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          <div className="min-h-screen bg-gray-50">
            <Navbar />
            <main>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/products" element={<Products />} />
                <Route path="/products/:id" element={<ProductDetail />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/cart" element={<ProtectedRoute><Cart /></ProtectedRoute>} />
                <Route path="/checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />
                <Route path="/orders" element={<ProtectedRoute><OrderList /></ProtectedRoute>} />
                <Route path="/orders/:id" element={<ProtectedRoute><OrderDetail /></ProtectedRoute>} />
                <Route path="/payment/return" element={<ProtectedRoute><PaymentReturn /></ProtectedRoute>} />
              </Routes>
            </main>
          </div>
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
