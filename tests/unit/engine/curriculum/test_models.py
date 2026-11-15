import pytest

from engine.curriculum import (
    DEFAULT_TOPIC,
    Curriculum,
    CurriculumError,
    Gender,
    Lexeme,
    PartOfSpeech,
    Pattern,
    Topic,
)


def build(items: list[Lexeme], order: list[str]) -> Curriculum:
    return Curriculum(items=tuple(items), order=tuple(order))


def noun(
    id_: str,
    welsh: str,
    forms: tuple[str, ...] = (),
    homographs: tuple[str, ...] = (),
) -> Lexeme:
    return Lexeme(
        id=f"lex:{id_}",
        welsh=welsh,
        english=id_,
        part_of_speech=PartOfSpeech.NOUN,
        forms=forms,
        homographs=homographs,
    )


def L(id_: str, *prerequisites: str) -> Lexeme:
    return Lexeme(
        id=f"lex:{id_}",
        welsh=id_,
        english=id_,
        part_of_speech=PartOfSpeech.VERB,
        prerequisites=prerequisites,
    )


class TestModels:
    def test_gender_requires_noun(self) -> None:
        with pytest.raises(CurriculumError, match="Gender is only valid for nouns"):
            Lexeme(
                id="lex:x",
                welsh="x",
                english="x",
                part_of_speech=PartOfSpeech.VERB,
                gender=Gender.MASCULINE,
            )

    def test_noun_with_gender(self) -> None:
        assert (
            Lexeme(
                id="lex:x",
                welsh="x",
                english="x",
                part_of_speech=PartOfSpeech.NOUN,
                gender=Gender.FEMININE,
            ).gender
            == Gender.FEMININE
        )

    def test_id_prefix_enforced(self) -> None:
        with pytest.raises(CurriculumError, match="Invalid id 'pat:x'"):
            Lexeme(id="pat:x", welsh="x", english="x", part_of_speech=PartOfSpeech.NOUN)

    def test_pattern_slots_must_match_template(self) -> None:
        with pytest.raises(CurriculumError, match="do not match declared slot"):
            Pattern(
                id="pat:x", template="Dw i'n [VERB]", english="I am [VERB]ing", slots={}
            )

    def test_pattern_ok(self) -> None:
        p = Pattern(
            id="pat:x",
            template="Dw i'n [VERB]",
            english="I'm [VERB]ing",
            slots={"VERB": PartOfSpeech.VERB},
        )
        assert p.slots == {"VERB": PartOfSpeech.VERB}

    def test_blank_fields_rejected(self) -> None:
        with pytest.raises(CurriculumError, match="Welsh must not be blank"):
            Lexeme(id="lex:x", welsh=" ", english="x", part_of_speech=PartOfSpeech.NOUN)


class TestValidation:
    def test_valid(self) -> None:
        c = build([L("a"), L("b", "lex:a")], ["lex:a", "lex:b"])
        assert c.topological_order() == ("lex:a", "lex:b")
        assert c.get("lex:b").id == "lex:b"

    def test_duplicate_ids(self) -> None:
        with pytest.raises(CurriculumError, match="Duplicate item ids: lex:a"):
            build([L("a"), L("a")], ["lex:a"])

    def test_unknown_prerequisite(self) -> None:
        with pytest.raises(
            CurriculumError, match="lex:a requires unknown item lex:zzz"
        ):
            build([L("a", "lex:zzz")], ["lex:a"])

    def test_cycle_reports_path(self) -> None:
        items = [L("a", "lex:c"), L("b", "lex:a"), L("c", "lex:b")]
        with pytest.raises(CurriculumError, match=r"lex:a -> lex:c -> lex:b -> lex:a"):
            build(items, ["lex:a", "lex:b", "lex:c"])

    def test_self_prerequisite_is_a_cycle(self) -> None:
        with pytest.raises(CurriculumError, match=r"lex:a -> lex:a"):
            build([L("a", "lex:a")], ["lex:a"])

    def test_order_violating_prerequisites(self) -> None:
        with pytest.raises(
            CurriculumError, match="lex:a comes before its prerequisite.*lex:b"
        ):
            build([L("a", "lex:b"), L("b")], ["lex:a", "lex:b"])

    def test_order_missing_item(self) -> None:
        with pytest.raises(CurriculumError, match="lex:b is missing from order"):
            build([L("a"), L("b")], ["lex:a"])

    def test_order_unknown_item(self) -> None:
        with pytest.raises(
            CurriculumError, match="order\\[1\\] is unknown item lex:nope"
        ):
            build([L("a")], ["lex:a", "lex:nope"])

    def test_order_repeated_item(self) -> None:
        with pytest.raises(CurriculumError, match="order\\[1\\] repeats lex:a"):
            build([L("a")], ["lex:a", "lex:a"])


