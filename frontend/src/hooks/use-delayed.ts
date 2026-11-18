import { useEffect, useState } from "react";

/** Becomes true once the component has been there for a while, so something brief is never flashed. */
export function useDelayed(milliseconds: number): boolean {
  const [elapsed, setElapsed] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setElapsed(true);
    }, milliseconds);

    return () => {
      clearTimeout(timer);
    };
  }, [milliseconds]);

  return elapsed;
}
