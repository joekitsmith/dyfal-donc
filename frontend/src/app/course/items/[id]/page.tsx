import { ItemPage } from "@/features/course";

type PageProps = { readonly params: Promise<{ readonly id: string }> };

export default async function Page({ params }: PageProps) {
  const { id } = await params;

  return <ItemPage itemId={decodeURIComponent(id)} />;
}
