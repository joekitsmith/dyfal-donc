import { useState } from "react";

import type { components } from "@/api/schema";

import { useDisclosure } from "@/hooks/use-disclosure";

import type { ReportSource, ReportSubject } from "../types";

import { itemSubject, sentenceSubject } from "../utils/subjects";

type Item = Parameters<typeof itemSubject>[0];
type Sentence = components["schemas"]["SentenceResponse"];

/**
 * For a screen that reports one thing at a time: ``reportSentence`` and the like open the dialog
 * about it, and ``dialog`` is what to give the ``ReportDialog``.
 */
export function useReportDialog(source: ReportSource) {
  const { close, isOpen, open } = useDisclosure();
  const [subjects, setSubjects] = useState<readonly ReportSubject[]>([]);

  function reportAbout(about: readonly ReportSubject[]) {
    setSubjects(about);
    open();
  }

  return {
    dialog: { allowNone: false, onClose: close, open: isOpen, source, subjects },
    reportItem: (item: Item) => {
      reportAbout([itemSubject(item)]);
    },
    reportNothingInParticular: () => {
      reportAbout([]);
    },
    reportSentence: (sentence: Sentence) => {
      reportAbout([sentenceSubject(sentence)]);
    },
  };
}
