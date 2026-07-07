import DocumentPanel from "./components/DocumentPanel";
import QueryPanel from "./components/QueryPanel";

function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Self-RAG Engine</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl">
        <div className="md:col-span-1">
          <DocumentPanel />
        </div>
        <div className="md:col-span-2">
          <QueryPanel />
        </div>
      </div>
    </div>
  );
}

export default App;