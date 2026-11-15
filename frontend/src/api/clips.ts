import { API_BASE_PATH } from "@/config/paths";

export type Clip = {
  readonly blob: Blob;
  readonly milliseconds: number;
};

export class ClipUnavailableError extends Error {
  readonly status: number;

  constructor(status: number) {
    super(`The audio is unavailable (status ${status})`);
    this.status = status;
  }
}

/** The audio links in an exercise are paths on the API, which this app reaches under its proxy. */
export function audioUrl(path: string, baseUrl: string = API_BASE_PATH): string {
  return `${baseUrl}${path}`;
}

export type FetchClipOptions = {
  readonly baseUrl?: string;
  readonly signal?: AbortSignal;
};

export async function fetchClip(
  path: string,
  { baseUrl = API_BASE_PATH, signal }: FetchClipOptions = {},
): Promise<Clip> {
  const started = performance.now();
  const response = await fetch(audioUrl(path, baseUrl), signal === undefined ? {} : { signal });

  if (!response.ok) {
    throw new ClipUnavailableError(response.status);
  }

  const blob = await response.blob();

  return { blob, milliseconds: performance.now() - started };
}
