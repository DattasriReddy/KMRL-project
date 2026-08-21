"use client";

import { useEffect, useState } from "react";
import { getStats } from "@/services/api";
import Loader from "./Loader";

export default function DashboardStats() {
  const [stats, setStats] = useState({
    total: 0,
    processed: 0,
    pending: 0,
    failed: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        setIsLoading(true);
        const data = await getStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to load stats:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, []);

  if (isLoading) {
    return (
      <div className="rounded-xl border border-white/10 bg-white/5 p-8">
        <Loader size="sm" label="Loading stats..." />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      
      <div className="rounded-xl border border-white/10 bg-white/5 p-5">
        <p className="text-sm text-slate-400">
          Total Documents
        </p>
        <h2 className="mt-2 text-2xl font-bold text-white">
          {stats.total}
        </h2>
      </div>

      <div className="rounded-xl border border-white/10 bg-white/5 p-5">
        <p className="text-sm text-slate-400">
          Processed
        </p>
        <h2 className="mt-2 text-2xl font-bold text-white">
          {stats.processed}
        </h2>
      </div>

      <div className="rounded-xl border border-white/10 bg-white/5 p-5">
        <p className="text-sm text-slate-400">
          Pending
        </p>
        <h2 className="mt-2 text-2xl font-bold text-white">
          {stats.pending}
        </h2>
      </div>

      <div className="rounded-xl border border-white/10 bg-white/5 p-5">
        <p className="text-sm text-slate-400">
          Failed
        </p>
        <h2 className="mt-2 text-2xl font-bold text-white">
          {stats.failed}
        </h2>
      </div>

    </div>
  );
}