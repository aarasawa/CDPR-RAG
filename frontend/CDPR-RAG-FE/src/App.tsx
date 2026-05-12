import { useState } from "react";

const API_URL = "http://localhost:8000/query";

interface QueryResponse {
  answer: string;
  sources: string[];
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    if (!question.trim()) return;
    setLoading(true);
    setError("");
    setResponse(null);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data: QueryResponse = await res.json();
      setResponse(data);
    } catch {
      setError("Failed to reach the API. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <h1 style={styles.title}>CDPR Pesticide Reg Assistant</h1>
        <p style={styles.subtitle}>
          Ask questions about California pesticide regulations, worker rights,
          and application requirements.
        </p>

        <div style={styles.inputRow}>
          <textarea
            style={styles.textarea}
            rows={3}
            placeholder="e.g. What is pesticide drift? What are worker rights?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            style={styles.button}
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? "Thinking..." : "Ask"}
          </button>
        </div>

        {error && <p style={styles.error}>{error}</p>}

        {response && (
          <div style={styles.responseBox}>
            <div style={styles.answer}>
              <div style={{ whiteSpace: "pre-wrap" }}>{response.answer}</div>
            </div>
            <div style={styles.sources}>
              <strong>Sources:</strong> {response.sources.join(", ")}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#0f0f0f",
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "center",
    padding: "48px 16px",
    fontFamily: "system-ui, sans-serif",
  },
  container: {
    width: "100%",
    maxWidth: "720px",
  },
  title: {
    color: "#ffb347",
    fontSize: "1.5rem",
    marginBottom: "8px",
    letterSpacing: "0.05em",
  },
  subtitle: {
    color: "#888",
    fontSize: "0.9rem",
    marginBottom: "24px",
  },
  inputRow: {
    display: "flex",
    gap: "12px",
    alignItems: "flex-start",
  },
  textarea: {
    flex: 1,
    backgroundColor: "#1a1a1a",
    border: "1px solid #333",
    borderRadius: "6px",
    color: "#eee",
    padding: "12px",
    fontSize: "0.95rem",
    resize: "vertical",
  },
  button: {
    backgroundColor: "#ffb347",
    color: "#0f0f0f",
    border: "none",
    borderRadius: "6px",
    padding: "12px 20px",
    fontWeight: "bold",
    cursor: "pointer",
    fontSize: "0.95rem",
    whiteSpace: "nowrap",
  },
  error: {
    color: "#ff6b6b",
    marginTop: "12px",
  },
  responseBox: {
    marginTop: "24px",
    backgroundColor: "#1a1a1a",
    border: "1px solid #333",
    borderRadius: "6px",
    padding: "20px",
  },
  answer: {
    color: "#ddd",
    lineHeight: 1.7,
    fontSize: "0.95rem",
  },
  sources: {
    marginTop: "16px",
    color: "#888",
    fontSize: "0.85rem",
    borderTop: "1px solid #222",
    paddingTop: "12px",
  },
};