import { useState } from "react";
import AnswerCard from "./AnswerCard";

export default function QuestionCard() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim() || loading) return;

    const userMessage = { role: "user", content: question };

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();

      const assistantMessage = {
        role: "assistant",
        content: data.answer,
      };

      setMessages((prev) => [...prev, assistantMessage]);

    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Allow Enter key submission
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleAsk();
    }
  };

  return (
    <div className="bg-white/95 backdrop-blur-md rounded-xl shadow-xl p-6 md:p-8 max-w-3xl w-full mx-4 flex flex-col">
      
      {/* Title */}
      <h1 className="text-3xl md:text-4xl font-semibold text-gray-800 mb-6">
        Pump Selection Assistant
      </h1>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto space-y-2 mb-4 pr-2 max-h-[400px]">
        {messages.map((msg, index) => (
          <AnswerCard
            key={index}
            role={msg.role}
            content={msg.content}
          />
        ))}

        {loading && (
          <AnswerCard
            role="assistant"
            content="Thinking..."
          />
        )}
      </div>

      {/* Input Section */}
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask your HVAC pump question..."
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          onClick={handleAsk}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
        >
          Ask
        </button>
      </div>
    </div>
  );
}