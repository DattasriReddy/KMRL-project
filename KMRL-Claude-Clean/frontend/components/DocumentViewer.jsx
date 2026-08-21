"use client";

export default function DocumentViewer({ document, onClose, onOpenFullPage }) {
  if (!document) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="relative flex max-h-[90vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">

        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4">
          <div className="min-w-0">
            <h2 className="truncate text-lg font-semibold text-gray-900">
              {document.filename || document.name || "Document"}
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              {document.category || "Uncategorized"}
            </p>
          </div>

          <div className="ml-4 flex shrink-0 items-center gap-2">
            {onOpenFullPage && (
              <button
                type="button"
                onClick={onOpenFullPage}
                className="rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium text-gray-600 transition hover:bg-gray-50 hover:text-gray-900"
              >
                Open Full Page
              </button>
            )}

            <button
              type="button"
              onClick={onClose}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-gray-500 transition hover:bg-gray-100 hover:text-gray-900"
              aria-label="Close document viewer"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Document information */}
        <div className="overflow-y-auto p-6">

          <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-3">

            <div className="rounded-xl bg-gray-50 p-4">
              <p className="text-xs uppercase tracking-wide text-gray-400">
                Pages
              </p>
              <p className="mt-1 text-xl font-semibold text-gray-900">
                {document.pages ?? "—"}
              </p>
            </div>

            <div className="rounded-xl bg-gray-50 p-4">
              <p className="text-xs uppercase tracking-wide text-gray-400">
                Confidence
              </p>
              <p className="mt-1 text-xl font-semibold text-gray-900">
                {document.confidence != null
                  ? `${Math.round(document.confidence * 100)}%`
                  : "—"}
              </p>
            </div>

            <div className="col-span-2 rounded-xl bg-gray-50 p-4 sm:col-span-1">
              <p className="text-xs uppercase tracking-wide text-gray-400">
                Category
              </p>
              <p className="mt-1 truncate text-xl font-semibold text-gray-900">
                {document.category || "—"}
              </p>
            </div>

          </div>

          {/* Summary */}
          <div className="mb-6">
            <h3 className="mb-2 text-base font-semibold text-gray-900">
              AI Summary
            </h3>

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
              <p className="text-sm leading-7 text-gray-700">
                {document.summary || "No summary available."}
              </p>
            </div>
          </div>
          {/* Action Items */}
          <div className="mb-6">
            <h3 className="mb-2 text-base font-semibold text-gray-900">
              Action Items
            </h3>

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
              {document.action_items?.length > 0 ? (
                <ul className="space-y-2">
                  {document.action_items.map((item, index) => (
                    <li
                      key={index}
                      className="flex gap-2 text-sm leading-6 text-gray-700"
                    >
                      <span className="text-violet-500">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">
                  No action items identified.
                </p>
              )}
            </div>
          </div>

          {/* Deadline */}
          <div className="mb-6">
            <h3 className="mb-2 text-base font-semibold text-gray-900">
              Deadline
            </h3>

            <div className="rounded-xl border border-gray-200 bg-gray-50 p-5">
              <p className="text-sm font-medium text-gray-700">
                {document.deadline || "No deadline specified"}
              </p>
            </div>
          </div>

          {/* Extracted text */}
          {document.extracted_text && (
            <div>
              <h3 className="mb-2 text-base font-semibold text-gray-900">
                Extracted Text
              </h3>

              <div className="max-h-96 overflow-y-auto rounded-xl border border-gray-200 bg-gray-50 p-5">
                <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-6 text-gray-700">
                  {document.extracted_text}
                </pre>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}