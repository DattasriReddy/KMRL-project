"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getDocument, getDownloadUrl } from "@/services/api";
import Loader from "@/components/Loader";

export default function DocumentPage() {
  const { id } = useParams();
  const router = useRouter();

  const [document, setDocument] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;

    const fetchDocument = async () => {
      try {
        const data = await getDocument(id);

        if (data?.error) {
          throw new Error(data.error);
        }

        setDocument(data);
      } catch (err) {
        console.error(err);
        setError("Unable to load this document.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocument();
  }, [id]);

  if (isLoading) {
    return (
      <main className="min-h-screen bg-[#08090d] p-8 text-white">
        <div className="mx-auto max-w-4xl">
          <Loader label="Loading document..." />
        </div>
      </main>
    );
  }

  if (error || !document) {
    return (
      <main className="min-h-screen bg-[#08090d] p-8 text-white">
        <div className="mx-auto max-w-4xl">
          <button
            onClick={() => router.back()}
            className="mb-6 text-sm text-violet-400 hover:text-violet-300"
          >
            ← Back
          </button>

          <div className="rounded-2xl border border-red-400/20 bg-red-400/10 p-6 text-red-300">
            {error || "Document not found."}
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#08090d] px-5 py-10 text-white sm:px-8">
      <div className="mx-auto max-w-5xl">

        <div className="mb-8 flex items-center justify-between gap-4">
          <button
            onClick={() => router.back()}
            className="text-sm text-white/50 transition hover:text-white"
          >
            ← Back to Dashboard
          </button>

          <a
            href={getDownloadUrl(document.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white/70 transition hover:bg-white/10 hover:text-white"
          >
            Download
          </a>
        </div>

        <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] shadow-2xl">

          {/* HEADER */}
          <div className="border-b border-white/10 p-6 sm:p-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

              <div>
                <p className="text-xs uppercase tracking-wider text-white/40">
                  Document
                </p>

                <h1 className="mt-2 text-2xl font-bold">
                  {document.filename}
                </h1>
              </div>

              <div className="rounded-full bg-violet-500/10 px-4 py-2 text-sm text-violet-300">
                {document.category}
              </div>

            </div>
          </div>

          {/* SUMMARY */}
          <div className="space-y-6 p-6 sm:p-8">

            <section>
              <h2 className="mb-3 text-sm font-medium uppercase tracking-wider text-white/40">
                AI Summary
              </h2>

              <div className="rounded-2xl border border-white/10 bg-black/10 p-5 text-white/70 leading-7">
                {document.summary}
              </div>
            </section>

            {/* ACTION ITEMS */}
            <section>
              <h2 className="mb-3 text-sm font-medium uppercase tracking-wider text-white/40">
                Action Items
              </h2>

              <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
                {document.action_items?.length > 0 ? (
                  <ul className="space-y-2">
                    {document.action_items.map((item, index) => (
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
                  <p className="text-sm text-white/40">
                    No action items identified.
                  </p>
                )}
              </div>
            </section>

            {/* DEADLINE */}
            <section>
              <h2 className="mb-3 text-sm font-medium uppercase tracking-wider text-white/40">
                Deadline
              </h2>

              <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
                <p className="text-sm font-medium text-white/70">
                  {document.deadline || "No deadline specified"}
                </p>
              </div>
            </section>

            {/* STATS */}
            <div className="grid grid-cols-2 gap-4">

              <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
                <p className="text-xs uppercase tracking-wider text-white/40">
                  Pages
                </p>
                <p className="mt-2 text-2xl font-semibold">
                  {document.pages}
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
                <p className="text-xs uppercase tracking-wider text-white/40">
                  Confidence
                </p>
                <p className="mt-2 text-2xl font-semibold text-emerald-400">
                  {document.confidence != null
                    ? `${(document.confidence * 100).toFixed(0)}%`
                    : "—"}
                </p>
              </div>

            </div>

            {/* EXTRACTED TEXT */}
            <section>
              <h2 className="mb-3 text-sm font-medium uppercase tracking-wider text-white/40">
                Extracted Text
              </h2>

              <div className="max-h-[600px] overflow-y-auto whitespace-pre-wrap rounded-2xl border border-white/10 bg-black/20 p-5 text-sm leading-7 text-white/60">
                {document.extracted_text || "No extracted text available."}
              </div>
            </section>

          </div>
        </div>
      </div>
    </main>
  );
}
