import Box from "@mui/material/Box";

import { ListCard } from "@/components/list-card";
import { ListRow } from "@/components/list-row";
import { courseItemPath } from "@/config/paths";
import { textStyle } from "@/theme/text-style";

import type { SearchResult } from "../types";

import { opener } from "../utils/opener";
import { topicTitle } from "../utils/topic-title";

type SearchResultsProps = {
  /** Opens a word or phrase in place of going to its page. */
  readonly onOpenItem?: (itemId: string) => void;
  readonly results: readonly SearchResult[];
};

export function SearchResults({ onOpenItem, results }: SearchResultsProps) {
  if (results.length === 0) {
    return (
      <Box sx={{ ...textStyle("caption"), color: "var(--dd-muted)", mt: "28px" }}>
        Nothing you&apos;ve met matches that.
      </Box>
    );
  }

  return (
    <Box aria-label="Search results" component="section" sx={{ mt: "20px" }}>
      <ListCard>
        {results.map(({ item, topic }) => (
          <ListRow
            english={item.english}
            href={courseItemPath(item.id)}
            key={item.id}
            onOpen={opener(onOpenItem, item.id)}
            secondLine={{ size: "small", text: topicTitle(topic) }}
            welsh={item.welsh}
          />
        ))}
      </ListCard>
    </Box>
  );
}
