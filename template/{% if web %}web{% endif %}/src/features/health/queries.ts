import { queryOptions } from "@tanstack/react-query";
import { readHealth } from "../../api/client";

/** The API's health, as reported by `GET /api/health`. */
export const healthQuery = queryOptions({
  queryKey: ["health"],
  queryFn: async () => {
    // The generated client resolves on every status, so a failure is checked here.
    const { data, status } = await readHealth();
    if (status !== 200) {
      throw new Error(`Health check failed with HTTP ${status}`);
    }
    return data;
  },
});
