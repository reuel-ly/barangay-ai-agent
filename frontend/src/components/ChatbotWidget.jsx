import { useState, useRef, useEffect } from "react";

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userMessage = { role: "user", content: question };
    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setQuestion("");
    setLoading(true);

    try {
        const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            question: question,        // ← changed
            history: updatedMessages,  // ← changed
        }),
        });

        const data = await response.json();

        const botMessage = {
        role: "assistant",
        content: data.answer,
        };

        setMessages([...updatedMessages, botMessage]);

    } catch (error) {
        console.error("Error:", error);
        setMessages([
        ...updatedMessages,
        { role: "assistant", content: "Something went wrong." }
        ]);
    } finally {
        setLoading(false);
    }
    };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Bubble */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xl shadow-lg flex items-center justify-center transition-all"
        >
          💬
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="w-96 h-[500px] bg-white shadow-2xl rounded-2xl flex flex-col overflow-hidden border">
          
          {/* Header */}
          <div className="bg-blue-600 text-white p-4 flex justify-between items-center">
            <span className="font-semibold">
              Barangay Assistant
            </span>
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>

          {/* Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-gray-50">
            {messages.length === 0 && (
              <p className="text-sm text-gray-400">
                What's your inquiry? ...
              </p>
            )}

            {messages.map((msg, index) => (
              <div
                key={index}
                className={`max-w-[80%] px-4 py-2 rounded-xl text-sm whitespace-pre-line ${
                  msg.role === "user"
                    ? "ml-auto bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                {msg.content}
              </div>
            ))}

            {loading && (
              <p className="text-gray-400 text-sm">Thinking...</p>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form
            onSubmit={handleAsk}
            className="p-3 border-t flex gap-2"
          >
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Type your question..."
              className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />

            <button
              type="submit"
              disabled={loading}
              className="px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  );
}