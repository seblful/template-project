import { useQuery } from "@tanstack/react-query";
import { healthQuery } from "./queries";

/** Whether the API answers, and which version it runs: the example of a typed call. */
export function HealthBadge() {
  const { data, isPending, isError } = useQuery(healthQuery);

  if (isPending) {
    return <p className="text-slate-500">Checking the API…</p>;
  }
  if (isError) {
    return <p className="text-red-700">API unreachable</p>;
  }
  return (
    <p className="text-green-700">
      API {data.status}, version {data.version}
    </p>
  );
}
