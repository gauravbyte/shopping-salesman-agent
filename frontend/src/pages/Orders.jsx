import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import client from "../api/client";

const STATUS_COLOR = {
  pending: "bg-yellow-100 text-yellow-800",
  confirmed: "bg-blue-100 text-blue-800",
  shipped: "bg-purple-100 text-purple-800",
  delivered: "bg-green-100 text-green-800",
  cancelled: "bg-red-100 text-red-800",
};

function OrderDetail() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);

  useEffect(() => {
    client.get(`/orders/${id}`).then((r) => setOrder(r.data)).catch(() => {});
  }, [id]);

  if (!order) return <div className="p-8 text-center text-gray-400">Loading...</div>;

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <Link to="/orders" className="text-indigo-600 hover:underline text-sm">← Back to orders</Link>
      <h1 className="text-3xl font-bold text-gray-900 mt-4 mb-2">Order #{order.id}</h1>
      <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-6 ${STATUS_COLOR[order.status] ?? "bg-gray-100 text-gray-700"}`}>
        {order.status}
      </span>
      <div className="border rounded-lg p-6 bg-white">
        {order.items.map((item) => (
          <div key={item.id} className="flex justify-between text-sm py-2 border-b last:border-0">
            <span>{item.product.name} × {item.quantity}</span>
            <span>₹{(item.unit_price * item.quantity).toFixed(2)}</span>
          </div>
        ))}
        <div className="flex justify-between font-bold text-lg mt-4">
          <span>Total</span>
          <span>₹{order.total_amount.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}

function OrderList() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    client.get("/orders/").then((r) => setOrders(r.data)).catch(() => {});
  }, []);

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Your Orders</h1>
      {orders.length === 0 ? (
        <div className="text-center text-gray-400 py-16">
          No orders yet. <Link to="/products" className="text-indigo-600 hover:underline">Start shopping!</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Link key={order.id} to={`/orders/${order.id}`} className="block border rounded-lg p-5 bg-white hover:shadow-md transition-shadow">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-semibold text-gray-900">Order #{order.id}</p>
                  <p className="text-sm text-gray-500">{order.items.length} item(s)</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-gray-900">₹{order.total_amount.toFixed(2)}</p>
                  <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium mt-1 ${STATUS_COLOR[order.status] ?? "bg-gray-100 text-gray-700"}`}>
                    {order.status}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export { OrderList, OrderDetail };
export default OrderList;