class TestLexemeForms:
    def test_surface_forms_start_with_the_base_form(self) -> None:
        assert noun("llyfr", "llyfr", ("llyfrau",)).surface_forms == (
            "llyfr",
            "llyfrau",
        )

    def test_blank_form_is_rejected(self) -> None:
        with pytest.raises(CurriculumError, match="Form 0 must not be blank"):
            noun("llyfr", "llyfr", (" ",))

    def test_duplicate_form_is_rejected_ignoring_case(self) -> None:
        with pytest.raises(CurriculumError, match="Duplicate form 'Llyfrau'"):
            noun("llyfr", "llyfr", ("llyfrau", "Llyfrau"))

    def test_form_repeating_the_base_form_is_rejected(self) -> None:
        with pytest.raises(CurriculumError, match="Duplicate form 'llyfr'"):
            noun("llyfr", "llyfr", ("llyfr",))

    def test_lexeme_cannot_be_its_own_homograph(self) -> None:
        with pytest.raises(CurriculumError, match="its own homograph"):
            noun("llyfr", "llyfr", homographs=("lex:llyfr",))


class TestSurfaceFormConflicts:
    def test_form_shared_with_another_lexemes_base_is_rejected(self) -> None:
        with pytest.raises(CurriculumError, match="'tai' is shared by lex:tai, lex:ty"):
            build(
                [noun("tai", "tai"), noun("ty", "tŷ", ("tai",))], ["lex:tai", "lex:ty"]
            )

    def test_two_lexemes_with_the_same_base_form_are_rejected(self) -> None:
        with pytest.raises(CurriculumError, match="'cwrw' is shared"):
            build([noun("a", "cwrw"), noun("b", "Cwrw")], ["lex:a", "lex:b"])

    def test_mutual_homographs_are_allowed(self) -> None:
        build(
            [
                noun("a", "cwrw", homographs=("lex:b",)),
                noun("b", "cwrw", homographs=("lex:a",)),
            ],
            ["lex:a", "lex:b"],
        )

    def test_one_sided_homograph_is_rejected(self) -> None:
        with pytest.raises(CurriculumError, match="'cwrw' is shared"):
            build(
                [noun("a", "cwrw", homographs=("lex:b",)), noun("b", "cwrw")],
                ["lex:a", "lex:b"],
            )

    def test_unknown_homograph_is_rejected(self) -> None:
        with pytest.raises(
            CurriculumError, match="lex:a lists unknown homograph lex:zzz"
        ):
            build([noun("a", "cwrw", homographs=("lex:zzz",))], ["lex:a"])


class TestTopic:
    def test_defaults_to_the_spine(self) -> None:
        assert noun("coffi", "coffi").topic == DEFAULT_TOPIC == "spine"

    def test_patterns_default_to_the_spine_too(self) -> None:
        pattern = Pattern(
            id="pat:dw-in",
            template="Dw i'n [VERB]",
            english="I'm [VERB]ing",
            slots={"VERB": PartOfSpeech.VERB},
        )

        assert pattern.topic == "spine"

    def test_accepts_a_lowercase_slug(self) -> None:
        lexeme = Lexeme(
            id="lex:glaw",
            welsh="glaw",
            english="rain",
            part_of_speech=PartOfSpeech.NOUN,
            topic="weather-words",
        )

        assert lexeme.topic == "weather-words"

    @pytest.mark.parametrize("topic", ("", " ", "Weather", "1weather", "wea ther"))
    def test_rejects_anything_else(self, topic: str) -> None:
        with pytest.raises(CurriculumError, match="Invalid topic"):
            Lexeme(
                id="lex:glaw",
                welsh="glaw",
                english="rain",
                part_of_speech=PartOfSpeech.NOUN,
                topic=topic,
            )

    def test_a_pattern_rejects_an_invalid_topic(self) -> None:
        with pytest.raises(CurriculumError, match="Invalid topic"):
            Pattern(
                id="pat:dw-in",
                template="Dw i'n [VERB]",
                english="I'm [VERB]ing",
                slots={"VERB": PartOfSpeech.VERB},
                topic="Bad Topic",
            )


def in_topic(id_: str, topic: str, *prerequisites: str) -> Lexeme:
    return Lexeme(
        id=f"lex:{id_}",
        welsh=id_,
        english=id_,
        part_of_speech=PartOfSpeech.VERB,
        prerequisites=tuple(f"lex:{name}" for name in prerequisites),
        topic=topic,
    )


def with_topics(
    items: list[Lexeme], order: list[str], topics: list[Topic]
) -> Curriculum:
    return Curriculum(items=tuple(items), order=tuple(order), topics=tuple(topics))


SPINE = Topic(name="spine")
FOOD = Topic(name="food", requires=("spine",))
WEATHER = Topic(name="weather", requires=("spine",))


class TestTopicModel:
    def test_requires_nothing_by_default(self) -> None:
        assert Topic(name="spine").requires == ()

    def test_rejects_an_invalid_name(self) -> None:
        with pytest.raises(CurriculumError, match="Invalid topic"):
            Topic(name="Weather Pack")

    def test_cannot_require_itself(self) -> None:
        with pytest.raises(CurriculumError, match="cannot require itself"):
            Topic(name="food", requires=("food",))


