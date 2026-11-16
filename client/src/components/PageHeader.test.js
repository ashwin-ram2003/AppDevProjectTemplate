import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import PageHeader from "./PageHeader";

// PageHeader renders a <Link>, so it needs a router around it.
function renderHeader(props) {
  return render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <PageHeader {...props} />
    </MemoryRouter>
  );
}

test("shows the title and a link back to the dashboard by default", () => {
  renderHeader({ title: "Create Project" });

  expect(screen.getByRole("heading", { name: "Create Project" })).toBeTruthy();
  const backLink = screen.getByRole("link", { name: "Back to Dashboard" });
  expect(backLink.getAttribute("href")).toBe("/dashboard");
});

test("shows the subtitle under the title when given", () => {
  renderHeader({ title: "Robot Arm", subtitle: "Project ID: robot-arm" });

  expect(screen.getByRole("heading", { name: "Robot Arm" })).toBeTruthy();
  expect(screen.getByText("Project ID: robot-arm")).toBeTruthy();
});

test("custom actions replace the default back link", () => {
  renderHeader({
    title: "My Dashboard",
    actions: <button type="button">Sign Out</button>,
  });

  expect(screen.getByRole("button", { name: "Sign Out" })).toBeTruthy();
  expect(screen.queryByRole("link", { name: "Back to Dashboard" })).toBeNull();
});
