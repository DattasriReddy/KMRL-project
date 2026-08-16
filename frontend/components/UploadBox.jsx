"use client";

import { useRef, useState } from "react";

export default function UploadBox({ onFileSelect, selectedFile }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = (file) => {
    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Only PDF files are allowed.");
      return;
    }

    onFileSelect(file);
  };

  const handleInputChange = (event) => {
    const file = event.target.files?.[0];
    handleFile(file);

    // Allows selecting the same file again after clearing it
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
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleChooseFile}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-8 sm:p-12 text-center transition-all duration-300 ${
          isDragging
            ? "border-blue-500 bg-blue-50 scale-[1.02]"
            : "border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50/50 hover:scale-[1.01]"
        }`}
      >
        <div className="flex flex-col items-center gap-4">
          <div className="text-5xl">📄</div>

          <div>
            <h3 className="text-lg sm:text-xl font-semibold text-gray-800">
              Drag & Drop your PDF
            </h3>

            <p className="mt-2 text-sm text-gray-500">
              or click to browse
            </p>
          </div>

          <button
            type="button"
            onClick={(event) => {
              event.stopPropagation();
              handleChooseFile();
            }}
            className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white transition-all duration-200 hover:bg-blue-700 hover:shadow-lg active:scale-95"
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

          <p className="text-xs text-gray-400">
            PDF files only
          </p>
        </div>
      </div>

      {selectedFile && (
        <div className="mt-4 flex items-center justify-between gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-gray-800">
              Selected: {selectedFile.name}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              {formatFileSize(selectedFile.size)}
            </p>
          </div>

          <button
            type="button"
            onClick={handleClear}
            className="shrink-0 rounded-full px-2 py-1 text-lg text-gray-500 transition-colors hover:bg-red-50 hover:text-red-500"
            aria-label="Remove selected file"
          >
            ❌
          </button>
        </div>
      )}
    </div>
  );
}