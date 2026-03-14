/**
 * Pine Labs redirects the customer here after payment completes (success or failure).
 * URL params from Pine Labs will include order_id and status.
 * We sync the status with our backend, then show the result.
 */
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import client from "../api/client";

const STATUS = {
  loading: "loading",
  success: "success",
  failed: "failed",
  unknown: "unknown",
};

export default function PaymentReturn() {
  const [searchParams] = useSearchParams();
  const [state, setState] = useState(STATUS.loading);
  const [orderId, setOrderId] = useState(null);

  useEffect(() => {
    // Pine Labs passes merchant_order_reference (our order id) and status in query params
    const merchantRef = searchParams.get("merchant_order_reference") || searchParams.get("order_id");
    const rawStatus = (searchParams.get("status") || "").toUpperCase();

    if (!merchantRef) {
      setState(STATUS.unknown);
      return;
    }

    setOrderId(merchantRef);

    // Ask our backend to sync the latest status from Pine Labs
    client.post(`/orders/${merchantRef}/sync-payment`)
      .then((res) => {
        const orderStatus = res.data.status;
        if (orderStatus === "confirmed") setState(STATUS.success);
        else if (orderStatus === "cancelled") setState(STATUS.failed);
        else if (rawStatus.includes("SUCCESS") || rawStatus.includes("CHARGED")) setState(STATUS.success);
        else if (rawStatus.includes("FAIL") || rawStatus.includes("CANCEL")) setState(STATUS.failed);
        else setState(STATUS.unknown);
      })
      .catch(() => {
        // Fall back to raw Pine Labs status param if sync fails
        if (rawStatus.includes("SUCCESS") || rawStatus.includes("CHARGED")) setState(STATUS.success);
        else setState(STATUS.failed);
      });
  }, [searchParams]);

  if (state === STATUS.loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-4 animate-pulse">⏳</div>
          <p className="text-lg">Confirming your payment...</p>
        </div>
      </div>
    );
  }

  if (state === STATUS.success) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="text-center max-w-sm">
          <div className="text-6xl mb-4">✅</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
          <p className="text-gray-500 mb-6">Your order has been confirmed. Thank you for shopping with us.</p>
          <div className="flex flex-col gap-3">
            {orderId && (
              <Link
                to={`/orders/${orderId}`}
                className="bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-indigo-700"
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

  if (state === STATUS.failed) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="text-center max-w-sm">
          <div className="text-6xl mb-4">❌</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Failed</h1>
          <p className="text-gray-500 mb-6">Your payment could not be processed. No charges were made.</p>
          <div className="flex flex-col gap-3">
            <Link
              to="/cart"
              className="bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-indigo-700"
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

  // unknown / no order ref
  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="text-center max-w-sm">
        <div className="text-6xl mb-4">🤔</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Status Unknown</h1>
        <p className="text-gray-500 mb-6">We couldn't determine your payment status. Check your orders page for the latest update.</p>
        <Link to="/orders" className="bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-indigo-700">
          My Orders
        </Link>
      </div>
    </div>
  );
}
