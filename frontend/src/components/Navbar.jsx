export default function Navbar() {
  return (
    <nav className="w-full bg-[#0b1a2b] text-white shadow-md">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        
        {/* Logo + Name */}
        <div className="flex items-center gap-3">
          <img
            src="/logo.png" // replace with your actual logo
            alt="logo"
            className="w-8 h-8 object-contain"
          />
          <span className="text-lg font-semibold">MyWebsite</span>
        </div>

        {/* Nav Links */}
        <ul className="flex items-center gap-10 text-sm font-medium">
          <li className="hover:text-gray-300 cursor-pointer">Home</li>
          <li className="hover:text-gray-300 cursor-pointer">Contact</li>
          <li className="hover:text-gray-300 cursor-pointer">About</li>
        </ul>

      </div>
    </nav>
  );
}