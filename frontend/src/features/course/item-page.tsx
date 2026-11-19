"use client";

import { PageColumn } from "@/components/page-column";
import { ROUTES } from "@/config/paths";

import { ItemView } from "./components/item-view";

type ItemPageProps = { readonly itemId: string };

export function ItemPage({ itemId }: ItemPageProps) {
  return (
    <PageColumn>
      <ItemView back={{ href: ROUTES.course }} itemId={itemId} />
    </PageColumn>
  );
}
