import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="w-full bg-[#0b1a2b] text-white shadow-md">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img
            src="https://tse2.mm.bing.net/th/id/OIP.EEe7W0uveBBPVePD3h8k6gHaHW?rs=1&pid=ImgDetMain&o=7&rm=3"
            alt="logo"
            className="w-20 h-20 rounded-full object-cover border-2 border-white"
          />
          <span className="text-lg font-semibold">Brgy. San Manuel</span>
        </div>

        <ul className="flex items-center gap-10 text-lg font-medium">
          <li><Link to="/" className="hover:text-gray-300 ">Home</Link></li>
          <li><Link to="/contact" className="hover:text-gray-300">Contact</Link></li>
          <li><Link to="/about" className="hover:text-gray-300 ">About</Link></li>
        </ul>
      </div>
    </nav>
  );
}