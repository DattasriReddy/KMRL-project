"use client";

import { useState } from "react";

export default function SearchBar({ value = "", onChange }) {
  const [searchValue, setSearchValue] = useState(value);

  const handleChange = (e) => {
    const newValue = e.target.value;
    setSearchValue(newValue);

    if (onChange) {
      onChange(newValue);
    }
  };

  const handleClear = () => {
    setSearchValue("");

    if (onChange) {
      onChange("");
    }
  };

  return (
    <div className="w-full">
      <div className="relative flex items-center">
        {/* Search Icon */}
        <svg
          className="absolute left-4 w-5 h-5 text-gray-400 pointer-events-none"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="m21 21-4.35-4.35m2.35-5.65a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z"
          />
        </svg>

        {/* Input */}
        <input
          type="text"
          value={searchValue}
          onChange={handleChange}
          placeholder="Search documents..."
          className="w-full rounded-xl border border-gray-200 bg-white py-3 pl-12 pr-12 text-sm text-gray-800 placeholder-gray-400 outline-none transition-all duration-200 focus:border-gray-400 focus:ring-2 focus:ring-gray-100 hover:border-gray-300"
        />

        {/* Clear Button */}
        {searchValue && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 flex h-7 w-7 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 hover:text-gray-700"
            aria-label="Clear search"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 6l12 12M18 6 6 18"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}