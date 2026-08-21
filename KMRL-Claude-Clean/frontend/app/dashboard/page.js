"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import DashboardStats from "../../components/DashboardStats";
import DocumentCard from "../../components/DocumentCard";
import DocumentViewer from "../../components/DocumentViewer";
import SearchBar from "../../components/SearchBar";
import CategoryFilter from "../../components/CategoryFilter";
import Loader from "../../components/Loader";
import {
  getDocuments,
  searchDocuments,
  deleteDocument,
  getDownloadUrl,
} from "@/services/api";

export default function DashboardPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [previewDocument, setPreviewDocument] = useState(null);

  // Load documents from backend
  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      setError("");

      const data = await getDocuments();

      setDocuments(data.documents || data);
    } catch (err) {
      console.error(err);
      setError("Could not load documents from the backend.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  // Categories come from the actual documents
  const categories = useMemo(() => {
    const uniqueCategories = [
      ...new Set(documents.map((document) => document.category)),
    ];

    return ["All", ...uniqueCategories];
  }, [documents]);

  // Search + category filtering
  const [searchResults, setSearchResults] = useState(null);

  useEffect(() => {
    if (!search.trim()) {
      setSearchResults(null);
      return;
    }

    const runSearch = async () => {
      try {
        const data = await searchDocuments(search);
        setSearchResults(data.results || []);
      } catch (err) {
        console.error(err);
        setSearchResults([]);
      }
    };

    const timer = setTimeout(runSearch, 300);

    return () => clearTimeout(timer);
  }, [search]);

  const filteredDocuments = useMemo(() => {
    const sourceDocuments = searchResults ?? documents;

    return sourceDocuments.filter((document) => {
      const category = document.category || "";

      return (
        selectedCategory === "All" ||
        category === selectedCategory
      );
    });
  }, [documents, searchResults, selectedCategory]);

  // Convert backend document format to DocumentCard format
  const cardDocuments = filteredDocuments.map((document) => ({
    ...document,
    name: document.filename,
    status: "Processed",
    createdAt: "Recently added",
    size: "Available",
  }));

  const handlePreview = (document) => {
    setPreviewDocument(document);
  };

  const handleClosePreview = () => {
    setPreviewDocument(null);
  };

  const handleOpenFullPage = (document) => {
    setPreviewDocument(null);
    router.push(`/documents/${document.id}`);
  };

  const handleDownload = (document) => {
    window.open(getDownloadUrl(document.id), "_blank");
  };

  const handleDelete = async (documentId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this document?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await deleteDocument(documentId);

      // Remove deleted document from the UI
      setDocuments((currentDocuments) =>
        currentDocuments.filter(
          (document) => document.id !== documentId
        )
      );
    } catch (err) {
      console.error(err);
      alert("Could not delete the document.");
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">

        {/* HEADER */}
        <div className="mb-8">
          <p className="text-sm font-medium text-cyan-400">
            Document Management
          </p>

          <h1 className="mt-2 text-4xl font-black text-white">
            Dashboard
          </h1>

          <p className="mt-2 max-w-2xl text-slate-400">
            Manage, search and organize all your uploaded documents
            from one place.
          </p>
        </div>

        {/* STATISTICS */}
        <section className="mb-8">
          <DashboardStats />
        </section>

        {/* SEARCH + FILTER */}
        <section className="mb-8 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur">
          <div className="flex flex-col gap-5">

            <SearchBar
              value={search}
              onChange={setSearch}
            />

            <CategoryFilter
              categories={categories}
              selectedCategory={selectedCategory}
              onCategoryChange={setSelectedCategory}
            />

          </div>
        </section>

        {/* DOCUMENTS */}
        <section>

          <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

            <div>
              <h2 className="text-2xl font-bold text-white">
                Your Documents
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                {filteredDocuments.length} document
                {filteredDocuments.length !== 1 ? "s" : ""} found
              </p>
            </div>

          </div>

          {/* LOADING */}
          {isLoading && (
            <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-16 text-center">
              <Loader label="Loading documents..." />
            </div>
          )}

          {/* ERROR */}
          {!isLoading && error && (
            <div className="rounded-2xl border border-red-400/20 bg-red-400/10 px-6 py-16 text-center">
              <p className="text-red-300">
                {error}
              </p>

              <button
                onClick={loadDocuments}
                className="mt-4 rounded-lg bg-white px-4 py-2 text-sm font-medium text-gray-900"
              >
                Try Again
              </button>
            </div>
          )}

          {/* DOCUMENT CARDS */}
          {!isLoading && !error && cardDocuments.length > 0 && (
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              {cardDocuments.map((document) => (
                <DocumentCard
                  key={document.id}
                  document={document}
                  onView={handlePreview}
                  onDownload={handleDownload}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          )}

          {/* EMPTY */}
          {!isLoading &&
            !error &&
            cardDocuments.length === 0 && (
              <div className="rounded-2xl border border-dashed border-white/20 bg-white/5 px-6 py-16 text-center">

                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-white/10 text-2xl">
                  📄
                </div>

                <h3 className="mt-4 text-lg font-semibold text-white">
                  No documents found
                </h3>

                <p className="mt-2 text-sm text-slate-400">
                  Try another search term or select a different category.
                </p>

              </div>
            )}

        </section>

      </div>

      {/* QUICK PREVIEW MODAL */}
      {previewDocument && (
        <DocumentViewer
          document={previewDocument}
          onClose={handleClosePreview}
          onOpenFullPage={() => handleOpenFullPage(previewDocument)}
        />
      )}
    </main>
  );
}
