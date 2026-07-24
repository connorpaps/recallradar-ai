"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <div className="panel p-8">
      <h1 className="text-2xl font-bold">RecallRadar could not load this view.</h1>
      <p className="mt-2 text-sm text-slate-500">Check that the FastAPI backend is running at the configured API URL.</p>
      <button onClick={reset} className="btn-primary mt-5">Try again</button>
    </div>
  );
}
