import QuestionCard from "./QuestionCard";

export default function HeroSection() {
  return (
    <section
      className="relative h-screen flex items-center justify-center"

    >
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black/50"></div>

      {/* Centered Content */}
      <div className="relative z-10 flex items-center justify-center w-full">
        <QuestionCard />
      </div>
    </section>
  );
}