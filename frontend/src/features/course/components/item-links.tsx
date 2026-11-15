import Typography from "@mui/material/Typography";
import Link from "next/link";

import { courseItemPath } from "@/config/paths";

import type { CourseItem } from "../types";

type ItemLinksProps = {
  readonly items: readonly CourseItem[];
  readonly title: string;
};

/** Words or phrases in both languages, each linking to its page. It shows nothing for an empty list. */
export function ItemLinks({ items, title }: ItemLinksProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section aria-label={title}>
      <Typography component="h3" variant="h6">
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
