"use client";

import { FormEvent, useState } from "react";
import { askMetricMind } from "@/lib/api";
import ChatMessage, { Message } from "@/components/ChatMessage";
import DynamicChart from "@/components/DynamicChart";

const SUGGESTED = [
  {
    icon: "📊",
    title: "Margin analysis",
    question: "Why did our European margins drop last quarter?",
  },
  {
    icon: "💰",
    title: "Revenue insights",
    question: "What was total revenue by region in Q3?",
  },
  {
    icon: "📈",
    title: "Performance trends",
    question: "Show me margin percent by quarter for Europe",
  },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send(question: string) {
    if (!question.trim() || loading) return;

    const cleanQuestion = question.trim();

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: cleanQuestion,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await askMetricMind(cleanQuestion);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.answer,
          transparency: response.transparency,
        },
      ]);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Unable to connect to the MetricMind API.";

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: `Something went wrong.\n\n${message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    send(input);
  }

  const showWelcome = messages.length === 0;

  const lastAssistant = [...messages]
    .reverse()
    .find((message) => message.role === "assistant");

  return (
    <main className="metricmind-page">
      {/* HEADER */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">M</div>

          <div>
            <div className="brand-name">MetricMind</div>
            <div className="brand-subtitle">
              Conversational Business Intelligence
            </div>
          </div>
        </div>

        <div className="header-right">
          <div className="status-pill">
            <span className="status-dot" />
            Semantic Layer
            <span className="status-connected">Connected</span>
          </div>
        </div>
      </header>

      {/* MAIN */}
      <div className="main-content">
        {showWelcome && (
          <section className="welcome-section">
            <div className="welcome-icon">
              ✦
            </div>

            <div className="welcome-badge">
              AI-POWERED ANALYTICS
            </div>

            <h1 className="welcome-title">
              Ask your business data.
            </h1>

            <p className="welcome-description">
              Explore governed business metrics with natural language.
              MetricMind connects your questions to trusted data and
              transparent analytical steps.
            </p>
          </section>
        )}

        {/* SUGGESTIONS */}
        {showWelcome && (
          <section className="suggestions-section">
            <div className="section-heading">
              <span>Explore your data</span>
              <span className="heading-line" />
            </div>

            <div className="suggestions">
              {SUGGESTED.map((item) => (
                <button
                  key={item.question}
                  className="suggestion-card"
                  onClick={() => send(item.question)}
                >
                  <div className="suggestion-icon">
                    {item.icon}
                  </div>

                  <div className="suggestion-content">
                    <div className="suggestion-title">
                      {item.title}
                    </div>

                    <div className="suggestion-text">
                      {item.question}
                    </div>
                  </div>

                  <div className="suggestion-arrow">
                    →
                  </div>
                </button>
              ))}
            </div>
          </section>
        )}

        {/* CHAT */}
        <section className="chat-area">
          {messages.map((message, index) => (
            <ChatMessage
              key={`${message.role}-${index}`}
              message={message}
            />
          ))}

          {loading && (
            <div className="loading-message">
              <div className="assistant-mini-icon">
                M
              </div>

              <div className="loading-card">
                <div className="loading-title">
                  MetricMind is thinking
                </div>

                <div className="loading-subtitle">
                  Analyzing your business question...
                </div>

                <div className="loading-dots">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </div>
          )}

          {lastAssistant?.transparency &&
            lastAssistant.transparency.length > 0 && (
              <DynamicChart
                steps={lastAssistant.transparency}
              />
            )}
        </section>
      </div>

      {/* INPUT */}
      <div className="input-wrapper">
        <div className="input-container">
          <form
            className="question-form"
            onSubmit={handleSubmit}
          >
            <div className="input-icon">
              ✦
            </div>

            <input
              className="question-input"
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              placeholder="Ask MetricMind anything about your business data..."
              disabled={loading}
              autoComplete="off"
            />

            <button
              className="ask-button"
              type="submit"
              disabled={loading || !input.trim()}
            >
              {loading ? "..." : "Ask"}
              {!loading && <span>↗</span>}
            </button>
          </form>

          <div className="input-footer">
            <span>
              MetricMind uses governed business metrics
            </span>

            <span>
              Powered by your semantic layer
            </span>
          </div>
        </div>
      </div>
    </main>
  );
}