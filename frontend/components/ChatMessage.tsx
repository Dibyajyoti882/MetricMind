"use client";

import TransparencyPanel from "./TransparencyPanel";
import type { TransparencyStep } from "@/lib/api";

export interface Message {
  role: "user" | "assistant";
  content: string;
  transparency?: TransparencyStep[];
}

export default function ChatMessage({
  message,
}: {
  message: Message;
}) {
  const isUser = message.role === "user";

  return (
    <div className={`chat-message ${isUser ? "user-message" : "assistant-message"}`}>
      {!isUser && (
        <div className="chat-avatar">
          M
        </div>
      )}

      <div className={`message-column ${isUser ? "user-column" : ""}`}>
        <div className="message-label">
          {isUser ? "YOU" : "METRICMIND"}
        </div>

        <div
          className={`message-bubble ${
            isUser ? "user-bubble" : "assistant-bubble"
          }`}
        >
          <div className="message-content">
            {message.content}
          </div>

          {!isUser &&
            message.transparency &&
            message.transparency.length > 0 && (
              <div className="transparency-wrapper">
                <TransparencyPanel
                  steps={message.transparency}
                />
              </div>
            )}
        </div>

        {!isUser &&
          message.transparency &&
          message.transparency.length > 0 && (
            <div className="analysis-status">
              <span className="analysis-check">✓</span>
              Analysis completed
              <span className="analysis-separator">•</span>
              {message.transparency.length}{" "}
              {message.transparency.length === 1
                ? "query step"
                : "query steps"}
            </div>
          )}
      </div>
    </div>
  );
}