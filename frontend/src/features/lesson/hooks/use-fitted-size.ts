import { useEffect, useState } from "react";

import { SentenceFit } from "../utils/sentence-fit";

/** Refs that fit the English and Welsh sentences to their boxes. */
export function useFittedSize(): SentenceFit {
  const [fit] = useState(() => new SentenceFit());

  // A sentence measured before the font arrived has lines in the wrong places
  useEffect(() => {
    const refit = () => {
      fit.refit();
    };

    void document.fonts.ready.then(refit);
    document.fonts.addEventListener("loadingdone", refit);

    return () => {
      document.fonts.removeEventListener("loadingdone", refit);
    };
  }, [fit]);

  return fit;
}
