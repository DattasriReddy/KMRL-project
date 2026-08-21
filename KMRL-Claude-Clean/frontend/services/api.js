// Central API client for the KMRL Document Intelligence backend.
// Every page/component should go through these helpers instead of
// hardcoding fetch() calls and base URLs, so there is a single place
// to change the backend URL (e.g. for a Render deployment).

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function handleResponse(response, fallbackMessage) {
  if (!response.ok) {
    let message = fallbackMessage;

    try {
      const data = await response.json();
      message = data?.error || fallbackMessage;
    } catch {
      // response body wasn't JSON - fall back to default message
    }

    throw new Error(message);
  }

  return response.json();
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  return handleResponse(response, "Upload failed");
}

export async function searchDocuments(query) {
  const response = await fetch(
    `${API_BASE_URL}/search?q=${encodeURIComponent(query)}`
  );

  return handleResponse(response, "Search failed");
}

export async function getDocuments() {
  const response = await fetch(`${API_BASE_URL}/documents`);

  return handleResponse(response, "Failed to load documents");
}

export async function getDocument(id) {
  const response = await fetch(`${API_BASE_URL}/documents/${id}`);

  return handleResponse(response, "Document not found");
}

export async function deleteDocument(id) {
  const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
    method: "DELETE",
  });

  return handleResponse(response, "Delete failed");
}

export async function getStats() {
  const response = await fetch(`${API_BASE_URL}/stats`);

  return handleResponse(response, "Failed to load stats");
}

export function getDownloadUrl(id) {
  return `${API_BASE_URL}/documents/${id}/download`;
}

export { API_BASE_URL };
