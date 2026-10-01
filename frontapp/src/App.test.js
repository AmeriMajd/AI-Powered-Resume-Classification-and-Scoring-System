import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders the resume analysis workspace", () => {
  render(<App />);
  expect(screen.getByRole("heading", { name: /see how your resume/i })).toBeInTheDocument();
  expect(screen.getByLabelText(/job description/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /analyze match/i })).toBeDisabled();
});
