"use client";

import { FailureScreen } from "@/components/failure-screen";

type ErrorProps = { readonly retry: () => void };

export default function Error({ retry }: ErrorProps) {
  return <FailureScreen onRetry={retry} />;
}
