import React from "react";

export default function FooterLinks() {
  const socialLinks = [
    { name: "LinkedIn", url: "https://www.linkedin.com", bgColor: "bg-blue-700" },
    { name: "Facebook", url: "https://www.facebook.com", bgColor: "bg-blue-600" },
    { name: "YouTube", url: "https://www.youtube.com", bgColor: "bg-red-600" },
    { name: "X", url: "https://x.com", bgColor: "bg-sky-500" },
  ];

  return (
    <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50 flex space-x-3 p-2 bg-black/40 rounded-xl backdrop-blur-sm">
      {socialLinks.map((social) => (
        <a
          key={social.name}
          href={social.url}
          target="_blank"
          rel="noopener noreferrer"
          className={`px-3 py-2 rounded text-white font-semibold hover:opacity-80 transition ${social.bgColor}`}
        >
          {social.name}
        </a>
      ))}
    </div>
  );
}