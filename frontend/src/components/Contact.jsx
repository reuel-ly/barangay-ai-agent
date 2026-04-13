import ChatbotWidget from "./ChatbotWidget";

export default function Contact() {
  return (
    <div className="pt-32 px-6 text-center">
      <h1 className="text-3xl font-bold text-gray-800">Contact Us</h1>
      <p className="mt-4 text-gray-600">
        📍 Barangay Office Address <br />
        📞 0912-345-6789 <br />
        📧 barangay@email.com
      </p>
      <ChatbotWidget />
    </div>
  );
}