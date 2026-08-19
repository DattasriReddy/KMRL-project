"use client";

import React from "react";

export default function DocumentCard({
  document = {},
  onView,
  onDelete,
  onDownload,
}) {
  const {
    id,
    name = "Untitled Document",
    category = "Uncategorized",
    size = "Size unavailable",
    status = "Processed",
    createdAt = "Recently added",
  } = document;

  const getStatusStyles = () => {
    switch (status?.toLowerCase()) {
      case "processed":
      case "completed":
      case "success":
        return {
          container: "bg-green-50 text-green-700 border-green-200",
          dot: "bg-green-500",
        };

      case "processing":
      case "pending":
        return {
          container: "bg-yellow-50 text-yellow-700 border-yellow-200",
          dot: "bg-yellow-500",
        };

      case "failed":
      case "error":
        return {
          container: "bg-red-50 text-red-700 border-red-200",
          dot: "bg-red-500",
        };

      default:
        return {
          container: "bg-gray-50 text-gray-600 border-gray-200",
          dot: "bg-gray-400",
        };
    }
  };

  const statusStyles = getStatusStyles();

  const handleView = () => {
    if (onView) {
      onView(document);
    }
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete(id || document);
    }
  };

  const handleDownload = () => {
    if (onDownload) {
      onDownload(document);
    }
  };

  return (
    <article className="group w-full rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-gray-300 hover:shadow-lg">
      {/* Top Section */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 items-center gap-4">
          {/* PDF Icon */}
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-red-50">
            <svg
              className="h-6 w-6 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 18h10a2 2 0 0 0 2-2V8.5L14.5 4H7a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2Z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M14 4v5h5"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 14h1.5a1.5 1.5 0 0 0 0-3H8v5m5-5v5m0-5h1.5a1.5 1.5 0 0 1 0 3H13"
              />
            </svg>
          </div>

          {/* Document Information */}
          <div className="min-w-0">
            <h3
              className="truncate text-base font-semibold text-gray-900"
              title={name}
            >
              {name}
            </h3>

            <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-gray-500">
              <span>{category}</span>
              <span className="text-gray-300">•</span>
              <span>{size}</span>
            </div>
          </div>
        </div>

        {/* More Button */}
        <button
          type="button"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-gray-400 transition hover:bg-gray-100 hover:text-gray-700"
          aria-label="More options"
        >
          <svg
            className="h-5 w-5"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <circle cx="5" cy="12" r="1.5" />
            <circle cx="12" cy="12" r="1.5" />
            <circle cx="19" cy="12" r="1.5" />
          </svg>
        </button>
      </div>

      {/* Status + Date */}
      <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
        <span
          className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium ${statusStyles.container}`}
        >
          <span
            className={`h-1.5 w-1.5 rounded-full ${statusStyles.dot}`}
          />
          {status}
        </span>

        <span className="text-xs text-gray-400">{createdAt}</span>
      </div>

      {/* Divider */}
      <div className="my-4 border-t border-gray-100" />

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={handleView}
          className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-gray-800 active:scale-[0.98]"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z"
            />
            <circle cx="12" cy="12" r="2.5" />
          </svg>
          View
        </button>

        <button
          type="button"
          onClick={handleDownload}
          className="flex h-10 w-10 items-center justify-center rounded-lg border border-gray-200 text-gray-500 transition hover:bg-gray-50 hover:text-gray-900"
          aria-label="Download document"
          title="Download"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 3v12m0 0 4-4m-4 4-4-4M5 21h14"
            />
          </svg>
        </button>

        <button
          type="button"
          onClick={handleDelete}
          className="flex h-10 w-10 items-center justify-center rounded-lg border border-gray-200 text-gray-400 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
          aria-label="Delete document"
          title="Delete"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 7h16m-10 0v10m4-10v10M9 7V4h6v3m-8 0 1 14h8l1-14"
            />
          </svg>
        </button>
      </div>
    </article>
  );
}