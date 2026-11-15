import Typography from "@mui/material/Typography";

import type { Item } from "../types";

type ItemListProps = {
  readonly items: readonly Item[];
  readonly title: string;
};

/** Words and patterns in both languages. It shows nothing for an empty list. */
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
            <Typography>
              {item.welsh} – {item.english}
            </Typography>
          </li>
        ))}
      </ul>
    </section>
  );
}
