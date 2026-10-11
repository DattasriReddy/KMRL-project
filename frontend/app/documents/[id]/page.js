"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

const API_URL = "http://127.0.0.1:8000";

export default function DocumentPage() {
  const { id } = useParams();
  const router = useRouter();

  const [documentData, setDocumentData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;

    const fetchDocument = async () => {
      try {
        const response = await fetch(`${API_URL}/documents/${id}`);

        if (!response.ok) {
          throw new Error("Document not found");
        }

        const data = await response.json();
        setDocumentData(data);
      } catch (err) {
        console.error(err);
        setError("Unable to load this document.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocument();
  }, [id]); // Download feature added - enhanced formatting

  const downloadReport = () => {
    if (!documentData) return;

    // Format the document data for download
    const reportContent =
      `KOCHI METRO RAIL LIMITED - DOCUMENT ANALYSIS REPORT
====================================================

Document Information:
- Filename: ${documentData.filename || 'N/A'}
- Category: ${documentData.category || 'N/A'}
- Confidence: ${(documentData.confidence * 100).toFixed(1)}%
- Pages: ${documentData.pages || 'N/A'}

AI Summary:
${documentData.summary || 'No summary available'}

Deadlines:
${documentData.deadline && documentData.deadline !== "No deadline specified"
  ? documentData.deadline.split(';').map(d => `- ${d.trim()}`).join('\n')
  : 'No deadline specified'}

Action Items:
${documentData.action_items && Array.isArray(documentData.action_items) && documentData.action_items.length > 0
  ? documentData.action_items.map((item, index) => `${index + 1}. ${item}`).join('\n')
  : 'No action items found'}

Extracted Text:
${documentData.extracted_text || 'No extracted text available'}

Report Generated: ${new Date().toLocaleString()}
`;

    // Create a Blob with the report content
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    // Create a temporary link to trigger download
    const a = document.createElement('a');
    a.href = url;
    a.download = `KMRL_Report_${documentData.filename || 'document'}.txt`;

    // Append to body, click, and remove
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    // Clean up the URL object
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-[#08090d] p-8 text-white">
        <div className="mx-auto max-w-4xl">
          <p className="text-white/50">Loading document...</p>
        </div>
      </main>
    );
  }

  if (error || !documentData) {
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

        <button
          onClick={() => router.back()}
          className="mb-8 text-sm text-white/50 transition hover:text-white"
        >
          ← Back to Dashboard
        </button>

        <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] shadow-2xl">

          {/* HEADER */}
          <div className="border-b border-white/10 p-6 sm:p-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

              <div>
                <p className="text-xs uppercase tracking-wider text-white/40">
                  Document
                </p>

                <h1 className="mt-2 text-2xl font-bold">
                  {documentData.filename}
                </h1>
              </div>

              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
                <div className="rounded-full bg-violet-500/10 px-4 py-2 text-sm text-violet-300">
                  {documentData.category}
                </div>

                <button
                  onClick={() => downloadReport()}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-border border-white/10 bg-white/[0.04] text-white hover:bg-white/[0.08] transition-colors"
                >
                  <span className="h-3 w-3 flex-shrink-0">
                    {/* Download icon - simple arrow down */}
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-3 w-3">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l-8-8h4.5V6a2 2 0 012-2h4.5a2 2 0 012 2v5.5H20l-8 8z" />
                    </svg>
                  </span>
                  Download Report
                </button>
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
                {documentData.summary}
              </div>
            </section>

            {/* DEADLINES & ACTION ITEMS */}
            <section>
              <h2 className="mb-3 text-sm font-medium uppercase tracking-wider text-white/40">
                DEADLINES & ACTION ITEMS
              </h2>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {/* DEADLINES CARD */}
                <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
                  <p className="text-xs uppercase tracking-wider text-white/40">
                    Deadlines
                  </p>
                  <div className="mt-2 space-y-2">
                    {(documentData?.deadline && documentData.deadline !== "No deadline specified")
                      ? (() => {
                          // Handle deadline string - split by ";" and trim
                          const deadlineParts = typeof documentData.deadline === "string"
                            ? documentData.deadline.split(";").map(part => part.trim()).filter(Boolean)
                            : [];

                          if (deadlineParts.length === 0) {
                            return (
                              <p className="text-white/50 text-sm">
                                No deadline specified
                              </p>
                            );
                          }

                          return deadlineParts.map((date, index) => (
                            <div key={index} className="flex items-center text-white/70 text-sm">
                              {/* Calendar icon - using a simple square for now */}
                              <span className="mr-2 h-3 w-3 border border-white/20 rounded inline-flex items-center justify-center">
                                <span className="h-1.5 w-1.5 bg-white/50 rounded"></span>
                              </span>
                              <span>{date}</span>
                            </div>
                          ));
                        })()
                      : (
                        <p className="text-white/50 text-sm">
                          No deadline specified
                        </p>
                      )}
                  </div>
                </div>

                {/* ACTION ITEMS CARD */}
                <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
                  <p className="text-xs uppercase tracking-wider text-white/40">
                    Action Items
                  </p>
                  <div className="mt-2 space-y-2">
                    {(documentData?.action_items && Array.isArray(documentData.action_items) && documentData.action_items.length > 0)
                      ? (() => {
                          // Handle action_items - could be array, JSON string, or null
                          let items = [];
                          if (documentData.action_items) {
                            if (typeof documentData.action_items === "string") {
                              try {
                                items = JSON.parse(documentData.action_items);
                              } catch (e) {
                                // If JSON parsing fails, treat as single item array
                                items = [documentData.action_items];
                              }
                            } else if (Array.isArray(documentData.action_items)) {
                              items = documentData.action_items;
                            }
                          }

                          return items.map((item, index) => (
                            <div key={index} className="flex items-start text-white/70 text-sm">
                              {/* Checkbox icon */}
                              <span className="mr-2 h-3 w-3 flex-shrink-0 border border-white/20 rounded">
                                <span className="h-1.5 w-1.5 bg-white/50 rounded mt-0.5 ml-0.5"></span>
                              </span>
                              <span>{item}</span>
                            </div>
                          ));
                        })()
                      : (
                        <p className="text-white/50 text-sm">
                          No action items found
                        </p>
                      )}

                  </div>
                </div>
              </div>
            </section>

            {/* STATS */}
            <div className="grid grid-cols-2 gap-4">

              <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
                <p className="text-xs uppercase tracking-wider text-white/40">
                  Pages
                </p>
                <p className="mt-2 text-2xl font-semibold">
                  {documentData.pages}
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-black/10 p-5">
                <p className="text-xs uppercase tracking-wider text-white/40">
                  Confidence
                </p>
                <p className="mt-2 text-2xl font-semibold text-emerald-400">
                  {(documentData.confidence * 100).toFixed(0)}%
                </p>
              </div>

            </div>

            {/* EXTRACTED TEXT */}
            <section>
              <h2 className="mb-3 text-sm font-medium uppercase tracking-wider text-white/40">
                Extracted Text
              </h2>

              <div className="max-h-[600px] overflow-y-auto whitespace-pre-wrap rounded-2xl border border-white/10 bg-black/20 p-5 text-sm leading-7 text-white/60">
                {documentData.extracted_text || "No extracted text available."}
              </div>
            </section>

          </div>
        </div>
      </div>
    </main>
  );
}