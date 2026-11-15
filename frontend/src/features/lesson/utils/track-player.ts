import { POSITION_POLL_MILLISECONDS, SILENT_SAMPLE_RATE, SILENT_SAMPLES } from "../constants";
import { encodeWav } from "./wav";

export type TrackListeners = {
  /** Playback was refused or failed. */
  readonly onError: () => void;
  /** Something other than the lesson paused the audio: the lock screen, headphones, a call or an alarm. */
  readonly onPaused: () => void;
  /** Something other than the lesson resumed it. */
  readonly onPlayed: () => void;
  /** The position may have moved. This runs from `timeupdate` and a timer, because either may be throttled. */
  readonly onPosition: () => void;
};

/**
 * One audio element for the whole lesson, which plays one track per exercise. Browsers only allow
 * audio after a user gesture, and an element that has played once stays allowed, so the lesson
 * unlocks it on Start and then swaps each exercise's track into it. The element is never left
 * idle while the lesson runs, which is what keeps playing with the screen locked.
 */
export class TrackPlayer {
  #audio: HTMLAudioElement | undefined;
  #held = false;
  #listeners: TrackListeners | undefined;
  #ownPause = false;
  #url: string | undefined;

  /** Seconds into the current track. */
  get position(): number {
    return this.#audio?.currentTime ?? 0;
  }

  pause(): void {
    const audio = this.#audio;

    if (audio === undefined || audio.paused || audio.ended) {
      return;
    }

    this.#ownPause = true;
    audio.pause();
  }

  /** Plays the track from its start, in place of the one before, whose address is then released. */
  play(url: string): void {
    const audio = this.#element();
    const previous = this.#url;

    this.#held = false;
    this.#url = url;
    audio.src = url;
    this.#start(audio);

    if (previous !== undefined) {
      URL.revokeObjectURL(previous);
    }
  }

  /** Continues what `pause` held, or what something else paused. */
  resume(): void {
    if (!this.#held || this.#audio === undefined || this.#audio.ended) {
      return;
    }

    this.#held = false;
    this.#start(this.#audio);
  }

  seekToStart(): void {
    this.#element().currentTime = 0;
  }

  stop(): void {
    this.#held = false;

    if (this.#audio === undefined) {
      return;
    }

    if (!this.#audio.paused) {
      this.#ownPause = true;
      this.#audio.pause();
    }

    if (this.#url !== undefined) {
      URL.revokeObjectURL(this.#url);
      this.#url = undefined;
    }
  }

  /** Reports what happens to the audio until the returned function is called. */
  subscribe(listeners: TrackListeners): () => void {
    const audio = this.#element();
    const poll = setInterval(listeners.onPosition, POSITION_POLL_MILLISECONDS);
    const onPause = () => {
      if (this.#ownPause) {
        this.#ownPause = false;
        this.#held = true;

        return;
      }

      // The element also pauses when a track reaches its end, which nothing needs to hear about
      if (!audio.ended) {
        this.#held = true;
        listeners.onPaused();
      }
    };
    const onPlay = () => {
      this.#held = false;
      listeners.onPlayed();
    };

    this.#listeners = listeners;
    audio.addEventListener("timeupdate", listeners.onPosition);
    audio.addEventListener("pause", onPause);
    audio.addEventListener("play", onPlay);

    return () => {
      clearInterval(poll);
      audio.removeEventListener("timeupdate", listeners.onPosition);
      audio.removeEventListener("pause", onPause);
      audio.removeEventListener("play", onPlay);
      this.#listeners = undefined;
    };
  }

  /** Call this from the click that starts the lesson. */
  unlock(): void {
    const audio = this.#element();

    this.#url = URL.createObjectURL(encodeWav(new Int16Array(SILENT_SAMPLES), SILENT_SAMPLE_RATE));
    audio.src = this.#url;
    this.#start(audio);
  }

  #element(): HTMLAudioElement {
    this.#audio ??= new Audio();

    return this.#audio;
  }

  #start(audio: HTMLAudioElement): void {
    audio.play().catch((error: unknown) => {
      // Loading another track while this one was starting is not a failure
      if (!(error instanceof DOMException && error.name === "AbortError")) {
        this.#listeners?.onError();
      }
    });
  }
}
