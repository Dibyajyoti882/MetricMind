import TransparencyPanel from "./TransparencyPanel";
import type { TransparencyStep } from "@/lib/api";

export interface Message {
  role: "user" | "assistant";
  content: string;
  transparency?: TransparencyStep[];
}

export default function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <div style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", marginBottom: 12 }}>
      <div
        style={{
          maxWidth: "75%",
          background: isUser ? "#4f46e5" : "#f1f1f4",
          color: isUser ? "#fff" : "#111",
          padding: "10px 14px",
          borderRadius: 12,
          whiteSpace: "pre-wrap",
        }}
      >
        {message.content}
        {!isUser && message.transparency && <TransparencyPanel steps={message.transparency} />}
      </div>
    </div>
  );
}