class TestCurriculumTopics:
    ITEMS = [in_topic("a", "spine"), in_topic("b", "food"), in_topic("c", "weather")]
    ORDER = ["lex:a", "lex:b", "lex:c"]

    def test_accepts_topics_that_follow_what_they_require(self) -> None:
        curriculum = with_topics(self.ITEMS, self.ORDER, [SPINE, FOOD, WEATHER])

        assert curriculum.topics == (SPINE, FOOD, WEATHER)

    def test_rejects_duplicate_topics(self) -> None:
        with pytest.raises(CurriculumError, match="Duplicate topics: spine"):
            with_topics(self.ITEMS, self.ORDER, [SPINE, SPINE, FOOD, WEATHER])

    def test_rejects_a_requirement_that_is_not_a_topic(self) -> None:
        with pytest.raises(
            CurriculumError, match="food requires unknown topic cooking"
        ):
            with_topics(
                self.ITEMS,
                self.ORDER,
                [SPINE, Topic(name="food", requires=("cooking",)), WEATHER],
            )

    def test_rejects_a_topic_that_comes_before_what_it_requires(self) -> None:
        with pytest.raises(
            CurriculumError, match="food comes before the topic it requires"
        ):
            with_topics(self.ITEMS, self.ORDER, [FOOD, SPINE, WEATHER])

    def test_rejects_an_item_in_an_unknown_topic(self) -> None:
        with pytest.raises(CurriculumError, match="lex:c is in unknown topic weather"):
            with_topics(self.ITEMS, self.ORDER, [SPINE, FOOD])

    def test_rejects_a_prerequisite_in_a_topic_that_is_not_required(self) -> None:
        items = [
            in_topic("a", "spine"),
            in_topic("b", "food"),
            in_topic("c", "weather", "b"),
        ]

        with pytest.raises(CurriculumError, match="weather does not require food"):
            with_topics(items, self.ORDER, [SPINE, FOOD, WEATHER])

    def test_accepts_a_prerequisite_in_a_topic_required_through_another(self) -> None:
        items = [
            in_topic("a", "spine"),
            in_topic("b", "food", "a"),
            in_topic("c", "weather", "a"),
        ]
        deep = Topic(name="weather", requires=("food",))

        curriculum = with_topics(items, self.ORDER, [SPINE, FOOD, deep])

        assert curriculum.get("lex:c").prerequisites == ("lex:a",)


class TestKnownBefore:
    def test_without_topics_it_is_everything_earlier_in_the_order(self) -> None:
        curriculum = build([L("a"), L("b"), L("c")], ["lex:a", "lex:b", "lex:c"])

        assert curriculum.known_before("lex:c") == {"lex:a", "lex:b"}
        assert curriculum.known_before("lex:a") == frozenset()

    def test_with_topics_it_is_the_topics_earlier_items_and_every_required_item(
        self,
    ) -> None:
        items = [
            in_topic("a", "spine"),
            in_topic("b", "spine"),
            in_topic("c", "food"),
            in_topic("d", "food"),
        ]
        curriculum = with_topics(
            items, ["lex:a", "lex:b", "lex:c", "lex:d"], [SPINE, FOOD]
        )

        assert curriculum.known_before("lex:c") == {"lex:a", "lex:b"}
        assert curriculum.known_before("lex:d") == {"lex:a", "lex:b", "lex:c"}
        assert curriculum.known_before("lex:a") == frozenset()

    def test_a_sibling_topic_is_not_known(self) -> None:
        items = [
            in_topic("a", "spine"),
            in_topic("b", "food"),
            in_topic("c", "weather"),
        ]
        curriculum = with_topics(
            items, ["lex:a", "lex:b", "lex:c"], [SPINE, FOOD, WEATHER]
        )

        assert curriculum.known_before("lex:c") == {"lex:a"}

    def test_required_topics_count_whatever_order_the_topics_are_taught_in(
        self,
    ) -> None:
        items = [
            in_topic("a", "spine"),
            in_topic("b", "food"),
            in_topic("c", "weather"),
        ]
        reordered = with_topics(
            items, ["lex:a", "lex:c", "lex:b"], [SPINE, WEATHER, FOOD]
        )

        assert reordered.known_before("lex:b") == {"lex:a"}

    def test_requirements_are_followed_through_other_topics(self) -> None:
        items = [
            in_topic("a", "spine"),
            in_topic("b", "food"),
            in_topic("c", "weather"),
        ]
        deep = Topic(name="weather", requires=("food",))
        curriculum = with_topics(
            items, ["lex:a", "lex:b", "lex:c"], [SPINE, FOOD, deep]
        )

        assert curriculum.known_before("lex:c") == {"lex:a", "lex:b"}
