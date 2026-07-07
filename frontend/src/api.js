const API_BASE_URL = "http://127.0.0.1:5000/api/v1";
const API_KEY = import.meta.env.VITE_API_KEY;

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      ...options.headers,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }

  return data;
}

export async function ingestDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request("/ingest", {
    method: "POST",
    body: formData,
  });
}

export async function runQuery(query, topK = 5, forceRetrieve = false) {
  return request("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK, force_retrieve: forceRetrieve }),
  });
}

export async function listDocuments() {
  return request("/documents");
}

export async function deleteDocument(documentId) {
  return request(`/documents/${documentId}`, { method: "DELETE" });
}

export async function checkHealth() {
  const response = await fetch("http://127.0.0.1:5000/api/v1/health");
  return response.json();
}