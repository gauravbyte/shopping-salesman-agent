import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center text-center px-4">
      <h1 className="text-5xl font-extrabold text-indigo-700 mb-4">Shopping Salesman</h1>
      <p className="text-gray-500 text-lg max-w-xl mb-8">
        Your AI-powered shopping assistant. Browse thousands of products, manage your cart, and checkout seamlessly.
      </p>
      <Link
        to="/products"
        className="bg-indigo-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-indigo-700 transition-colors"
      >
        Browse Products
      </Link>
    </div>
  );
}
