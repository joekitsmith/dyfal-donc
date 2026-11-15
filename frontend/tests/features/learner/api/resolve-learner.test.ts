import { HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { createApiClient } from "@/api/client";
import { resolveLearner, startOver } from "@/features/learner/api/resolve-learner";

import { API_URL, apiHttp, server } from "../../../mocks/server";

const CURRENT_ID = "4f1d2c1e-6a0e-4a53-8f1b-0c6b6d5f6a11";
const GUEST_ID = "b2a8f0a4-1d3b-4c55-9a52-7d1f0f3c9e22";

// Created per test: the client keeps the fetch it finds, and msw replaces it when the server starts
function newClient() {
  return createApiClient(API_URL);
}

function user(id: string) {
  return { created_at: "2026-01-01T00:00:00Z", id, is_guest: true };
}

function guestHandler() {
  return apiHttp.post("/auth/guest", () => HttpResponse.json(user(GUEST_ID)));
}

function meHandler(status: number) {
  return apiHttp.get("/me", () =>
    status === 200 ? HttpResponse.json(user(CURRENT_ID)) : new HttpResponse(null, { status }),
  );
}

describe("resolveLearner", () => {
  it("keeps whoever is signed in", async () => {
    server.use(meHandler(200));

    expect(await resolveLearner(newClient())).toBe(CURRENT_ID);
  });

  it("starts a guest when nobody is signed in", async () => {
    server.use(meHandler(401), guestHandler());

    expect(await resolveLearner(newClient())).toBe(GUEST_ID);
  });

  it("does not start a guest when the server is failing", async () => {
    server.use(meHandler(500));

    await expect(resolveLearner(newClient())).rejects.toThrow("Could not check who is signed in (status 500)");
  });
});

describe("startOver", () => {
  it("deletes the account, then starts a new guest", async () => {
    server.use(
      apiHttp.delete("/me", () => new HttpResponse(null, { status: 204 })),
      guestHandler(),
    );

    expect(await startOver(newClient())).toBe(GUEST_ID);
  });

  it("fails without starting a guest when the account cannot be deleted", async () => {
    server.use(apiHttp.delete("/me", () => new HttpResponse(null, { status: 500 })));

    await expect(startOver(newClient())).rejects.toThrow("Could not start over (status 500)");
  });
});
