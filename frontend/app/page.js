export default function Home() {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950 px-6">

      {/* Background Blur */}
      <div className="absolute -top-40 left-0 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl" />
      <div className="absolute bottom-0 right-0 h-[28rem] w-[28rem] rounded-full bg-indigo-600/20 blur-3xl" />

      {/* Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.03)_1px,transparent_1px)] bg-[size:45px_45px]" />

      <section className="relative z-10 mx-auto w-full max-w-5xl text-center">

        <span className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-300">
          ✨ OCR + Gemini Powered
        </span>

        <h1 className="mt-8 text-5xl font-black leading-tight text-white md:text-7xl">
          Analyze Documents
          <br />
          <span className="bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            in Seconds
          </span>
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-300">
          Upload any PDF and let AI extract text,
          classify documents, and generate concise summaries
          in just a few seconds.
        </p>

        {/* Upload Card */}

        <div className="mx-auto mt-16 max-w-xl rounded-3xl border border-white/10 bg-white/5 p-10 shadow-2xl backdrop-blur-xl transition duration-300 hover:-translate-y-2 hover:border-cyan-400/40">

          <div className="mb-6 text-6xl">📄</div>

          <h2 className="text-2xl font-bold text-white">
            Drag & Drop PDF
          </h2>

          <p className="mt-3 text-slate-400">
            or choose a file from your computer
          </p>

          <button className="mt-8 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 px-8 py-3 font-semibold text-white transition duration-300 hover:scale-105">
            Choose PDF
          </button>

          <p className="mt-6 text-sm text-slate-500">
            Supports PDF up to 20 MB
          </p>

        </div>

        {/* Features */}

        <div className="mt-14 grid gap-6 md:grid-cols-3">

          <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
            <div className="text-3xl">⚡</div>
            <h3 className="mt-3 font-semibold text-white">
              Fast OCR
            </h3>
            <p className="mt-2 text-sm text-slate-400">
              Extract text from scanned PDFs quickly.
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
            <div className="text-3xl">🧠</div>
            <h3 className="mt-3 font-semibold text-white">
              Gemini AI
            </h3>
            <p className="mt-2 text-sm text-slate-400">
              Smart summaries and automatic categorization.
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
            <div className="text-3xl">🔒</div>
            <h3 className="mt-3 font-semibold text-white">
              Secure
            </h3>
            <p className="mt-2 text-sm text-slate-400">
              Your uploaded documents remain protected.
            </p>
          </div>

        </div>

      </section>

    </main>
  );
}