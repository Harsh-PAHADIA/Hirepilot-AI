import { useState } from "react";
import API from "../services/api";

function Placement() {
  const [resume, setResume] = useState("");
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submitAnalysis = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await API.post("/analyze", { resume, jd });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Unable to analyze.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-shell">
      <div className="page-header">
        <div>
          <p className="page-tag">Placement analysis</p>
          <h2>Resume + JD insight</h2>
          <p className="page-description">Submit a student resume and a job description to get score-based prioritization, gap recommendations, and an action plan.</p>
        </div>
      </div>

      <div className="split-panel">
        <div className="form-card">
          <label className="field-label">Candidate resume</label>
          <textarea
            value={resume}
            onChange={(event) => setResume(event.target.value)}
            rows={10}
            className="field-textarea"
            placeholder="Paste resume text here..."
          />

          <label className="field-label">Job description</label>
          <textarea
            value={jd}
            onChange={(event) => setJd(event.target.value)}
            rows={10}
            className="field-textarea"
            placeholder="Paste job description here..."
          />

          <button className="action-button" onClick={submitAnalysis} disabled={loading || !resume.trim() || !jd.trim()}>
            {loading ? "Running analysis..." : "Run placement analysis"}
          </button>

          {error && <div className="status-error" style={{ marginTop: 16 }}>{error}</div>}
        </div>

        <div className="result-card">
          {!result && (
            <div className="empty-state-card">
              <p>Input resume and JD to generate a structured placement report.</p>
            </div>
          )}

          {result && (
            <div className="result-stack">
              <section className="result-section">
                <div className="result-heading">
                  <h3>Job match score</h3>
                  <span className="pill-pill">{result.score?.score ?? "—"}%</span>
                </div>
                <p>{result.score?.reason || "Job score generated from resume and JD match."}</p>
              </section>

              <section className="result-section">
                <h3>JD analysis</h3>
                <p>{result.jd_analysis?.summary || "JD analysis is not available."}</p>
                <div className="tag-row">
                  {result.jd_analysis?.company && <span className="tag">Company: {result.jd_analysis.company}</span>}
                  {result.jd_analysis?.role && <span className="tag">Role: {result.jd_analysis.role}</span>}
                </div>
              </section>

              <section className="result-section">
                <h3>Gap analysis</h3>
                <div className="tag-row">
                  <span className="tag">Missing skills</span>
                  <span>{result.gap_analysis?.missing_skills?.join(", ") || "None detected"}</span>
                </div>
                <ul className="bullet-list">
                  {(result.gap_analysis?.suggestions || []).map((suggestion, index) => (
                    <li key={index}>{suggestion}</li>
                  ))}
                </ul>
              </section>

              <section className="result-section">
                <h3>Action plan</h3>
                <div className="plan-grid">
                  <div>
                    <h4>Today</h4>
                    <ul className="bullet-list">
                      {(result.plan?.today || []).map((task, index) => (
                        <li key={index}>{task}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4>This week</h4>
                    <ul className="bullet-list">
                      {(result.plan?.this_week || []).map((task, index) => (
                        <li key={index}>{task}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </section>

              {result.interview_prep && (
                <section className="result-section">
                  <h3>Interview prep</h3>
                  <div className="tag-row">
                    <span className="tag">Focus areas</span>
                    <span>{result.interview_prep.focus_areas?.join(", ") || "TBD"}</span>
                  </div>
                  <ul className="bullet-list">
                    {(result.interview_prep.questions || []).map((question, index) => (
                      <li key={index}>{question}</li>
                    ))}
                  </ul>
                </section>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Placement;
