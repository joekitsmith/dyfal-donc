import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ClipUnavailableError, fetchClip } from "@/api/clips";
import { ClipButton } from "@/features/smoke/components/clip-button";

vi.mock("@/api/clips", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api/clips")>()),
  fetchClip: vi.fn(),
}));

const play = vi.fn<() => Promise<void>>();

class FakeAudio {
  play = play;
  addEventListener = vi.fn();
}

describe("ClipButton", () => {
  beforeEach(() => {
    vi.stubGlobal("Audio", FakeAudio);
    URL.createObjectURL = vi.fn(() => "blob:clip");
    URL.revokeObjectURL = vi.fn();
    play.mockResolvedValue(undefined);
    vi.spyOn(console, "info").mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    play.mockReset();
  });

  it("plays the clip and shows how long it took to fetch", async () => {
    vi.mocked(fetchClip).mockResolvedValue({ blob: new Blob(["x"]), milliseconds: 120 });

    render(<ClipButton label="Welsh" path="/exercises/x/audio/welsh" />);
    await userEvent.click(screen.getByRole("button", { name: "Welsh" }));

    expect(fetchClip).toHaveBeenCalledWith("/exercises/x/audio/welsh");
    expect(play).toHaveBeenCalledOnce();
    expect(await screen.findByText("120 ms")).toBeInTheDocument();
  });

  it("says so when the audio is unavailable", async () => {
    vi.mocked(fetchClip).mockRejectedValue(new ClipUnavailableError(503));

    render(<ClipButton label="Welsh" path="/exercises/x/audio/welsh" />);
    await userEvent.click(screen.getByRole("button", { name: "Welsh" }));

    expect(await screen.findByText("The audio is unavailable (status 503)")).toBeInTheDocument();
    expect(play).not.toHaveBeenCalled();
  });
});
