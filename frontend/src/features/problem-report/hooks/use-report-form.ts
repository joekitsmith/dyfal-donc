import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, useWatch } from "react-hook-form";

import type { ReportFormValues, ReportSource, ReportSubject, ReportValues } from "../types";

import { useSendProblemReport } from "../api/use-send-problem-report";
import { NO_SUBJECT } from "../constants";
import { reportSchema } from "../utils/report-schema";
import { sendFailureMessage } from "../utils/send-failure-message";
import { toRequestBody } from "../utils/to-request-body";

/**
 * The report form. The first subject is chosen to begin with, and a choice is only worth showing when
 * there is more than one thing it could be about: with one sentence offered, that is the sentence.
 */
export function useReportForm({
  allowNone,
  source,
  subjects,
}: {
  readonly allowNone: boolean;
  readonly source: ReportSource;
  readonly subjects: readonly ReportSubject[];
}) {
  const { control, formState, handleSubmit, register } = useForm<ReportFormValues, unknown, ReportValues>({
    defaultValues: { category: "", description: "", subjectId: subjects[0]?.id ?? NO_SUBJECT },
    resolver: zodResolver(reportSchema),
  });
  const { error, isPending, isSuccess, mutate } = useSendProblemReport();
  const description = useWatch({ control, name: "description" });
  const choose = subjects.length > 1 || (subjects.length === 1 && allowNone);

  return {
    control,
    description: { length: description.length },
    errors: {
      category: formState.errors.category?.message,
      description: formState.errors.description?.message,
    },
    failure: error === null ? null : sendFailureMessage(error),
    isSending: isPending,
    onSubmit: handleSubmit((values) => {
      mutate(
        toRequestBody(
          source,
          subjects.find((subject) => subject.id === values.subjectId),
          values,
        ),
      );
    }),
    register,
    sent: isSuccess,
    subject: {
      choices: choose ? subjects : [],
      fixed: choose ? undefined : subjects[0],
      showNone: choose && allowNone,
    },
  };
}
