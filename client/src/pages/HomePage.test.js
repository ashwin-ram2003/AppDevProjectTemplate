import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
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
    hwSets: { HWSet1: 5 },
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

  expect(await screen.findByRole("heading", { name: "Robot Arm" })).toBeTruthy();
  expect(screen.getByRole("heading", { name: "Solo Project" })).toBeTruthy();
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

  expect(await screen.findByRole("heading", { name: "Robot Arm" })).toBeTruthy();
});

test("shows project details directly on the dashboard", async () => {
  mockFetch(200, { projects: PROJECTS });
  renderPage();
  submitUserId("sydney");

  await screen.findByRole("heading", { name: "Robot Arm" });
  expect(screen.getByText("Senior design prototype")).toBeTruthy();
  expect(screen.getByText("sydney, alice")).toBeTruthy();
  expect(screen.getByText("No description yet.")).toBeTruthy();
  expect(screen.queryByText(/Open project/)).toBeNull();
});

test("checks hardware out directly from a project card", async () => {
  mockFetch(200, { projects: PROJECTS });
  renderPage();
  submitUserId("sydney");

  const project = (await screen.findByRole("heading", { name: "Robot Arm" })).closest("li");
  const row = within(project).getByLabelText("HWSet1 controls");
  fireEvent.change(within(row).getByLabelText(/quantity for hwset1/i), {
    target: { value: "3" },
  });
  fireEvent.click(within(row).getByRole("button", { name: "Check Out" }));

  expect(within(row).getByText("Available: 97 / 100")).toBeTruthy();
  expect(within(row).getByRole("status").textContent).toBe("Checked out 3 unit(s).");
});

test("prevents checkout when hardware stock is insufficient", async () => {
  mockFetch(200, { projects: PROJECTS });
  renderPage();
  submitUserId("sydney");

  const project = (await screen.findByRole("heading", { name: "Robot Arm" })).closest("li");
  const row = within(project).getByLabelText("HWSet1 controls");
  fireEvent.change(within(row).getByLabelText(/quantity for hwset1/i), {
    target: { value: "101" },
  });
  fireEvent.click(within(row).getByRole("button", { name: "Check Out" }));

  expect(within(row).getByRole("alert").textContent).toBe("Only 100 unit(s) are available.");
  expect(within(row).getByText("Available: 100 / 100")).toBeTruthy();
});

test("checks hardware in and prevents returning too much", async () => {
  mockFetch(200, { projects: PROJECTS });
  renderPage();
  submitUserId("sydney");

  const project = (await screen.findByRole("heading", { name: "Robot Arm" })).closest("li");
  const row = within(project).getByLabelText("HWSet1 controls");
  const quantity = within(row).getByLabelText(/quantity for hwset1/i);

  fireEvent.change(quantity, { target: { value: "6" } });
  fireEvent.click(within(row).getByRole("button", { name: "Check In" }));
  expect(within(row).getByRole("alert").textContent).toBe(
    "This project can only check in 5 unit(s)."
  );

  fireEvent.change(quantity, { target: { value: "2" } });
  jest.useFakeTimers();
  fireEvent.click(within(row).getByRole("button", { name: "Check In" }));
  expect(within(row).getByText("Available: 100 / 100")).toBeTruthy();
  expect(within(row).getByRole("status").textContent).toBe("Checked in 2 unit(s).");

  act(() => jest.advanceTimersByTime(2000));
  expect(within(row).queryByRole("status")).toBeNull();
  jest.useRealTimers();
});

test("shows already full when a project has no hardware to check in", async () => {
  mockFetch(200, { projects: PROJECTS });
  renderPage();
  submitUserId("sydney");

  const project = (await screen.findByRole("heading", { name: "Solo Project" })).closest("li");
  const row = within(project).getByLabelText("HWSet1 controls");
  fireEvent.click(within(row).getByRole("button", { name: "Check In" }));

  expect(within(row).getByRole("alert").textContent).toBe("HWSet1 is already full.");
});

test("shows all other projects and joins one from the dashboard", async () => {
  const availableProject = {
    projectName: "Drone Team",
    projectId: "drone-team",
    description: "Autonomous drone project",
    hwSets: {},
    users: ["alice"],
  };
  const response = (body) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(body),
  });
  const fetchSpy = jest.spyOn(global, "fetch")
    .mockImplementationOnce(() => response({ projects: PROJECTS }))
    .mockImplementationOnce(() => response({ projects: [...PROJECTS, availableProject] }))
    .mockImplementationOnce(() => response({
      ...availableProject,
      users: ["alice", "sydney"],
    }));

  renderPage();
  submitUserId("sydney");

  const availableList = await screen.findByRole("list", { name: "Available projects" });
  const card = within(availableList).getByRole("heading", { name: "Drone Team" }).closest("li");
  expect(
    within(card).getAllByRole("button", { name: "Check Out" })
      .every((button) => button.disabled)
  ).toBe(true);

  fireEvent.click(within(card).getByRole("button", { name: "Join" }));

  await waitFor(() => {
    expect(screen.queryByRole("list", { name: "Available projects" })).toBeNull();
  });
  expect(
    within(screen.getByRole("list", { name: "My projects" }))
      .getByRole("heading", { name: "Drone Team" })
  ).toBeTruthy();
  expect(fetchSpy.mock.calls[2][0]).toBe("/api/projects/drone-team/users");
});
