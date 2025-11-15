import axios from "axios";

// Use relative URLs - Next.js will proxy to backend via rewrites
// This works in both dev and production with the proxy configured in next.config.ts
const API_URL = "";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const sendMessage = async (message: string) => {
  const response = await api.post("/api/chat", { message });
  return response.data;
};
