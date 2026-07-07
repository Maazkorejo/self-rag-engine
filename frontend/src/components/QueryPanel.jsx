import { useState } from "react";
import { runQuery } from "../api";

const STEP_LABELS = {
  Retrieve: "Retrieve Decision",
  IsRel: "Relevance Check",
  IsSup: "Support Verification",
  IsUse: "Utility Score",
};

function StepBadge({ step }) {
  if (step.step === "Retrieve") {
    return (
      <div className="flex items-center gap-3 py-2">
        <span className={`w-2.5 h-2.5 rounded-full ${step.decision ? "bg-emerald-500" : "bg-gray-400"}`} />
        <span className="text-sm text-gray-700">
          <strong>{STEP_LABELS.Retrieve}:</strong> {step.decision ? "Retrieval needed" : "Answering directly"}
        </span>
      </div>
    );
  }

  if (step.step === "IsRel") {
    return (
      <div className="flex items-center gap-3 py-2">
        <span className={`w-2.5 h-2.5 rounded-full ${step.relevant ? "bg-emerald-500" : "bg-red-400"}`} />
        <span className="text-sm text-gray-700">
          <strong>{STEP_LABELS.IsRel}:</strong> chunk {step.chunk_id?.slice(0, 8)}... marked{" "}
          {step.relevant ? "relevant" : "irrelevant"}
        </span>
      </div>
    );
  }

  if (step.step === "IsSup") {
    const color =
      step.status === "FULLY_SUPPORTED"
        ? "bg-emerald-500"
        : step.status === "PARTIALLY_SUPPORTED"
        ? "bg-amber-500"
        : "bg-red-500";
    return (
      <div className="flex items-center gap-3 py-2">
        <span className={`w-2.5 h-2.5 rounded-full ${color}`} />
        <span className="text-sm text-gray-700">
          <strong>{STEP_LABELS.IsSup}</strong> (attempt {step.attempt}): {step.status}
        </span>
      </div>
    );
  }

  if (step.step === "IsUse") {
    return (
      <div className="flex items-center gap-3 py-2">
        <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
        <span className="text-sm text-gray-700">
          <strong>{STEP_LABELS.IsUse}:</strong> {step.score}/5
        </span>
      </div>
    );
  }

  return null;
}

export default function QueryPanel() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runQuery(query);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Ask a Question</h2>

      <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask something about your documents..."
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {error && <p className="text-sm text-red-600 mb-4">{error}</p>}

      {result && (
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Reflection Pipeline
            </h3>
            <div className="bg-gray-50 rounded-lg p-4">
              {result.reflection_log.map((step, i) => (
                <StepBadge key={i} step={step} />
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Answer
            </h3>
            <p className="text-gray-900 whitespace-pre-wrap">{result.final_answer}</p>
            {result.hallucination_risk && (
              <p className="text-xs text-red-600 mt-2">
                ⚠ Hallucination risk flagged — answer may not be fully grounded.
              </p>
            )}
          </div>

          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span>Utility: {result.utility_score}/5</span>
            <span>Sources used: {result.sources_used.length}</span>
          </div>
        </div>
      )}
    </div>
  );
}