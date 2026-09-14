"use client";

import { useState } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");

  const handleAsk = () => {
    if (!question.trim()) return;

    setResponse(
      "This is a sample AI response. The backend connection will be added later."
    );
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white flex justify-center px-4 py-10">
      <div className="w-full max-w-3xl">
        <h1 className="text-3xl font-bold text-center mb-2">
          MetricMind
        </h1>

        <p className="text-center text-gray-400 mb-8">
          Ask your business question
        </p>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
          <label className="block text-sm text-gray-400 mb-2">
            Business Question
          </label>

          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Why did European margins drop?"
            className="w-full min-h-32 rounded-xl bg-gray-950 border border-gray-700 p-4 text-white placeholder-gray-500 outline-none"
          />

          <button
            onClick={handleAsk}
            className="mt-4 rounded-xl bg-white px-6 py-3 font-semibold text-black"
          >
            Ask
          </button>
        </div>

        {response && (
          <div className="mt-6 bg-gray-900 border border-gray-800 rounded-2xl p-6">
            <h2 className="text-lg font-semibold mb-3">
              AI Response
            </h2>

            <p className="text-gray-300 leading-7">
              {response}
            </p>
          </div>
        )}
      </div>
    </main>
  );
}