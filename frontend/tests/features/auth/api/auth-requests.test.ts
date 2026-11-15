import { HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { ApiError } from "@/api/api-error";
import { createApiClient } from "@/api/client";
import { resolveSession } from "@/features/auth/api/auth-requests";

import { API_URL, apiHttp, server } from "../../../mocks/server";

const USER_ID = "4f1d2c1e-6a0e-4a53-8f1b-0c6b6d5f6a11";

// Created per test: the client keeps the fetch it finds, and msw replaces it when the server starts
function newClient() {
  return createApiClient(API_URL);
}

describe("resolveSession", () => {
  it("returns whoever is signed in", async () => {
    server.use(
      apiHttp.get("/me", () => HttpResponse.json({ created_at: "2026-01-01T00:00:00Z", id: USER_ID, is_guest: true })),
    );

    expect(await resolveSession(newClient())).toEqual({ id: USER_ID, isGuest: true });
  });

  it("returns null when nobody is signed in", async () => {
    server.use(apiHttp.get("/me", () => new HttpResponse(null, { status: 401 })));

    expect(await resolveSession(newClient())).toBeNull();
  });

  it("fails when the server is failing, so nobody is wrongly signed out", async () => {
    server.use(apiHttp.get("/me", () => new HttpResponse(null, { status: 500 })));

    await expect(resolveSession(newClient())).rejects.toThrow(ApiError);
  });
});
