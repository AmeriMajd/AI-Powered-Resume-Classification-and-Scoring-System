import { useRef, useState } from "react";
import {
  Alert,
  Button,
  Chip,
  CircularProgress,
  CssBaseline,
  LinearProgress,
  ThemeProvider,
  createTheme,
} from "@mui/material";
import "./App.css";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#b9ff66" },
    secondary: { main: "#8ca8ff" },
    background: { default: "#0b0d10", paper: "#13171c" },
  },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    button: { textTransform: "none", fontWeight: 700 },
  },
  shape: { borderRadius: 14 },
});

const SAMPLE_JOB =
  "We are looking for a Python backend developer to build and maintain REST APIs. " +
  "You should have experience with FastAPI, PostgreSQL, Docker, AWS, automated testing, " +
  "and Git. Experience deploying machine-learning models is a plus.";

function SkillList({ items, tone = "default", emptyText }) {
  if (!items?.length) return <p className="empty-copy">{emptyText}</p>;
  return (
    <div className="chip-list">
      {items.map((item) => (
        <Chip key={item} label={item} size="small" className={"skill-chip " + tone} />
      ))}
    </div>
  );
}

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  const selectFile = (file) => {
    setError("");
    setResult(null);
    if (!file) return;
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please choose a PDF file.");
      return;
    }
    if (file.size > 6 * 1024 * 1024) {
      setError("Your PDF must be smaller than 6 MB.");
      return;
    }
    setResume(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragActive(false);
    selectFile(event.dataTransfer.files?.[0]);
  };

  const handleAnalyze = async () => {
    if (!resume || !jobDescription.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jobDescription.trim());

    try {
      const response = await fetch("/api/analyze", { method: "POST", body: formData });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || "Analysis failed. Please try again.");
      setResult(data);
    } catch (requestError) {
      setError(requestError.message || "The server could not be reached.");
    } finally {
      setLoading(false);
    }
  };

  const canAnalyze = resume && jobDescription.trim() && !loading;
  const roleConfidence = result ? Math.round(result.role_confidence * 100) : 0;

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="app-shell">
        <header className="site-header">
          <a className="brand" href="#top" aria-label="Resume Match Lab home">
            <span className="brand-mark">RM</span>
            <span>Resume Match Lab</span>
          </a>
          <span className="engine-label"><i /> Explainable NLP demo</span>
        </header>

        <main id="top">
          <section className="hero">
            <div className="eyebrow">Resume intelligence, without the black box</div>
            <h1>See how your resume<br />meets the role.</h1>
            <p>
              Upload a text-based PDF and paste a job description. Get an instant role prediction,
              match score, skill-gap breakdown, and practical suggestions.
            </p>
          </section>

          <section className="workspace" aria-label="Resume analysis workspace">
            <div className="input-panel panel">
              <div className="panel-heading">
                <span className="step">01</span>
                <div><h2>Add your inputs</h2><p>Your file is processed in memory and is not stored.</p></div>
              </div>

              <div
                className={"drop-zone " + (dragActive ? "active " : "") + (resume ? "has-file" : "")}
                onDragEnter={(event) => { event.preventDefault(); setDragActive(true); }}
                onDragOver={(event) => event.preventDefault()}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
                role="button"
                tabIndex={0}
                onKeyDown={(event) => event.key === "Enter" && inputRef.current?.click()}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept="application/pdf,.pdf"
                  hidden
                  onChange={(event) => selectFile(event.target.files?.[0])}
                />
                <span className="file-icon">{resume ? "✓" : "↑"}</span>
                {resume ? (
                  <div><strong>{resume.name}</strong><span>{(resume.size / 1024).toFixed(0)} KB · Ready to analyze</span></div>
                ) : (
                  <div><strong>Drop your resume here</strong><span>or click to choose a PDF · max 6 MB</span></div>
                )}
              </div>

              <div className="field-heading">
                <label htmlFor="job-description">Job description</label>
                <button type="button" onClick={() => setJobDescription(SAMPLE_JOB)}>Use sample</button>
              </div>
              <textarea
                id="job-description"
                value={jobDescription}
                onChange={(event) => { setJobDescription(event.target.value); setResult(null); }}
                placeholder="Paste the full job description here…"
                rows={10}
                maxLength={20000}
              />
              <div className="character-count">{jobDescription.length.toLocaleString()} / 20,000</div>

              {error && <Alert severity="error" variant="outlined">{error}</Alert>}
              <Button
                className="analyze-button"
                variant="contained"
                color="primary"
                size="large"
                disabled={!canAnalyze}
                onClick={handleAnalyze}
              >
                {loading ? <><CircularProgress size={20} color="inherit" /> Analyzing resume…</> : "Analyze match →"}
              </Button>
            </div>

            <div className="result-panel panel" aria-live="polite">
              <div className="panel-heading">
                <span className="step">02</span>
                <div><h2>Your match report</h2><p>Evidence you can use to tailor your application.</p></div>
              </div>

              {!result && !loading && (
                <div className="result-placeholder">
                  <div className="radar"><span /><span /><span /><b>?</b></div>
                  <h3>Your report will appear here</h3>
                  <p>We compare language and named technical skills, then explain what influenced the score.</p>
                  <ul><li>Likely professional role</li><li>Resume-to-job similarity</li><li>Matching and missing skills</li><li>Actionable recommendations</li></ul>
                </div>
              )}

              {loading && (
                <div className="loading-state">
                  <div className="scan-lines" />
                  <h3>Reading your experience…</h3>
                  <p>Extracting text, mapping skills, and comparing the role.</p>
                  <LinearProgress color="primary" />
                </div>
              )}

              {result && (
                <div className="report">
                  <div className="score-row">
                    <div className="score-ring" style={{ "--score": String(result.match_score * 3.6) + "deg" }}>
                      <div><strong>{Math.round(result.match_score)}</strong><span>/100</span></div>
                    </div>
                    <div className="score-summary">
                      <span className="report-label">Overall match</span>
                      <h3>{result.match_score >= 70 ? "Strong alignment" : result.match_score >= 45 ? "Promising foundation" : "Room to tailor"}</h3>
                      <p>{result.document.filename} · {result.document.pages} page{result.document.pages === 1 ? "" : "s"} · {result.document.word_count} words</p>
                    </div>
                  </div>

                  <div className="metric-grid">
                    <div><span>Likely role</span><strong>{result.predicted_role}</strong><small>{roleConfidence}% relative confidence</small></div>
                    <div><span>Text similarity</span><strong>{result.text_similarity}%</strong><small>TF-IDF language overlap</small></div>
                    <div><span>Skill coverage</span><strong>{result.skill_coverage ?? "—"}{result.skill_coverage != null ? "%" : ""}</strong><small>Named job skills found</small></div>
                  </div>

                  <div className="report-section">
                    <h4>Matching skills <span>{result.matching_skills.length}</span></h4>
                    <SkillList items={result.matching_skills} tone="positive" emptyText="No named skills overlapped yet." />
                  </div>
                  <div className="report-section">
                    <h4>Skills to review <span>{result.missing_skills.length}</span></h4>
                    <SkillList items={result.missing_skills} tone="warning" emptyText="No missing named skills detected." />
                  </div>
                  <div className="report-section">
                    <h4>Suggestions</h4>
                    <ol className="recommendations">
                      {result.recommendations.map((item, index) => <li key={item}><b>{index + 1}</b><span>{item}</span></li>)}
                    </ol>
                  </div>
                  <p className="disclaimer">This explainable portfolio demo is not a hiring decision tool. Scores are directional and should be reviewed by a person.</p>
                </div>
              )}
            </div>
          </section>
        </main>

        <footer><span>Built with React, Flask, scikit-learn & Docker</span><span>Privacy-first · No resume storage</span></footer>
      </div>
    </ThemeProvider>
  );
}

export default App;
