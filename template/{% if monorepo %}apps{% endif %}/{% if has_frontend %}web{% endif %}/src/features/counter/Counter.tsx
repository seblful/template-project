import { useState } from "react";

/** A button that counts its own clicks: the example feature, needing no backend. */
export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button
      type="button"
      className="rounded bg-slate-900 px-4 py-2 text-white"
      onClick={() => setCount((current) => current + 1)}
    >
      Count: {count}
    </button>
  );
}
