"use client";

import { useState } from "react";
import UploadBox from "./components/UploadBox";
import DocumentPreview from "./DocumentPreview";

export default function UploadSection() {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
  };

  const handleRemove = () => {
    setSelectedFile(null);
  };

  const handleChange = () => {
    setSelectedFile(null);
  };

  return (
    <section className="w-full px-4 py-8">
      <div className="mx-auto max-w-3xl">
        {!selectedFile ? (
          <UploadBox
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
          />
        ) : (
          <DocumentPreview
            file={selectedFile}
            onRemove={handleRemove}
            onChange={handleChange}
          />
        )}
      </div>
    </section>
  );
}