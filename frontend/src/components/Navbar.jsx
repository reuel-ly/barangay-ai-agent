import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="w-full bg-[#0b1a2b] text-white shadow-md">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img
            src="/logo.png"
            alt="logo"
            className="w-8 h-8 object-contain"
          />
          <span className="text-lg font-semibold">MyWebsite</span>
        </div>

        <ul className="flex items-center gap-10 text-sm font-medium">
          <li><Link to="/" className="hover:text-gray-300">Home</Link></li>
          <li><Link to="/contact" className="hover:text-gray-300">Contact</Link></li>
          <li><Link to="/about" className="hover:text-gray-300">About</Link></li>
        </ul>
      </div>
    </nav>
  );
}