import { createRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

export const router = createRouter({ routeTree });

// Registers this router's routes globally, so every <Link to> and navigate() call is
// type-checked against them.
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
