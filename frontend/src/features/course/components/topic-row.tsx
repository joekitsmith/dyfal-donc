import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";

import { ChevronIcon } from "@/components/icons/chevron-icon";
import { ListCard } from "@/components/list-card";
import { textStyle } from "@/theme/text-style";

import type { TopicProgress } from "../types";

import { describeTopic } from "../utils/describe-topic";
import { topicTitle } from "../utils/topic-title";

type TopicRowProps = {
  readonly onOpen: () => void;
  readonly topic: TopicProgress;
};

/** A topic that has been started, folded up to a single row. */
export function TopicRow({ onOpen, topic }: TopicRowProps) {
  return (
    <ListCard>
      <li>
        <ButtonBase
          aria-expanded="false"
          onClick={onOpen}
          sx={{
            alignItems: "center",
            display: "flex",
            gap: "12px",
            justifyContent: "space-between",
            minHeight: 52,
            py: "10px",
            textAlign: "left",
            width: "100%",
          }}
        >
          <Box component="span" sx={{ ...textStyle("label"), fontWeight: 600 }}>
            {topicTitle(topic.name)}
          </Box>
          <Box component="span" sx={{ alignItems: "center", color: "var(--dd-muted)", display: "flex", gap: "8px" }}>
            <Box component="span" sx={textStyle("body")}>
              {describeTopic(topic)}
            </Box>
            <ChevronIcon direction="down" size={20} />
          </Box>
        </ButtonBase>
      </li>
    </ListCard>
  );
}
