import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import CreateProjectPage from "./CreateProjectPage";

beforeEach(() => {
  // Pretend "sydney" signed in, the same way LoginPage does.
  sessionStorage.setItem("dashboardUserId", "sydney");
});

afterEach(() => {
  sessionStorage.clear();
  jest.restoreAllMocks();
});

function renderPage() {
  render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <CreateProjectPage />
    </MemoryRouter>
  );
}

function mockFetch(status, body) {
  jest.spyOn(global, "fetch").mockResolvedValue({
    ok: status >= 200 && status < 300,
    json: () => Promise.resolve(body),
  });
}

function fillAndSubmit() {
  fireEvent.change(screen.getByLabelText("Project Name"), {
    target: { value: "Robot Arm" },
  });
  fireEvent.change(screen.getByLabelText("Project ID"), {
    target: { value: "robot-arm" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Create Project" }));
}

test("creates a project and shows a confirmation", async () => {
  mockFetch(201, { projectName: "Robot Arm", projectId: "robot-arm" });
  renderPage();

  fillAndSubmit();

  expect(await screen.findByRole("status")).toHaveTextContent("robot-arm");
  expect(global.fetch).toHaveBeenCalledWith(
    "/api/projects",
    expect.objectContaining({ method: "POST" })
  );
  const sentBody = JSON.parse(global.fetch.mock.calls[0][1].body);
  expect(sentBody.userId).toBe("sydney");
});

test("shows the server's error when the ID is taken", async () => {
  mockFetch(409, { error: "Project ID 'robot-arm' is already taken." });
  renderPage();

  fillAndSubmit();

  expect(await screen.findByRole("alert")).toHaveTextContent("already taken");
});

test("requires name and ID before calling the server", async () => {
  jest.spyOn(global, "fetch");
  renderPage();

  fireEvent.click(screen.getByRole("button", { name: "Create Project" }));

  expect(await screen.findByRole("alert")).toHaveTextContent("required");
  expect(global.fetch).not.toHaveBeenCalled();
});

test("has no user ID field; the signed-in user is used", () => {
  renderPage();

  expect(screen.queryByLabelText(/user id/i)).toBeNull();
});

test("links back to the dashboard", () => {
  renderPage();

  expect(screen.getByRole("link", { name: "Back to Dashboard" })).toHaveAttribute("href", "/dashboard");
});
test("shows a Go to Project button after the project is created", async () => {
  mockFetch(201, { projectName: "Robot Arm", projectId: "robot-arm" });
  render(
    <MemoryRouter
      initialEntries={["/projects/new"]}
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <Routes>
        <Route path="/projects/new" element={<CreateProjectPage />} />
        <Route path="/projects/:projectId" element={<p>Project page for robot-arm</p>} />
      </Routes>
    </MemoryRouter>
  );

  fillAndSubmit();

  const goButton = await screen.findByRole("button", { name: "Go to Project" });
  fireEvent.click(goButton);

  expect(await screen.findByText("Project page for robot-arm")).toBeInTheDocument();
});

test("does not show Go to Project when creation fails", async () => {
  mockFetch(409, { error: "Project ID 'robot-arm' is already taken." });
  renderPage();

  fillAndSubmit();

  await screen.findByRole("alert");
  expect(screen.queryByRole("button", { name: "Go to Project" })).toBeNull();
});