import DocumentPanel from "./components/DocumentPanel";
import QueryPanel from "./components/QueryPanel";
import HealthIndicator from "./components/HealthIndicator";
import ErrorBoundary from "./components/ErrorBoundary";

function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Self-RAG Engine</h1>
          <HealthIndicator />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl">
          <div className="md:col-span-1">
            <DocumentPanel />
          </div>
          <div className="md:col-span-2">
            <QueryPanel />
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;