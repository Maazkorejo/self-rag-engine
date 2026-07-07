import { useState, useEffect } from "react";
import { ingestDocument, listDocuments, deleteDocument } from "../api";

export default function DocumentPanel() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const loadDocuments = async () => {
    try {
      const data = await listDocuments();
      setDocuments(data.documents);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      await ingestDocument(file);
      await loadDocuments();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteDocument(id);
      await loadDocuments();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Documents</h2>

      <label className="block mb-4">
        <span className="text-sm text-gray-600">Upload PDF, TXT, or MD</span>
        <input
          type="file"
          accept=".pdf,.txt,.md"
          onChange={handleFileChange}
          disabled={uploading}
          className="mt-2 block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-indigo-600 file:text-white file:text-sm file:font-medium hover:file:bg-indigo-700 file:cursor-pointer disabled:opacity-50"
        />
      </label>

      {uploading && <p className="text-sm text-indigo-600 mb-2">Uploading and indexing...</p>}
      {error && <p className="text-sm text-red-600 mb-2">{error}</p>}

      <ul className="space-y-2">
        {documents.length === 0 && (
          <li className="text-sm text-gray-400">No documents indexed yet.</li>
        )}
        {documents.map((doc) => (
          <li
            key={doc.id}
            className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2 text-sm"
          >
            <span className="truncate text-gray-800">{doc.filename}</span>
            <button
              onClick={() => handleDelete(doc.id)}
              className="text-red-500 hover:text-red-700 text-xs font-medium ml-2"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}