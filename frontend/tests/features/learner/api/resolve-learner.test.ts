import { HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { createApiClient } from "@/api/client";
import { readStoredLearnerId, storeLearnerId } from "@/features/learner/api/learner-storage";
import { createLearner, resolveLearner } from "@/features/learner/api/resolve-learner";

import { MemoryStorage } from "../../../mocks/memory-storage";
import { API_URL, apiHttp, server } from "../../../mocks/server";

const STORED_ID = "4f1d2c1e-6a0e-4a53-8f1b-0c6b6d5f6a11";
const CREATED_ID = "b2a8f0a4-1d3b-4c55-9a52-7d1f0f3c9e22";

// Created per test: the client keeps the fetch it finds, and msw replaces it when the server starts
function newClient() {
  return createApiClient(API_URL);
}

function creationHandler() {
  return apiHttp.post("/learners", () =>
    HttpResponse.json(
      { course_release: "release", created_at: "2026-01-01T00:00:00Z", id: CREATED_ID },
      { status: 201 },
    ),
  );
}

function progressHandler(status: number) {
  return apiHttp.get("/learners/{learner_id}/progress", () => new HttpResponse(null, { status }));
}

describe("createLearner", () => {
  it("creates a learner and remembers its id", async () => {
    server.use(creationHandler());
    const storage = new MemoryStorage();

    expect(await createLearner(newClient(), storage)).toBe(CREATED_ID);
    expect(readStoredLearnerId(storage)).toBe(CREATED_ID);
  });

  it("fails when the server refuses", async () => {
    server.use(apiHttp.post("/learners", () => new HttpResponse(null, { status: 500 })));

    await expect(createLearner(newClient(), new MemoryStorage())).rejects.toThrow(
      "Could not create a learner (status 500)",
    );
  });
});

describe("resolveLearner", () => {
  it("creates a learner on the first visit", async () => {
    server.use(creationHandler());

    expect(await resolveLearner(newClient(), new MemoryStorage())).toBe(CREATED_ID);
  });

  it("keeps a stored learner the server still knows", async () => {
    server.use(progressHandler(200));
    const storage = new MemoryStorage();
    storeLearnerId(storage, STORED_ID);

    expect(await resolveLearner(newClient(), storage)).toBe(STORED_ID);
  });

  it("creates a new learner when the stored one no longer exists", async () => {
    server.use(progressHandler(404), creationHandler());
    const storage = new MemoryStorage();
    storeLearnerId(storage, STORED_ID);

    expect(await resolveLearner(newClient(), storage)).toBe(CREATED_ID);
    expect(readStoredLearnerId(storage)).toBe(CREATED_ID);
  });

  it("does not replace the stored learner when the server is failing", async () => {
    server.use(progressHandler(500));
    const storage = new MemoryStorage();
    storeLearnerId(storage, STORED_ID);

    await expect(resolveLearner(newClient(), storage)).rejects.toThrow("Could not check the learner (status 500)");
    expect(readStoredLearnerId(storage)).toBe(STORED_ID);
  });
});
