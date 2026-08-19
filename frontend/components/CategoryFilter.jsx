"use client";

import React from "react";

const defaultCategories = [
  "All",
  "Resume",
  "Report",
  "Invoice",
  "Research",
  "Other",
];

export default function CategoryFilter({
  categories = defaultCategories,
  selectedCategory = "All",
  onCategoryChange,
}) {
  const handleCategoryChange = (category) => {
    if (onCategoryChange) {
      onCategoryChange(category);
    }
  };

  return (
    <div className="w-full">
      <div className="flex flex-wrap items-center gap-2">
        {categories.map((category) => {
          const isActive = selectedCategory === category;

          return (
            <button
              key={category}
              type="button"
              onClick={() => handleCategoryChange(category)}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "border-gray-900 bg-gray-900 text-white shadow-sm"
                  : "border-gray-200 bg-white text-gray-600 hover:border-gray-400 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              {category}
            </button>
          );
        })}
      </div>
    </div>
  );
}