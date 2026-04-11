import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import FooterLinks from "./components/FooterLinks";
import ChatbotWidget from "./components/ChatbotWidget";


export default function App() {
  return (
    <div className="font-sans">
      <Navbar />
      <HeroSection />
      <FooterLinks />
      <ChatbotWidget />
    </div>
  );
}