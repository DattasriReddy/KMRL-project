"use client";

import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

export default function DashboardStats() {
  const [stats, setStats] = useState({
    total: 0,
    processed: 0,
    pending: 0,
    failed: 0,
  });

  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await fetch(`${API_URL}/stats`);

        if (!response.ok) {
          throw new Error("Failed to load stats");
        }

        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error("Stats error:", error);
      }
    };

    loadStats();
  }, []);

  const cards = [
    ["Total Documents", stats.total],
    ["Processed", stats.processed],
    ["Pending", stats.pending],
    ["Failed", stats.failed],
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map(([label, value]) => (
        <div
          key={label}
          className="rounded-xl border border-white/10 bg-white/5 p-5"
        >
          <p className="text-sm text-gray-400">{label}</p>
          <h2 className="mt-2 text-2xl font-bold text-white">
            {value}
          </h2>
        </div>
      ))}
    </div>
  );
}