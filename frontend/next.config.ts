import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },
  // Required for Telegram WebApp
  async headers() {
    return [
      {
        source: "/tg-app/:path*",
        headers: [
          {
            key: "X-Frame-Options",
            value: "ALLOWALL",
          },
        ],
      },
    ];
  },
  // API Proxy for production - routes /api/* to backend container
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://backend:8000/api/:path*",
      },
      {
        source: "/ws",
        destination: "http://backend:8000/ws",
      },
    ];
  },
};

export default nextConfig;
