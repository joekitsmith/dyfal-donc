const STORAGE_KEY = "headphone-hint";
const SHOWN_FOR_VISITS = 5;

type HintState = { readonly used: boolean; readonly visits: number };

const listeners = new Set<() => void>();

export function getServerSnapshot(): null {
  return null;
}

export function getSnapshot(): null | string {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

/** Shown for the first few visits, until a headphone or lock screen control has been used. Without storage it always shows. */
export function isHintVisible(snapshot: null | string): boolean {
  const { used, visits } = parse(snapshot);

  return !used && visits <= SHOWN_FOR_VISITS;
}

export function recordUse(): void {
  update((state) => ({ ...state, used: true }));
}

export function recordVisit(): void {
  update((state) => ({ ...state, visits: state.visits + 1 }));
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  window.addEventListener("storage", listener);

  return () => {
    listeners.delete(listener);
    window.removeEventListener("storage", listener);
  };
}

function parse(snapshot: null | string): HintState {
  const fresh = { used: false, visits: 0 };

  if (snapshot === null) {
    return fresh;
  }

  try {
    const parsed: unknown = JSON.parse(snapshot);

    if (
      typeof parsed === "object" &&
      parsed !== null &&
      "used" in parsed &&
      typeof parsed.used === "boolean" &&
      "visits" in parsed &&
      typeof parsed.visits === "number"
    ) {
      return { used: parsed.used, visits: parsed.visits };
    }
  } catch {
    // Something else wrote here, so start again
  }

  return fresh;
}

function update(change: (state: HintState) => HintState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(change(parse(getSnapshot()))));
  } catch {
    // Without storage the hint simply keeps showing
  }

  for (const listener of listeners) {
    listener();
  }
}
