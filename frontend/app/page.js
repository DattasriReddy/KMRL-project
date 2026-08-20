"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import UploadBox from "@/components/UploadBox";
import ResultCard from "@/components/ResultCard";
import Loading from "@/components/Loading";

export default function Home() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    setResult(null);
    setError("");
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      setResult(data);
      setTimeout(() => {
        router.push("/dashboard");
      }, 1000);
    } catch (err) {
      console.error(err);
      setError("Something went wrong while processing the PDF.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#08090d] px-5 py-12 text-white sm:py-20">
      <div className="mx-auto max-w-5xl">

        {/* HERO */}
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

        {/* UPLOAD */}
        <section className="mx-auto max-w-3xl">
          <UploadBox
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
          />
        </section>

        {/* LOADING */}
        {isLoading && (
          <section className="mx-auto mt-8 max-w-3xl">
            <Loading />
          </section>
        )}

        {/* ERROR */}
        {!isLoading && error && (
          <section className="mx-auto mt-8 max-w-3xl rounded-xl border border-red-400/20 bg-red-400/10 p-4 text-center text-red-300">
            {error}
          </section>
        )}

        {/* RESULT */}
        {!isLoading && result && (
          <section className="mx-auto mt-8 max-w-3xl">
            <ResultCard
              category={result.category}
              summary={result.summary}
              pages={result.pages}
              confidence={result.confidence * 100}
            />
          </section>
        )}

        {/* EMPTY STATE */}
        {!selectedFile && !isLoading && (
          <div className="mt-8 text-center text-sm text-white/30">
            Upload a PDF to begin analysis
          </div>
        )}

      </div>
    </main>
  );
}