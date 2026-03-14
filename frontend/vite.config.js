import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    historyApiFallback: true,
    proxy: {
      // Pine Labs posts form data to /payment/return.
      // In dev, forward that POST to backend /payments/return.
      "/payment/return": {
        target: "http://localhost:8001",
        changeOrigin: true,
        rewrite: () => "/payments/return",
      },
      "/api": {
        target: "http://localhost:8001",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
