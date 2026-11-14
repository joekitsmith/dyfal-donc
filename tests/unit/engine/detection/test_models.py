from engine.detection import DetectedItem, Detection


class TestDetection:
    def test_item_ids_are_unique_and_in_order_of_first_appearance(self) -> None:
        items = tuple(
            DetectedItem(item_id=item_id, start=position, end=position + 1)
            for position, item_id in enumerate(["lex:b", "lex:a", "lex:b"])
        )
        assert Detection(items=items, problems=()).item_ids == ("lex:b", "lex:a")
