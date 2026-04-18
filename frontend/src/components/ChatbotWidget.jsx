import { useState, useRef, useEffect } from "react";

const INITIAL_SERVICES = [
  {
    id: "clearance",
    label: "Barangay Clearance",
  },
  {
    id: "indigency",
    label: "Certificate of Indigency",
  },
  {
    id: "blotter",
    label: "Blotter Report",
  },
];

const RULE_BASED_RESPONSES = {
  clearance: `Barangay Clearance

Description:
A Barangay Clearance is an official document issued by the barangay certifying that the requesting person has no pending criminal, civil, or administrative case within the barangay. It is commonly used as proof of good standing in the community.

Who can apply:
Any registered resident of the barangay may apply. Some barangays require at least six months of residency.

Requirements:
• One valid government-issued ID
• Proof of residency
• Accomplished application form
• Recent ID photo (if required)
• Cedula / Community Tax Certificate

Steps:
1. Go to the barangay hall during office hours.
2. Fill out the application form.
3. Submit the form and requirements.
4. Pay the processing fee.
5. Wait for processing and signature.
6. Receive the Barangay Clearance.

Processing time:
Usually 10 to 30 minutes, depending on volume and completeness of documents.

Fees:
Usually around PHP 20 to PHP 100.

Common uses:
• Employment
• Bank account opening
• School requirements
• Loan applications
• Government transactions`,

  indigency: `Certificate of Indigency

Description:
A Certificate of Indigency is an official barangay document stating that a resident belongs to a low-income household and cannot afford certain expenses such as medical, legal, or educational costs.

Who can apply:
Residents who are financially incapable of meeting basic needs. Priority is often given to unemployed individuals, elderly persons, PWDs, solo parents, and those facing medical emergencies.

Requirements:
• One valid government-issued ID
• Proof of residency
• Request letter or referral letter if needed
• Supporting documents showing financial need, if available

Steps:
1. Visit the barangay hall.
2. Inform the staff of the purpose of the request.
3. Fill out the application form.
4. Submit supporting documents or explain your situation.
5. Wait for verification or interview.
6. Receive the signed certificate.

Processing time:
Usually released on the same day.

Fees:
Generally free of charge or with only a very minimal fee.

Common uses:
• Hospital or medical assistance
• DSWD assistance
• PhilHealth indigent application
• PAO legal aid
• Scholarship assistance
• Malasakit Center requirements`,

  blotter: `Blotter Report

Description:
A Blotter Report is an official barangay record of an incident, complaint, or dispute reported in the community. It serves as an official record and may be used later for legal or police-related purposes.

Who can file:
Any resident, visitor, or person who experienced or witnessed an incident within the barangay.

Requirements:
• Valid government-issued ID
• Written or verbal statement of the incident
• Names of involved persons, if known
• Supporting evidence such as photos, screenshots, or medical documents, if available

Steps:
1. Go to the barangay hall.
2. Inform the duty officer or barangay staff that you want to file a blotter report.
3. Explain the incident clearly.
4. The staff records the incident in the blotter logbook.
5. Request a certified copy if needed.
6. The barangay may recommend mediation or refer the matter to the police if necessary.

Processing time:
Usually recorded immediately, around 15 to 45 minutes.

Fees:
Filing is generally free. A certified copy may cost around PHP 20 to PHP 50.

Important note:
A blotter report is not yet a formal criminal case. It is an official record of the reported incident.`,
};

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [availableServices, setAvailableServices] = useState(INITIAL_SERVICES);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, availableServices]);

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
          question: question,
          history: updatedMessages,
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
        { role: "assistant", content: "Something went wrong." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleServiceClick = (service) => {
    setAvailableServices((prev) =>
      prev.filter((item) => item.id !== service.id)
    );

    const userMessage = { role: "user", content: service.label };

    const botMessage = {
      role: "assistant",
      content:
        RULE_BASED_RESPONSES[service.id] ||
        "Sorry, no information is available for this service.",
    };

    setMessages((prev) => [...prev, userMessage, botMessage]);
  };

  const resetServiceButtons = () => {
    setAvailableServices(INITIAL_SERVICES);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-xl shadow-lg flex items-center justify-center transition-all"
        >
          💬
        </button>
      )}

      {isOpen && (
        <div className="w-96 h-[500px] bg-white shadow-2xl rounded-2xl flex flex-col overflow-hidden border">
          <div className="bg-blue-600 text-white p-4 flex justify-between items-center">
            <span className="font-semibold">Barangay Assistant</span>
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-gray-50">
            {messages.length === 0 && (
              <p className="text-sm text-gray-400">What's your inquiry? ...</p>
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

            {loading && <p className="text-gray-400 text-sm">Thinking...</p>}

            <div ref={messagesEndRef} />
          </div>

          <div className="p-3 border-t bg-white">
            <div className="flex flex-wrap gap-2 mb-3">
              {availableServices.map((service) => (
                <button
                  key={service.id}
                  onClick={() => handleServiceClick(service)}
                  disabled={loading}
                  type="button"
                  className="px-3 py-2 rounded-full bg-blue-100 text-blue-700 text-xs font-medium hover:bg-blue-200 transition disabled:opacity-50"
                >
                  {service.label}
                </button>
              ))}

              {availableServices.length === 0 && (
                <button
                  onClick={resetServiceButtons}
                  type="button"
                  className="px-3 py-2 rounded-full bg-gray-200 text-gray-700 text-xs font-medium hover:bg-gray-300 transition"
                >
                  Show options again
                </button>
              )}
            </div>

            <form onSubmit={handleAsk} className="flex gap-2">
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
        </div>
      )}
    </div>
  );
}