import { describe, expect, it, vi } from "vitest";

import {
  lessonMetadata,
  type MediaSessionLike,
  registerMediaSession,
  reportPosition,
} from "@/features/lesson/utils/media-session";

function fakeSession() {
  const handlers = new Map<string, (() => void) | null>();
  const session: MediaSessionLike = {
    metadata: null,
    playbackState: "none",
    setActionHandler: (action, handler) => {
      handlers.set(action, handler as (() => void) | null);
    },
    setPositionState: vi.fn(),
  };

  return { handlers, session };
}

const HANDLERS = { missed: vi.fn(), pause: vi.fn(), play: vi.fn(), replay: vi.fn() };

describe("registerMediaSession", () => {
  it("maps previous to replay and next to missed, and leaves seeking unset", () => {
    const { handlers, session } = fakeSession();

    registerMediaSession(session, HANDLERS);
    handlers.get("previoustrack")?.();
    handlers.get("nexttrack")?.();
    handlers.get("play")?.();
    handlers.get("pause")?.();

    expect(HANDLERS.replay).toHaveBeenCalledOnce();
    expect(HANDLERS.missed).toHaveBeenCalledOnce();
    expect(HANDLERS.play).toHaveBeenCalledOnce();
    expect(HANDLERS.pause).toHaveBeenCalledOnce();
    expect(handlers.get("seekbackward")).toBeNull();
    expect(handlers.get("seekforward")).toBeNull();
    expect(handlers.get("seekto")).toBeNull();
  });

  it("takes everything away when the lesson ends, and survives an action the browser does not know", () => {
    const { handlers, session } = fakeSession();
    const { setActionHandler } = session;

    session.setActionHandler = (action, handler) => {
      if (action === "seekto") {
        throw new TypeError("Unsupported");
      }

      setActionHandler(action, handler);
    };

    const cleanup = registerMediaSession(session, HANDLERS);

    session.metadata = { title: "I can go" } as MediaMetadata;
    session.playbackState = "playing";
    cleanup();

    expect([...handlers.values()].every((handler) => handler === null)).toBe(true);
    expect(session.metadata).toBeNull();
    expect(session.playbackState).toBe("none");
  });
});

describe("lessonMetadata", () => {
  it("has the English as the title and nothing of the Welsh", () => {
    expect(lessonMetadata("I can go")).toMatchObject({ artist: "dyfal-donc", title: "I can go" });
  });

  it("is the name of the app until there is an exercise", () => {
    expect(lessonMetadata(null)).toMatchObject({ artist: "dyfal-donc", title: "dyfal-donc" });
  });

  it("lists the larger artwork first", () => {
    expect(lessonMetadata(null).artwork?.[0]).toMatchObject({ sizes: "512x512" });
  });
});

describe("reportPosition", () => {
  it("reports the position against the end of the exercise, not the end of the tail", () => {
    const { session } = fakeSession();

    reportPosition(session, 4, 17.5);
    reportPosition(session, 20, 17.5);

    expect(session.setPositionState).toHaveBeenNthCalledWith(1, { duration: 17.5, playbackRate: 1, position: 4 });
    expect(session.setPositionState).toHaveBeenNthCalledWith(2, { duration: 17.5, playbackRate: 1, position: 17.5 });
  });

  it("carries on when the browser refuses", () => {
    const { session } = fakeSession();

    vi.mocked(session.setPositionState).mockImplementation(() => {
      throw new TypeError("Invalid");
    });

    expect(() => {
      reportPosition(session, 1, 0);
    }).not.toThrow();
  });
});
