"use client";

import { useState } from "react";

type Issue = {
  flag_type: string;
  count: number;
  description: string;
  affected_strikes: string[];
};

type CoachReport = {
  summary: string;
  strengths: string[];
  issues: Issue[];
  recommended_drills: string[];
};

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<CoachReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/analyze", { method: "POST" });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data: CoachReport = await res.json();
      setReport(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-2xl mx-auto py-16 px-6 font-sans">
      <h1 className="text-3xl font-bold mb-8">Strikely Coach</h1>

      <button
        onClick={handleAnalyze}
        disabled={loading}
        className="px-6 py-3 rounded-full bg-black text-white font-medium disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Analyze Session"}
      </button>

      {error && <p className="mt-6 text-red-600">{error}</p>}

      {report && (
        <div className="mt-10 space-y-6">
          <section>
            <h2 className="text-xl font-semibold mb-1">Summary</h2>
            <p className="text-zinc-700">{report.summary}</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold mb-1">Strengths</h2>
            <ul className="list-disc pl-5 space-y-1 text-zinc-700">
              {report.strengths.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
          </section>
          <section>
            <h2 className="text-xl font-semibold mb-1">Issues</h2>
            {report.issues.map((issue, i) => (
              <div key={i} className="mb-3 p-4 rounded-lg border border-zinc-200">
                <p className="font-medium">{issue.flag_type} — {issue.count}x</p>
                <p className="text-zinc-600 mt-1">{issue.description}</p>
              </div>
            ))}
          </section>
          <section>
            <h2 className="text-xl font-semibold mb-1">Recommended Drills</h2>
            <ul className="list-disc pl-5 space-y-1 text-zinc-700">
              {report.recommended_drills.map((d, i) => <li key={i}>{d}</li>)}
            </ul>
          </section>
        </div>
      )}
    </main>
  );
}
