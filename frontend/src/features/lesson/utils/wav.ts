const HEADER_BYTES = 44;
const BYTES_PER_SAMPLE = 2;
const BITS_PER_SAMPLE = 16;
const PCM_ENCODING = 1;
const MONO = 1;
const CHUNK_HEADER_BYTES = 8;
const RIFF_HEADER_BYTES = 12;
const FORMAT_CHUNK_BYTES = 16;

export type WavClip = {
  /** Mono, 16-bit samples. */
  readonly pcm: Int16Array;
  readonly sampleRate: number;
};

/** The samples of a mono 16-bit PCM WAV file, which is what the speech service makes. Anything else is refused. */
export function parseWav(buffer: ArrayBuffer): WavClip {
  const view = new DataView(buffer);
  const text = (offset: number, length: number) => new TextDecoder().decode(new Uint8Array(buffer, offset, length));

  if (buffer.byteLength < RIFF_HEADER_BYTES || text(0, 4) !== "RIFF" || text(8, 4) !== "WAVE") {
    throw new Error("The audio is not a WAV file");
  }

  let format: undefined | { bits: number; channels: number; encoding: number; sampleRate: number };
  let offset = RIFF_HEADER_BYTES;

  while (offset + CHUNK_HEADER_BYTES <= buffer.byteLength) {
    const id = text(offset, 4);
    const size = view.getUint32(offset + 4, true);
    const body = offset + CHUNK_HEADER_BYTES;

    if (id === "fmt ") {
      format = {
        bits: view.getUint16(body + 14, true),
        channels: view.getUint16(body + 2, true),
        encoding: view.getUint16(body, true),
        sampleRate: view.getUint32(body + 4, true),
      };
    } else if (id === "data") {
      if (format?.encoding !== PCM_ENCODING || format.channels !== MONO || format.bits !== BITS_PER_SAMPLE) {
        throw new Error("The audio is not mono 16-bit PCM");
      }

      const length = Math.min(size, buffer.byteLength - body);

      // A copy, because the samples must start at an even offset
      return {
        pcm: new Int16Array(buffer.slice(body, body + length - (length % BYTES_PER_SAMPLE))),
        sampleRate: format.sampleRate,
      };
    }

    offset = body + size + (size % 2);
  }

  throw new Error("The audio has no samples");
}

export function encodeWav(pcm: Int16Array, sampleRate: number): Blob {
  return new Blob([encodeWavBytes(pcm, sampleRate)], { type: "audio/wav" });
}

export function encodeWavBytes(pcm: Int16Array, sampleRate: number): Uint8Array<ArrayBuffer> {
  const bytes = new Uint8Array(HEADER_BYTES + pcm.length * BYTES_PER_SAMPLE);
  const view = new DataView(bytes.buffer);
  const write = (offset: number, text: string) => {
    for (let index = 0; index < text.length; index += 1) {
      view.setUint8(offset + index, text.charCodeAt(index));
    }
  };

  write(0, "RIFF");
  view.setUint32(4, bytes.length - CHUNK_HEADER_BYTES, true);
  write(8, "WAVEfmt ");
  view.setUint32(16, FORMAT_CHUNK_BYTES, true);
  view.setUint16(20, PCM_ENCODING, true);
  view.setUint16(22, MONO, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * BYTES_PER_SAMPLE, true);
  view.setUint16(32, BYTES_PER_SAMPLE, true);
  view.setUint16(34, BITS_PER_SAMPLE, true);
  write(36, "data");
  view.setUint32(40, pcm.length * BYTES_PER_SAMPLE, true);

  // Through a view, so the samples are written little-endian on every machine
  pcm.forEach((sample, index) => {
    view.setInt16(HEADER_BYTES + index * BYTES_PER_SAMPLE, sample, true);
  });

  return bytes;
}
