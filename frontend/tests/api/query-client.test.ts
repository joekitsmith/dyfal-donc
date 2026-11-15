import { describe, expect, it } from "vitest";

import { createQueryClient } from "@/api/query-client";

describe("createQueryClient", () => {
  it("never refetches or retries by itself", () => {
    const { mutations, queries } = createQueryClient().getDefaultOptions();

    expect(queries).toMatchObject({
      refetchOnReconnect: false,
      refetchOnWindowFocus: false,
      retry: false,
      staleTime: Infinity,
    });
    expect(mutations).toMatchObject({ retry: false });
  });
});
