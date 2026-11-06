import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import ProjectPage from "./ProjectPage";

afterEach(() => {
  jest.restoreAllMocks();
});

function renderPage(projectId = "robot-arm") {
  render(
    <MemoryRouter
      initialEntries={[`/projects/${projectId}`]}
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <Routes>
        <Route path="/projects/:projectId" element={<ProjectPage />} />
      </Routes>
    </MemoryRouter>
  );
}

function mockFetch(status, body) {
  return jest.spyOn(global, "fetch").mockResolvedValue({
    ok: status >= 200 && status < 300,
    json: () => Promise.resolve(body),
  });
}

test("loads and shows the project's details", async () => {
  const fetchSpy = mockFetch(200, {
    projectName: "Robot Arm",
    projectId: "robot-arm",
    description: "Senior design prototype",
    hwSets: { HWSet1: 5 },
    users: ["sydney", "alice"],
  });
  renderPage();

  expect(await screen.findByRole("heading", { name: "Robot Arm" })).toBeTruthy();
  expect(screen.getByText("Project ID: robot-arm")).toBeTruthy();
  expect(screen.getByRole("heading", { name: "Description" })).toBeTruthy();
  expect(screen.getByText("Senior design prototype")).toBeTruthy();
  expect(screen.getByText("HWSet1: 5")).toBeTruthy();
  expect(fetchSpy.mock.calls[0][0]).toBe("/api/projects/robot-arm");
});

test("shows the server error for a missing project", async () => {
  mockFetch(404, { error: "Project not found." });
  renderPage("ghost");

  expect((await screen.findByRole("alert")).textContent).toBe("Project not found.");
});

test("has a link back to the dashboard", async () => {
  mockFetch(404, { error: "Project not found." });
  renderPage();
  await screen.findByRole("alert"); // let the fetch finish first

  expect(
    screen.getByRole("link", { name: "Back to Dashboard" }).getAttribute("href")
  ).toBe("/dashboard");
});

test("members list is closed until the Members tab is clicked", async () => {
  mockFetch(200, {
    projectName: "Robot Arm",
    projectId: "robot-arm",
    description: "",
    hwSets: {},
    users: ["sydney", "alice"],
  });
  renderPage();

  const toggle = await screen.findByRole("button", { name: /Members \(2\)/ });
  expect(toggle.getAttribute("aria-expanded")).toBe("false");
  expect(screen.queryByText("alice")).toBeNull();

  fireEvent.click(toggle);
  expect(toggle.getAttribute("aria-expanded")).toBe("true");
  expect(screen.getByText("sydney")).toBeTruthy();
  expect(screen.getByText("alice")).toBeTruthy();

  fireEvent.click(toggle);
  expect(screen.queryByText("alice")).toBeNull();
});
