"use client";

import { useRef, useState } from "react";

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

type Strike = {
  id: string;
  type: string;
  hand: string;
  timestamp: number;
  start_frame: number;
  peak_frame: number;
  end_frame: number;
};

type QualityFlag = {
  strike_id: string;
  flag_type: string;
  severity: string;
  description: string;
};

type SessionAnalysis = {
  fps: number;
  frame_count: number;
  duration_seconds: number;
  detected_strikes: Strike[];
  quality_flags: QualityFlag[];
};

export default function Home() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<CoachReport | null>(null);
  const [debug, setDebug] = useState<SessionAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function post(endpoint: string) {
    if (!file) return;
    setLoading(true);
    setError(null);
    setReport(null);
    setDebug(null);
    const form = new FormData();
    form.append("video", file);
    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      return await res.json();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze() {
    const data = await post("/analyze");
    if (data) setReport(data as CoachReport);
  }

  async function handleDebug() {
    const data = await post("/debug/cv");
    if (data) setDebug(data as SessionAnalysis);
  }

  return (
    <main className="max-w-2xl mx-auto py-16 px-6 font-sans">
      <h1 className="text-3xl font-bold mb-8">Strikely Coach</h1>

      <div className="space-y-4">
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          className="hidden"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />

        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-zinc-300 rounded-lg p-8 text-center cursor-pointer hover:border-zinc-500 transition-colors"
        >
          {file ? (
            <p className="text-zinc-700 font-medium">{file.name}</p>
          ) : (
            <p className="text-zinc-400">Click to select a video file</p>
          )}
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="px-6 py-3 rounded-full bg-black text-white font-medium disabled:opacity-40"
          >
            {loading ? "Analyzing..." : "Analyze Session"}
          </button>
          <button
            onClick={handleDebug}
            disabled={!file || loading}
            className="px-6 py-3 rounded-full border border-zinc-300 text-zinc-700 font-medium disabled:opacity-40 hover:border-zinc-500 transition-colors"
          >
            {loading ? "Running..." : "Debug CV"}
          </button>
        </div>
      </div>

      {error && <p className="mt-6 text-red-600">{error}</p>}

      {debug && (
        <div className="mt-10 space-y-6">
          <div className="p-4 rounded-lg bg-zinc-50 border border-zinc-200 text-sm text-zinc-600 font-mono">
            {debug.duration_seconds.toFixed(1)}s &middot; {debug.fps} fps
            &middot; {debug.frame_count} frames &middot;{" "}
            {debug.detected_strikes.length} strikes &middot;{" "}
            {debug.quality_flags.length} flags
          </div>

          <section>
            <h2 className="text-xl font-semibold mb-3">Detected Strikes</h2>
            <div className="space-y-2">
              {debug.detected_strikes.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center gap-4 p-3 rounded-lg border border-zinc-200 text-sm"
                >
                  <span className="font-mono text-zinc-400 w-8">{s.id}</span>
                  <span className="font-medium w-20 capitalize">{s.type}</span>
                  <span className="text-zinc-500 w-16 capitalize">
                    {s.hand}
                  </span>
                  <span className="text-zinc-500">
                    {s.timestamp.toFixed(2)}s
                  </span>
                  <span className="text-zinc-400 font-mono text-xs ml-auto">
                    f{s.start_frame}–{s.peak_frame}–{s.end_frame}
                  </span>
                </div>
              ))}
              {debug.detected_strikes.length === 0 && (
                <p className="text-zinc-400 text-sm">No strikes detected.</p>
              )}
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-3">Quality Flags</h2>
            <div className="space-y-2">
              {debug.quality_flags.map((f, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg border border-zinc-200 text-sm"
                >
                  <div className="flex items-center gap-3 mb-1">
                    <span className="font-mono text-zinc-400">
                      {f.strike_id}
                    </span>
                    <span className="font-medium capitalize">
                      {f.flag_type.replace(/_/g, " ")}
                    </span>
                    <span
                      className={`ml-auto text-xs font-medium uppercase px-2 py-0.5 rounded-full ${
                        f.severity === "high"
                          ? "bg-red-100 text-red-700"
                          : f.severity === "medium"
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-zinc-100 text-zinc-600"
                      }`}
                    >
                      {f.severity}
                    </span>
                  </div>
                  <p className="text-zinc-500">{f.description}</p>
                </div>
              ))}
              {debug.quality_flags.length === 0 && (
                <p className="text-zinc-400 text-sm">No flags raised.</p>
              )}
            </div>
          </section>
        </div>
      )}

      {report && (
        <div className="mt-10 space-y-6">
          <section>
            <h2 className="text-xl font-semibold mb-1">Summary</h2>
            <p className="text-zinc-700">{report.summary}</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold mb-1">Strengths</h2>
            <ul className="list-disc pl-5 space-y-1 text-zinc-700">
              {report.strengths.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </section>
          <section>
            <h2 className="text-xl font-semibold mb-1">Issues</h2>
            {report.issues.map((issue, i) => (
              <div
                key={i}
                className="mb-3 p-4 rounded-lg border border-zinc-200"
              >
                <p className="font-medium">
                  {issue.flag_type} — {issue.count}x
                </p>
                <p className="text-zinc-600 mt-1">{issue.description}</p>
              </div>
            ))}
          </section>
          <section>
            <h2 className="text-xl font-semibold mb-1">Recommended Drills</h2>
            <ul className="list-disc pl-5 space-y-1 text-zinc-700">
              {report.recommended_drills.map((d, i) => (
                <li key={i}>{d}</li>
              ))}
            </ul>
          </section>
        </div>
      )}
    </main>
  );
}
