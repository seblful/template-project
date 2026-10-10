import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Testing Library unmounts between tests on its own only when the runner exposes
// globals. Vitest's are off, so imports stay explicit and the cleanup is wired here.
afterEach(cleanup);
