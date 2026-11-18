import { NoticeCard } from "@/components/notice-card";

import type { PasskeyFailure } from "../types";

import { FAILURE_MESSAGES } from "../constants";

type PasskeyFailureNoticeProps = { readonly failure: PasskeyFailure };

export function PasskeyFailureNotice({ failure }: PasskeyFailureNoticeProps) {
  return <NoticeCard role="status">{FAILURE_MESSAGES[failure]}</NoticeCard>;
}
