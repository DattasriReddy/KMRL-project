"use client";

export default function DocumentPreview({ file, onRemove, onChange }) {
  if (!file) return null;

  const fileSize =
    file.size < 1024 * 1024
      ? `${(file.size / 1024).toFixed(1)} KB`
      : `${(file.size / (1024 * 1024)).toFixed(1)} MB`;

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-lg transition-all duration-300 hover:-translate-y-1 hover:shadow-xl sm:p-6">
        
        {/* File information */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          
          <div className="flex min-w-0 items-center gap-4">
            
            {/* PDF Icon */}
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-red-50 text-3xl">
              📄
            </div>

            {/* File name and size */}
            <div className="min-w-0">
              <h3 className="truncate text-base font-semibold text-gray-800 sm:text-lg">
                {file.name}
              </h3>

              <p className="mt-1 text-sm text-gray-500">
                PDF • {fileSize}
              </p>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex w-full gap-3 sm:w-auto">
            <button
              type="button"
              onClick={onChange}
              className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-all duration-200 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-600 active:scale-95 sm:flex-none"
            >
              Change
            </button>

            <button
              type="button"
              onClick={onRemove}
              className="flex-1 rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-500 transition-all duration-200 hover:bg-red-50 hover:text-red-600 active:scale-95 sm:flex-none"
            >
              Remove
            </button>
          </div>
        </div>

        {/* Preview status */}
        <div className="mt-5 rounded-xl bg-green-50 px-4 py-3">
          <p className="text-sm font-medium text-green-700">
            ✓ PDF selected successfully
          </p>
        </div>
      </div>
    </div>
  );
}