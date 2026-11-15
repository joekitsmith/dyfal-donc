import { SummaryPage } from "@/features/learning-session";

type PageProps = { readonly params: Promise<{ readonly id: string }> };

export default async function Page({ params }: PageProps) {
  const { id } = await params;

  return <SummaryPage sessionId={Number(id)} />;
}
