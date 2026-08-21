import CategoryBadge from "./CategoryBadge";
import SummaryCard from "./SummaryCard";

export default function ResultCard({
  filename = "KMRL_Maintenance_Report.pdf",
  category = "Maintenance",
  summary = "The inspection report identifies electrical maintenance issues that require attention at the station.",
  actionItems = [],
  deadline = "No deadline specified",
  pages = 2,
  confidence = 98,
}) {
  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] shadow-2xl shadow-black/20 backdrop-blur-xl">

      {/* HEADER */}
      <div className="border-b border-white/10 p-6 sm:p-8">

        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">

          <div className="flex items-center gap-4">

            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-violet-500/10 text-2xl">
              📄
            </div>

            <div>
              <p className="text-xs uppercase tracking-wider text-white/40">
                Document
              </p>

              <h2 className="mt-1 max-w-md truncate text-base font-semibold text-white">
                {filename}
              </h2>
            </div>

          </div>

          <CategoryBadge category={category} />

        </div>

      </div>


      {/* CONTENT */}
      <div className="space-y-5 p-6 sm:p-8">

        <SummaryCard summary={summary} />
        {/* ACTION ITEMS */}
        <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
          <p className="text-xs font-medium uppercase tracking-wider text-white/40">
            Action Items
          </p>

          {actionItems.length > 0 ? (
            <ul className="mt-3 space-y-2">
              {actionItems.map((item, index) => (
                <li
                  key={index}
                  className="flex gap-2 text-sm leading-6 text-white/70"
                >
                  <span className="text-violet-400">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-white/40">
              No action items identified.
            </p>
          )}
        </div>

        {/* DEADLINE */}
        <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
          <p className="text-xs font-medium uppercase tracking-wider text-white/40">
            Deadline
          </p>

          <p className="mt-2 text-base font-semibold text-white">
            {deadline || "No deadline specified"}
          </p>
        </div>


        {/* STATS */}
        <div className="grid grid-cols-2 gap-4">

          <div className="rounded-2xl border border-white/10 bg-black/10 p-5 transition hover:bg-white/[0.04]">

            <p className="text-xs font-medium uppercase tracking-wider text-white/40">
              Pages
            </p>

            <p className="mt-2 text-2xl font-semibold text-white">
              {pages}
            </p>

          </div>


          <div className="rounded-2xl border border-white/10 bg-black/10 p-5 transition hover:bg-white/[0.04]">

            <p className="text-xs font-medium uppercase tracking-wider text-white/40">
              Confidence
            </p>

            <p className="mt-2 text-2xl font-semibold text-emerald-400">
              {confidence}%
            </p>

          </div>

        </div>

      </div>

    </div>
  );
}