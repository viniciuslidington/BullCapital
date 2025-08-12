import type { ChatRequest } from "@/types/ai";
import axios from "axios";

const AI_BASE_URL = "http://localhost:8001";

const api = axios.create({
  baseURL: AI_BASE_URL,
});

export const AIService = {
  chat: async ({ question, conversation_id }: ChatRequest) => {
    const res = await api.post(`/chat`, {
      question: question,
      conversation_id: conversation_id,
    });
    return res.data;
  },
  getMessages: async (conversation_id: string) => {
    const res = await api.get(`/conversations/${conversation_id}`);
    return res.data;
  },

  health: async (): Promise<{ ok: boolean; service: string }> => {
    const response = await api.get(`/health`);
    return response.data;
  },
};
