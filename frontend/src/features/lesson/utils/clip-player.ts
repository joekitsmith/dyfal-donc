const SILENT_SAMPLE_RATE = 8000;
const SILENT_SAMPLES = 400;
const WAV_HEADER_BYTES = 44;

export type PlayOptions = {
  readonly onEnded: () => void;
  readonly onError: () => void;
  readonly onStarted?: () => void;
};

/**
 * One audio element for the whole lesson. Browsers only allow audio after a user gesture, and
 * an element that has played once stays allowed, so the lesson unlocks it on Start and then
 * plays every clip through it.
 */
export class ClipPlayer {
  #audio: HTMLAudioElement | undefined;
  #paused = false;
  #silentUrl: string | undefined;

  pause(): void {
    if (this.#audio === undefined || this.#audio.paused || this.#audio.ended) {
      return;
    }

    this.#paused = true;
    this.#audio.pause();
  }

  play(url: string, { onEnded, onError, onStarted }: PlayOptions): void {
    const audio = this.#element();

    this.stop();
    audio.onended = onEnded;
    audio.onplaying = onStarted ?? null;
    audio.src = url;
    audio.play().catch((error: unknown) => {
      if (!(error instanceof DOMException && error.name === "AbortError")) {
        onError();
      }
    });
  }

  resume(): void {
    if (!this.#paused) {
      return;
    }

    this.#paused = false;
    void this.#element().play();
  }

  stop(): void {
    this.#paused = false;

    if (this.#audio === undefined) {
      return;
    }

    this.#audio.onended = null;
    this.#audio.onplaying = null;
    this.#audio.pause();
  }

  /** Call this from the click that starts the lesson. */
  unlock(): void {
    this.#silentUrl ??= URL.createObjectURL(silentWav());
    this.#element().src = this.#silentUrl;
    this.#element()
      .play()
      .catch(() => undefined);
  }

  #element(): HTMLAudioElement {
    this.#audio ??= new Audio();

    return this.#audio;
  }
}

function silentWav(): Blob {
  const bytes = new Uint8Array(WAV_HEADER_BYTES + SILENT_SAMPLES);
  const view = new DataView(bytes.buffer);
  const writeText = (offset: number, text: string) => {
    for (let index = 0; index < text.length; index += 1) {
      view.setUint8(offset + index, text.charCodeAt(index));
    }
  };

  writeText(0, "RIFF");
  view.setUint32(4, bytes.length - 8, true);
  writeText(8, "WAVEfmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, SILENT_SAMPLE_RATE, true);
  view.setUint32(28, SILENT_SAMPLE_RATE, true);
  view.setUint16(32, 1, true);
  view.setUint16(34, 8, true);
  writeText(36, "data");
  view.setUint32(40, SILENT_SAMPLES, true);
  bytes.fill(128, WAV_HEADER_BYTES);

  return new Blob([bytes], { type: "audio/wav" });
}
