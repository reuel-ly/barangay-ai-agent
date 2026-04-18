import ChatbotWidget from "./ChatbotWidget";

export default function Homepage() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <main className="flex flex-col items-center justify-center text-center flex-grow p-10">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Welcome to Barangay San Manuel
        </h1>
        <p className="text-gray-600 max-w-2xl mb-6">
          Welcome to our official Barangay website! Stay updated with the latest
          news, announcements, and community events. We’re committed to serving
          our residents by making services easier, faster, and more transparent.
        </p>
        <p className="text-gray-600 max-w-2xl">
          Explore our site to learn more about our projects, contact the Barangay
          office, or reach out through our chatbot for quick assistance. Together,
          let’s build a safe, clean, and united community. 💙
        </p>
      </main>

      <ChatbotWidget />
    </div>
  );
}