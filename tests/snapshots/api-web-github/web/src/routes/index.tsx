import { createFileRoute } from "@tanstack/react-router";
import { HealthBadge } from "../features/health/HealthBadge";

export const Route = createFileRoute("/")({ component: HomePage });

/** The home page: a route only arranges features, it holds no logic of its own. */
function HomePage() {
  return (
    <>
      <h1 className="text-2xl font-semibold">demo-proj</h1>
      <HealthBadge />
    </>
  );
}
