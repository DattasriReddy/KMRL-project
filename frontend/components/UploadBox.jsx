"use client";

import { useRef, useState } from "react";

export default function UploadBox({ onFileSelect, selectedFile }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState("");

  const handleFile = (file) => {
    if (!file) return;

    if (file.type !== "application/pdf") {
      setError("Only PDF files are allowed.");
      return;
    }

    setError("");
    onFileSelect(file);
  };

  const handleInputChange = (event) => {
    const file = event.target.files?.[0];

    handleFile(file);

    event.target.value = "";
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];

    handleFile(file);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleChooseFile = () => {
    inputRef.current?.click();
  };

  const handleClear = () => {
    setError("");
    onFileSelect(null);
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="w-full max-w-2xl mx-auto">

      {/* Upload Area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleChooseFile}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-8 sm:p-12 text-center transition-all duration-300 ${
          isDragging
            ? "border-cyan-400 bg-cyan-400/10 scale-[1.02]"
            : "border-white/20 bg-white/5 hover:border-cyan-400/60 hover:bg-white/10 hover:scale-[1.01]"
        }`}
      >
        <div className="flex flex-col items-center gap-4">

          <div className="text-5xl">📄</div>

          <div>
            <h3 className="text-lg sm:text-xl font-semibold text-white">
              Drag & Drop your PDF
            </h3>

            <p className="mt-2 text-sm text-slate-400">
              or click to browse
            </p>
          </div>

          <button
            type="button"
            onClick={(event) => {
              event.stopPropagation();
              handleChooseFile();
            }}
            className="rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition-all duration-200 hover:scale-105 hover:shadow-lg active:scale-95"
          >
            Choose PDF
          </button>

          <input
            ref={inputRef}
            type="file"
            accept="application/pdf,.pdf"
            onChange={handleInputChange}
            className="hidden"
          />

          <p className="text-xs text-slate-500">
            PDF files only
          </p>

        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="mt-4 rounded-xl border border-red-400/30 bg-red-400/10 px-4 py-3 text-sm text-red-300">
          ⚠️ {error}
        </div>
      )}

      {/* Selected File */}
      {selectedFile && (
        <div className="mt-4 flex items-center justify-between gap-4 rounded-xl border border-white/10 bg-white/5 p-4 shadow-sm">

          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-white">
              {selectedFile.name}
            </p>

            <p className="mt-1 text-xs text-slate-400">
              {formatFileSize(selectedFile.size)}
            </p>
          </div>

          <button
            type="button"
            onClick={(event) => {
              event.stopPropagation();
              handleClear();
            }}
            className="shrink-0 rounded-full px-2 py-1 text-lg text-slate-400 transition-colors hover:bg-red-500/10 hover:text-red-400"
            aria-label="Remove selected file"
          >
            ✕
          </button>

        </div>
      )}

    </div>
  );
}