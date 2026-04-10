export default function Navbar() {
  return (
    <nav className="absolute top-0 left-0 w-full z-20 bg-white/90 backdrop-blur-sm shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-700 rounded-sm flex items-center justify-center text-white font-bold">
            K
          </div>
          <span className="font-semibold text-gray-800 text-lg">Kaizen</span>
        </div>

        {/* Nav Links */}
        <ul className="hidden md:flex items-center gap-8 text-gray-600 font-medium">
          <li className="hover:text-blue-600 cursor-pointer">About Us</li>
          <li className="hover:text-blue-600 cursor-pointer">Solutions</li>
          <li className="hover:text-blue-600 cursor-pointer">Media</li>
          <li className="hover:text-blue-600 cursor-pointer">Careers</li>
        </ul>

        {/* Right Icons */}
        <div className="flex items-center gap-4">
          <button className="text-gray-600 hover:text-blue-600">
            🔔
          </button>
          <div className="w-8 h-8 rounded-full bg-orange-400"></div>
        </div>

      </div>
    </nav>
  );
}