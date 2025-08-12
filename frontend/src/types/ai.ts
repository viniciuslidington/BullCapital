export interface ChatMessage {
  content: string;
  role: "user" | "ai";
  timestamp: string;
}

export interface ChatRequest {
  question: string;
  conversation_id: string | undefined;
}

export interface ChatResponse {
  content: string;
  conversation_id: string;
}
