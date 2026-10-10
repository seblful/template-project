import { createRouter } from "@tanstack/react-router";
import { indexRoute } from "./routes/index";
import { rootRoute } from "./routes/root";

// Routes are declared in code rather than discovered from files: file-based routing
// generates a route tree that every build rewrites, which a check would have to
// ignore or regenerate first.
const routeTree = rootRoute.addChildren([indexRoute]);

export const router = createRouter({ routeTree });

// Registers this router's routes globally, so every <Link to> and navigate() call is
// type-checked against them.
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
