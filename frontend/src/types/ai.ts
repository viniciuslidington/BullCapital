export interface ChatMessage {
  content: string;
  sender: "user" | "bot";
  timestamp: string;
}

export interface ChatRequest {
  content: string;
  sender: "user" | "bot";
  conversation_id: string | null;
  user_id: string | null;
}

export interface ChatResponse {
  conversation_id: string;
  user_id: string | null;
  temporario: boolean;
  messages: ChatMessage[];
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  temporario: boolean;
  message_count: number;
  last_message: string;
  created_at: string;
}

export interface ConversationListResponse {
  conversations: Conversation[];
  count: number;
  skip: number;
  limit: number;
  filtered_by_user_id: string;
}
