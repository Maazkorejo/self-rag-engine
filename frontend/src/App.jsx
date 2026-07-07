import DocumentPanel from "./components/DocumentPanel";

function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Self-RAG Engine</h1>
      <div className="max-w-md">
        <DocumentPanel />
      </div>
    </div>
  );
}

export default App;