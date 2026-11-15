import { describe, expect, it } from "vitest";

import { encodeWavBytes, parseWav } from "@/features/lesson/utils/wav";

describe("wav", () => {
  it("writes a mono 16-bit header and reads the samples back", () => {
    const samples = new Int16Array([0, 1, -1, 32_767, -32_768]);
    const bytes = encodeWavBytes(samples, 22_050);
    const view = new DataView(bytes.buffer);

    expect(new TextDecoder().decode(bytes.slice(0, 4))).toBe("RIFF");
    expect(view.getUint32(4, true)).toBe(bytes.length - 8);
    expect(view.getUint32(24, true)).toBe(22_050);
    expect(view.getUint32(40, true)).toBe(samples.length * 2);
    expect(parseWav(bytes.buffer)).toEqual({ pcm: samples, sampleRate: 22_050 });
  });

  it("skips chunks it does not need", () => {
    const wav = encodeWavBytes(new Int16Array([5, 6]), 8000);
    const extra = new Uint8Array([...new TextEncoder().encode("LIST"), 4, 0, 0, 0, 1, 2, 3, 4]);
    const bytes = new Uint8Array([...wav.slice(0, 36), ...extra, ...wav.slice(36)]);

    expect(parseWav(bytes.buffer).pcm).toEqual(new Int16Array([5, 6]));
  });

  it("refuses what is not a mono 16-bit WAV file", () => {
    const stereo = encodeWavBytes(new Int16Array(2), 8000);

    new DataView(stereo.buffer).setUint16(22, 2, true);

    expect(() => parseWav(new TextEncoder().encode("not audio at all").buffer)).toThrow("not a WAV file");
    expect(() => parseWav(stereo.buffer)).toThrow("not mono 16-bit PCM");
  });
});
