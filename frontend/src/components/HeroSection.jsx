import QuestionCard from "./QuestionCard";

export default function HeroSection() {
  return (
    <section
      className="relative h-screen flex items-center justify-center"
      style={{
        backgroundImage: "url('https://tse2.mm.bing.net/th/id/OIP.w1ARHX_DZrYzXW-muUuqGQHaDP?pid=ImgDet&w=208&h=91&c=7&dpr=1.3&o=7&rm=3')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
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