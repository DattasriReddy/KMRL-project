export default function Loading() {
  return (
    <div className="flex flex-col items-center justify-center rounded-3xl border border-white/10 bg-white/[0.03] px-6 py-12 text-center">

      <div className="relative mb-6">

        <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/10 border-t-violet-400" />

        <div className="absolute inset-0 flex items-center justify-center">
          ✦
        </div>

      </div>

      <h3 className="text-lg font-semibold text-white">
        Analyzing document
      </h3>

      <p className="mt-2 max-w-sm text-sm leading-6 text-white/50">
        Extracting information and preparing your AI-powered summary...
      </p>

    </div>
  );
}