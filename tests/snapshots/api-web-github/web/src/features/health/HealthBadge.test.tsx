import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, expect, test, vi } from "vitest";
import { HealthBadge } from "./HealthBadge";

afterEach(() => {
  vi.unstubAllGlobals();
});

/** Render inside a fresh query cache, with retries off so failures show at once. */
function renderWithQueries(ui: ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>{ui}</QueryClientProvider>,
  );
}

test("shows the version the API reports", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => Response.json({ status: "ok", version: "1.2.3" })),
  );

  renderWithQueries(<HealthBadge />);

  expect(await screen.findByText("API ok, version 1.2.3")).toBeDefined();
});

test("says so when the API does not answer", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(null, { status: 503 })),
  );

  renderWithQueries(<HealthBadge />);

  expect(await screen.findByText("API unreachable")).toBeDefined();
});
