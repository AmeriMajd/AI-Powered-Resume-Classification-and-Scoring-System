import { useState } from "react";
import {
  Container,
  Typography,
  Button,
  TextField,
  Box,
  LinearProgress,
  Paper,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from "@mui/material";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#00bcd4" },
    secondary: { main: "#ff4081" },
    background: {
      default: "#181c24",
      paper: "rgba(30,34,44,0.95)",
    },
  },
  typography: {
    fontFamily: "'Poppins', sans-serif",
  },
});

function App() {
  const [resume, setResume] = useState(null);
  const [jobDesc, setJobDesc] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!resume || !jobDesc) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_desc", jobDesc);

    const classifyRes = await fetch("http://localhost:5000/classify", {
      method: "POST",
      body: formData,
    });
    const classifyData = await classifyRes.json();

    const formData2 = new FormData();
    formData2.append("resume", resume);
    formData2.append("job_desc", jobDesc);

    const scoreRes = await fetch("http://localhost:5000/score", {
      method: "POST",
      body: formData2,
    });
    const scoreData = await scoreRes.json();

    setResult({
      job_role: classifyData.job_role,
      confidence: classifyData.confidence,
      score: scoreData.score,
    });
    setLoading(false);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "100vh",
          background: "linear-gradient(135deg, #232526 0%, #1a2980 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "'Poppins', sans-serif",
        }}
      >
        <Container maxWidth="sm">
          <Paper elevation={6} sx={{ p: 4, borderRadius: 4, boxShadow: 8 }}>
            <Typography
              variant="h3"
              align="center"
              gutterBottom
              sx={{
                fontWeight: 600,
                color: "primary.main",
                letterSpacing: 1,
                mb: 2,
              }}
            >
              Resume Analyzer
            </Typography>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <Button
                variant="contained"
                component="label"
                color={resume ? "success" : "primary"}
                sx={{ fontWeight: 600, fontSize: "1rem" }}
              >
                {resume ? resume.name : "Upload Resume (PDF)"}
                <input
                  type="file"
                  accept=".pdf"
                  hidden
                  onChange={(e) => setResume(e.target.files[0])}
                />
              </Button>
              <TextField
                label="Job Description"
                multiline
                minRows={4}
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
                variant="outlined"
                sx={{
                  background: "rgba(255,255,255,0.04)",
                  borderRadius: 2,
                  input: { color: "#fff" },
                  label: { color: "#bbb" },
                }}
              />
              <Button
                variant="contained"
                color="secondary"
                onClick={handleAnalyze}
                disabled={loading || !resume || !jobDesc}
                size="large"
                sx={{ fontWeight: 600, fontSize: "1.1rem" }}
              >
                {loading ? "Analyzing..." : "Analyze Resume"}
              </Button>
              {loading && <LinearProgress color="secondary" />}
              {result && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" color="primary">
                    Result:
                  </Typography>
                  <Typography>
                    <strong>Job Role:</strong> {result.job_role} (Confidence: {result.confidence?.toFixed(2)})
                  </Typography>
                  <Typography>
                    <strong>Match Score:</strong> {result.score?.toFixed(2)}
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;