export default function SummaryCard({ summary }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">

      <div className="mb-4 flex items-center gap-3">

        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-500/10 text-violet-300">
          ✦
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-white/40">
            AI Generated
          </p>

          <h3 className="text-sm font-semibold text-white">
            Summary
          </h3>
        </div>

      </div>

      <p className="text-sm leading-7 text-white/65">
        {summary}
      </p>

    </div>
  );
}