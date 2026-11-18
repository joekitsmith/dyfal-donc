import { ListCard } from "@/components/list-card";
import { ListRow } from "@/components/list-row";
import { SubHeading } from "@/components/sub-heading";
import { courseItemPath } from "@/config/paths";

import type { Item } from "../types";

type ItemSectionProps = {
  readonly items: readonly Item[];
  readonly note?: string;
  readonly title: string;
};

/** Words and patterns under a sub-heading, each linking to its page. It shows nothing for an empty list. */
export function ItemSection({ items, note, title }: ItemSectionProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section aria-label={title}>
      <SubHeading level="h2" {...(note === undefined ? {} : { note })}>
        {title}
      </SubHeading>
      <ListCard>
        {items.map((item) => (
          <ListRow english={item.english} href={courseItemPath(item.id)} key={item.id} welsh={item.welsh} />
        ))}
      </ListCard>
    </section>
  );
}
