import { useEffect, useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import client from "../api/client";

const STATUS = {
  loading: "loading",
  success: "success",
  failed: "failed",
  no_ref: "no_ref",
};

export default function PaymentReturn() {
  const [searchParams] = useSearchParams();
  const [state, setState] = useState(STATUS.loading);
  const [orderId, setOrderId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const merchantRef =
      searchParams.get("merchant_order_reference") || searchParams.get("order_id");
    const rawStatus = (searchParams.get("status") || "").toUpperCase();

    // Navigated here directly with no Pine Labs params — redirect to orders
    if (!merchantRef) {
      setState(STATUS.no_ref);
      const timer = setTimeout(() => navigate("/orders", { replace: true }), 3000);
      return () => clearTimeout(timer);
    }

    setOrderId(merchantRef);

    client
      .post(`/orders/${merchantRef}/sync-payment`)
      .then((res) => {
        const s = res.data.status;
        if (s === "confirmed") setState(STATUS.success);
        else if (s === "cancelled") setState(STATUS.failed);
        else if (rawStatus.includes("SUCCESS") || rawStatus.includes("CHARGED"))
          setState(STATUS.success);
        else if (rawStatus.includes("FAIL") || rawStatus.includes("CANCEL"))
          setState(STATUS.failed);
        else setState(STATUS.success); // payment_initiated → treat as pending success
      })
      .catch(() => {
        if (rawStatus.includes("SUCCESS") || rawStatus.includes("CHARGED"))
          setState(STATUS.success);
        else setState(STATUS.failed);
      });
  }, [searchParams, navigate]);

  if (state === STATUS.loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="text-center text-gray-500">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-lg font-medium">Confirming your payment...</p>
          <p className="text-sm mt-1">Please wait, do not close this page.</p>
        </div>
      </div>
    );
  }

  if (state === STATUS.no_ref) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="text-center max-w-sm">
          <div className="text-5xl mb-4">↩️</div>
          <h1 className="text-xl font-bold text-gray-900 mb-2">Redirecting you...</h1>
          <p className="text-gray-500 mb-6">Taking you to your orders page.</p>
          <Link to="/orders" className="text-indigo-600 hover:underline text-sm">
            Go now
          </Link>
        </div>
      </div>
    );
  }

  if (state === STATUS.success) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="text-center max-w-sm">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-5">
            <svg className="w-10 h-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
          <p className="text-gray-500 mb-6">
            Your order has been confirmed. Thank you for shopping with us.
          </p>
          <div className="flex flex-col gap-3">
            {orderId && (
              <Link
                to={`/orders/${orderId}`}
                className="bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-indigo-700 transition"
              >
                View Order
              </Link>
            )}
            <Link to="/products" className="text-indigo-600 hover:underline text-sm">
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // failed
  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="text-center max-w-sm">
        <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-5">
          <svg className="w-10 h-10 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Failed</h1>
        <p className="text-gray-500 mb-6">
          Your payment could not be processed. No charges were made.
        </p>
        <div className="flex flex-col gap-3">
          <Link
            to="/cart"
            className="bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-indigo-700 transition"
          >
            Back to Cart
          </Link>
          {orderId && (
            <Link to={`/orders/${orderId}`} className="text-indigo-600 hover:underline text-sm">
              View Order Details
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
