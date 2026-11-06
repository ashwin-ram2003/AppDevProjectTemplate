import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import HomePage from "./HomePage";

afterEach(() => {
  jest.restoreAllMocks();
  sessionStorage.clear();
});

function renderPage() {
  render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <HomePage />
    </MemoryRouter>
  );
}

function mockFetch(status, body) {
  return jest.spyOn(global, "fetch").mockResolvedValue({
    ok: status >= 200 && status < 300,
    json: () => Promise.resolve(body),
  });
}

function submitUserId(userId) {
  fireEvent.change(screen.getByLabelText("User ID"), {
    target: { value: userId },
  });
  fireEvent.click(screen.getByRole("button", { name: "Show My Projects" }));
}

const PROJECTS = [
  {
    projectName: "Robot Arm",
    projectId: "robot-arm",
    description: "Senior design prototype",
    hwSets: {},
    users: ["sydney", "alice"],
  },
  {
    projectName: "Solo Project",
    projectId: "solo",
    description: "",
    hwSets: {},
    users: ["sydney"],
  },
];

test("dashboard displays projects section and create project link", () => {
  renderPage();

  expect(
    screen.getByRole("heading", { name: "My Dashboard" })
  ).toBeTruthy();

  expect(
    screen.getByRole("heading", { name: "My Projects" })
  ).toBeTruthy();

  const createProjectLink = screen.getByRole("link", {
    name: /create project/i,
  });

  expect(createProjectLink.getAttribute("href")).toBe("/projects/new");
});

test("dashboard links to the join project page", () => {
  renderPage();

  const joinProjectLink = screen.getByRole("link", { name: /join project/i });

  expect(joinProjectLink.getAttribute("href")).toBe("/projects/join");
});

test("shows every project the user belongs to", async () => {
  const fetchSpy = mockFetch(200, { projects: PROJECTS });
  renderPage();

  submitUserId(" sydney ");

  expect(await screen.findByRole("link", { name: "Robot Arm" })).toBeTruthy();
  expect(screen.getByRole("link", { name: "Solo Project" })).toBeTruthy();
  expect(screen.getByText(/2 members/)).toBeTruthy();
  expect(screen.getByText(/1 member$/)).toBeTruthy();
  expect(fetchSpy.mock.calls[0][0]).toBe("/api/users/sydney/projects");
});

test("shows an empty message when the user has no projects", async () => {
  mockFetch(200, { projects: [] });
  renderPage();

  submitUserId("newbie");

  expect(
    await screen.findByText(/don't belong to any projects yet/i)
  ).toBeTruthy();
});

test("shows the server error for an unknown user", async () => {
  mockFetch(404, { error: "User 'ghost' was not found." });
  renderPage();

  submitUserId("ghost");

  expect((await screen.findByRole("alert")).textContent).toBe(
    "User 'ghost' was not found."
  );
});

test("asks for a user ID instead of calling the server when blank", () => {
  const fetchSpy = mockFetch(200, { projects: [] });
  renderPage();

  submitUserId("   ");

  expect(screen.getByRole("alert").textContent).toBe(
    "Enter your user ID to see your projects."
  );
  expect(fetchSpy).not.toHaveBeenCalled();
});

test("reloads the list automatically for a remembered user", async () => {
  sessionStorage.setItem("dashboardUserId", "sydney");
  mockFetch(200, { projects: PROJECTS });
  renderPage();

  expect(await screen.findByRole("link", { name: "Robot Arm" })).toBeTruthy();
});

test("clicking a project card shows a snippet, clicking again hides it", async () => {
  mockFetch(200, { projects: PROJECTS });
  renderPage();
  submitUserId("sydney");

  await screen.findByRole("link", { name: "Robot Arm" });
  expect(screen.queryByText("Senior design prototype")).toBeNull();

  fireEvent.click(screen.getByText(/Project ID: robot-arm/));
  expect(screen.getByText("Senior design prototype")).toBeTruthy();
  expect(screen.getByText("sydney, alice")).toBeTruthy();
  expect(
    screen.getByRole("button", { name: "Hide details for Robot Arm" })
      .getAttribute("aria-expanded")
  ).toBe("true");

  fireEvent.click(screen.getByText(/Project ID: robot-arm/));
  expect(screen.queryByText("Senior design prototype")).toBeNull();
});

test("only one snippet is open at a time", async () => {
  mockFetch(200, { projects: PROJECTS });
  renderPage();
  submitUserId("sydney");
  await screen.findByRole("link", { name: "Robot Arm" });

  fireEvent.click(screen.getByRole("button", { name: "Show details for Robot Arm" }));
  fireEvent.click(screen.getByRole("button", { name: "Show details for Solo Project" }));

  expect(screen.queryByText("Senior design prototype")).toBeNull();
  expect(screen.getByText("No description yet.")).toBeTruthy();
});

test("clicking the project name goes to the project page", async () => {
  mockFetch(200, { projects: PROJECTS });
  render(
    <MemoryRouter
      initialEntries={["/dashboard"]}
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <Routes>
        <Route path="/dashboard" element={<HomePage />} />
        <Route path="/projects/:projectId" element={<p>Project page</p>} />
      </Routes>
    </MemoryRouter>
  );
  submitUserId("sydney");

  const nameLink = await screen.findByRole("link", { name: "Robot Arm" });
  expect(nameLink.getAttribute("href")).toBe("/projects/robot-arm");

  fireEvent.click(nameLink);
  expect(screen.getByText("Project page")).toBeTruthy();
});
