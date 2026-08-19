"use client";

import { useMemo, useState } from "react";
import DashboardStats from "../../components/DashboardStats";
import DocumentCard from "../../components/DocumentCard";
import SearchBar from "../../components/SearchBar";
import CategoryFilter from "../../components/CategoryFilter";

const documents = [
  {
    id: 1,
    name: "Project Report.pdf",
    category: "Report",
    size: "2.4 MB",
    status: "Processed",
    createdAt: "Today",
  },
  {
    id: 2,
    name: "Resume.pdf",
    category: "Resume",
    size: "1.2 MB",
    status: "Processed",
    createdAt: "Yesterday",
  },
  {
    id: 3,
    name: "Research Paper.pdf",
    category: "Research",
    size: "3.8 MB",
    status: "Processing",
    createdAt: "2 days ago",
  },
  {
    id: 4,
    name: "Invoice.pdf",
    category: "Invoice",
    size: "850 KB",
    status: "Processed",
    createdAt: "3 days ago",
  },
];

const categories = [
  "All",
  "Resume",
  "Report",
  "Invoice",
  "Research",
  "Other",
];

export default function DashboardPage() {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  const filteredDocuments = useMemo(() => {
    return documents.filter((document) => {
      const matchesSearch = document.name
        .toLowerCase()
        .includes(search.toLowerCase());

      const matchesCategory =
        selectedCategory === "All" ||
        document.category === selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }, [search, selectedCategory]);

  const handleView = (document) => {
    console.log("View document:", document);
  };

  const handleDownload = (document) => {
    console.log("Download document:", document);
  };

  const handleDelete = (documentId) => {
    console.log("Delete document:", documentId);
  };

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">

        {/* Header */}
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

        {/* Statistics */}
        <section className="mb-8">
          <DashboardStats />
        </section>

        {/* Search and Category Filter */}
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

        {/* Documents Header */}
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

          {/* Document Cards */}
          {filteredDocuments.length > 0 ? (
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              {filteredDocuments.map((document) => (
                <DocumentCard
                  key={document.id}
                  document={document}
                  onView={handleView}
                  onDownload={handleDownload}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          ) : (
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
    </main>
  );
}