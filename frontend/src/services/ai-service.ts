import type { ChatRequest } from "@/types/ai";
import axios from "axios";

const AI_BASE_URL = "http://localhost:8001";

const api = axios.create({
  baseURL: AI_BASE_URL,
});

export const AIService = {
  chat: async (ChatRequest: ChatRequest) => {
    const res = await api.post(`/chat`, ChatRequest);
    return res.data;
  },
  getMessages: async (conversation_id: string) => {
    const res = await api.get(`/conversations/${conversation_id}`);
    return res.data;
  },
  getConversations: async (user_id: string | undefined) => {
    const res = await api.get(`/conversations`, { params: { user_id } });
    return res.data;
  },

  health: async (): Promise<{ status: string; service: string }> => {
    const response = await api.get(`/health`);
    return response.data;
  },
};
