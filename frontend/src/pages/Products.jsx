import { useState, useEffect } from "react";
import client from "../api/client";
import ProductCard from "../components/ProductCard";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filters, setFilters] = useState({ search: "", category: "", min_price: "", max_price: "" });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get("/categories").then((r) => setCategories(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (filters.search) params.search = filters.search;
    if (filters.category) params.category = filters.category;
    if (filters.min_price) params.min_price = filters.min_price;
    if (filters.max_price) params.max_price = filters.max_price;
    client.get("/products", { params })
      .then((r) => setProducts(r.data))
      .finally(() => setLoading(false));
  }, [filters]);

  function handleChange(e) {
    setFilters((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Products</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-8">
        <input
          name="search"
          placeholder="Search..."
          value={filters.search}
          onChange={handleChange}
          className="border rounded px-3 py-2 text-sm w-48 focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <select
          name="category"
          value={filters.category}
          onChange={handleChange}
          className="border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.slug}>{c.name}</option>
          ))}
        </select>
        <input
          name="min_price"
          type="number"
          placeholder="Min price"
          value={filters.min_price}
          onChange={handleChange}
          className="border rounded px-3 py-2 text-sm w-28 focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
        <input
          name="max_price"
          type="number"
          placeholder="Max price"
          value={filters.max_price}
          onChange={handleChange}
          className="border rounded px-3 py-2 text-sm w-28 focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-16">Loading products...</div>
      ) : products.length === 0 ? (
        <div className="text-center text-gray-400 py-16">No products found.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  );
}
