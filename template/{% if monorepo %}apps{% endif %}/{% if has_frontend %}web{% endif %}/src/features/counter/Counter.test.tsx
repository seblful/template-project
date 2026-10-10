import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test } from "vitest";
import { Counter } from "./Counter";

test("each click increments the count", async () => {
  const user = userEvent.setup();
  render(<Counter />);

  await user.click(screen.getByRole("button", { name: "Count: 0" }));

  expect(screen.getByRole("button", { name: "Count: 1" })).toBeDefined();
});
