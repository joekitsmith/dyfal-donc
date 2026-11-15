import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { audioUrl, ClipUnavailableError, fetchClip } from "@/api/clips";

import { API_URL, server } from "../mocks/server";

const AUDIO_PATH = "/exercises/i-can-go/audio/welsh";

describe("audioUrl", () => {
  it("puts the API's path under the proxy", () => {
    expect(audioUrl(AUDIO_PATH)).toBe("/api/exercises/i-can-go/audio/welsh");
  });

  it("takes another base", () => {
    expect(audioUrl(AUDIO_PATH, API_URL)).toBe(`${API_URL}${AUDIO_PATH}`);
  });
});

describe("fetchClip", () => {
  it("returns the audio and how long it took", async () => {
    server.use(
      http.get(`${API_URL}${AUDIO_PATH}`, () =>
        HttpResponse.arrayBuffer(new Uint8Array([1, 2, 3]).buffer, {
          headers: { "Content-Type": "audio/wav" },
        }),
      ),
    );

    const clip = await fetchClip(AUDIO_PATH, { baseUrl: API_URL });

    expect(clip.blob.size).toBe(3);
    expect(clip.blob.type).toBe("audio/wav");
    expect(clip.milliseconds).toBeGreaterThanOrEqual(0);
  });

  it("fails with the status when the speech service is down", async () => {
    server.use(http.get(`${API_URL}${AUDIO_PATH}`, () => new HttpResponse(null, { status: 503 })));

    await expect(fetchClip(AUDIO_PATH, { baseUrl: API_URL })).rejects.toMatchObject({
      message: "The audio is unavailable (status 503)",
      status: 503,
    });
    await expect(fetchClip(AUDIO_PATH, { baseUrl: API_URL })).rejects.toBeInstanceOf(ClipUnavailableError);
  });
});
