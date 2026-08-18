"use client";

export default function DashboardStats() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      
      <div className="rounded-xl border p-5">
        <p className="text-sm text-gray-500">Total Documents</p>
        <h2 className="text-2xl font-bold mt-2">24</h2>
      </div>

      <div className="rounded-xl border p-5">
        <p className="text-sm text-gray-500">Processed</p>
        <h2 className="text-2xl font-bold mt-2">18</h2>
      </div>

      <div className="rounded-xl border p-5">
        <p className="text-sm text-gray-500">Pending</p>
        <h2 className="text-2xl font-bold mt-2">4</h2>
      </div>

      <div className="rounded-xl border p-5">
        <p className="text-sm text-gray-500">Failed</p>
        <h2 className="text-2xl font-bold mt-2">2</h2>
      </div>

    </div>
  );
}