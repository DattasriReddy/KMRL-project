<<<<<<< HEAD
"use client";

import { useState } from "react";
import UploadBox from "@/components/UploadBox";
import ResultCard from "@/components/ResultCard";
import Loading from "@/components/Loading";
=======
import UploadSection from "../UploadSection";
>>>>>>> 44d7734 (feat: complete document dashboard and upload UI)

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileSelect = (file) => {
    setSelectedFile(file);

    // Temporary demo loading state
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
    }, 1500);
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

<<<<<<< HEAD
          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-white/50 sm:text-lg">
            Upload KMRL documents and let AI extract, classify and
            summarize the information that matters.
          </p>

        </section>


        {/* UPLOAD SECTION */}
        <section className="mx-auto max-w-3xl">

          <UploadBox
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
          />

        </section>
=======
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

        {/* Upload Section */}
        <div className="mx-auto mt-16 max-w-xl">
          <UploadSection />
        </div>

        {/* Features */}
        <div className="mt-14 grid gap-6 md:grid-cols-3">
>>>>>>> 44d7734 (feat: complete document dashboard and upload UI)


        {/* LOADING */}
        {isLoading && (
          <section className="mx-auto mt-8 max-w-3xl">
            <Loading />
          </section>
        )}


        {/* RESULT */}
        {!isLoading && selectedFile && (
          <section className="mx-auto mt-8 max-w-3xl">

            <ResultCard
              category="Maintenance"
              summary="The inspection report identifies electrical maintenance issues that require attention at the station."
              pages={2}
              confidence={98}
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