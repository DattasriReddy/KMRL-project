export default function Hero() {
  return (
    <section className="mb-14 text-center">

      <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-violet-400/20 bg-violet-400/10 px-4 py-2 text-sm text-violet-300">
        <span>✦</span>
        AI-Powered Document Intelligence
      </div>

      <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
        Turn documents into
        <span className="block text-violet-400">
          intelligence.
        </span>
      </h1>

      <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-white/50 sm:text-lg">
        Upload KMRL documents and let AI extract, classify and
        summarize the information that matters.
      </p>

    </section>
  );
}
