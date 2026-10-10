import { createRootRoute, Outlet } from "@tanstack/react-router";

export const Route = createRootRoute({ component: RootLayout });

/** The layout every page renders inside. */
function RootLayout() {
  return (
    <main className="mx-auto max-w-2xl space-y-6 p-8">
      <Outlet />
    </main>
  );
}
