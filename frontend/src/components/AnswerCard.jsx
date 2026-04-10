export default function AnswerCard({ role, content }) {
  const isUser = role === "user";

  return (
    <div className={`w-full flex ${isUser ? "justify-end" : "justify-start"} mt-3`}>
      <div
        className={`
          px-5 py-3 rounded-2xl max-w-xl break-words shadow-sm
          ${isUser
            ? "bg-blue-600 text-white rounded-br-md"
            : "bg-neutral-700 text-neutral-100 rounded-bl-md"}
        `}
      >
        <p className="whitespace-pre-line leading-relaxed text-sm md:text-base">
          {content}
        </p>
      </div>
    </div>
  );
}