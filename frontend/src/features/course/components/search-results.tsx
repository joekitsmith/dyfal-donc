import Typography from "@mui/material/Typography";
import Link from "next/link";

import { courseItemPath } from "@/config/paths";

import type { SearchResult } from "../types";

type SearchResultsProps = { readonly results: readonly SearchResult[] };

export function SearchResults({ results }: SearchResultsProps) {
  if (results.length === 0) {
    return <Typography>Nothing you have met matches that</Typography>;
  }

  return (
    <ul aria-label="Search results">
      {results.map(({ item, topic }) => (
        <li key={item.id}>
          <Link href={courseItemPath(item.id)}>
            {item.welsh} – {item.english}
          </Link>
          <Typography color="text.secondary" component="span">
            {" "}
            ({topic})
          </Typography>
        </li>
      ))}
    </ul>
  );
}
