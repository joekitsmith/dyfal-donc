import Typography from "@mui/material/Typography";
import Link from "next/link";

import { courseItemPath } from "@/config/paths";

import type { Item } from "../types";

type ItemListProps = {
  readonly items: readonly Item[];
  readonly title: string;
};

/** Words and patterns in both languages, each linking to its page. It shows nothing for an empty list. */
export function ItemList({ items, title }: ItemListProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section aria-label={title}>
      <Typography component="h2" variant="h6">
        {title}
      </Typography>
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <Link href={courseItemPath(item.id)}>
              {item.welsh} – {item.english}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
