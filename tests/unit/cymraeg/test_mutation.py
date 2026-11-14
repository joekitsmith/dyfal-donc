import pytest
from hypothesis import given
from hypothesis import strategies as st

from cymraeg.mutation import Demutation, Mutation, demutate, mutate

RADICAL_INITIALS = (
    "p t c b d g m ll rh f ff ch th ph dd ng n l r h s j gw gl gr bl br cl cr dr "
    "pl pr tr w y a e i o u"
).split()
VOWELS = "aeiouwyâêîôûŵŷ"
CONSONANTS_AND_VOWELS = "abcdefghilmnoprstuwyâêîôûŵŷ"


@st.composite
def radical_words(draw: st.DrawFn) -> str:
    initial = draw(st.sampled_from(RADICAL_INITIALS))
    vowel = draw(st.sampled_from(VOWELS)) if initial[-1] not in VOWELS else ""
    tail = draw(st.text(alphabet=CONSONANTS_AND_VOWELS, max_size=8))
    word = initial + vowel + tail
    return draw(st.sampled_from((word, word.capitalize())))


def soft(radical: str) -> Demutation:
    return Demutation(radical=radical, mutation=Mutation.SOFT)


def nasal(radical: str) -> Demutation:
    return Demutation(radical=radical, mutation=Mutation.NASAL)


def aspirate(radical: str) -> Demutation:
    return Demutation(radical=radical, mutation=Mutation.ASPIRATE)


def h_prothesis(radical: str) -> Demutation:
    return Demutation(radical=radical, mutation=Mutation.H_PROTHESIS)


def as_is(token: str) -> Demutation:
    return Demutation(radical=token, mutation=None)


class TestMutateSoft:
    @pytest.mark.parametrize(
        ("word", "expected"),
        [
            ("pen", "ben"),
            ("tad", "dad"),
            ("cath", "gath"),
            ("bara", "fara"),
            ("dysgu", "ddysgu"),
            ("gardd", "ardd"),
            ("glas", "las"),
            ("gwaith", "waith"),
            ("mynd", "fynd"),
            ("llaeth", "laeth"),
            ("rhedeg", "redeg"),
        ],
    )
    def test_softens_the_initial_consonant(self, word: str, expected: str) -> None:
        assert mutate(word, Mutation.SOFT) == expected

    @pytest.mark.parametrize(
        "word", ["afal", "ffenest", "chwech", "ddoe", "phobl", "thema", "ngardd", "sut"]
    )
    def test_leaves_words_that_do_not_soften(self, word: str) -> None:
        assert mutate(word, Mutation.SOFT) == word


class TestMutateNasal:
    @pytest.mark.parametrize(
        ("word", "expected"),
        [
            ("pen", "mhen"),
            ("tad", "nhad"),
            ("cath", "nghath"),
            ("bara", "mara"),
            ("dysgu", "nysgu"),
            ("gardd", "ngardd"),
        ],
    )
    def test_nasalises_the_initial_consonant(self, word: str, expected: str) -> None:
        assert mutate(word, Mutation.NASAL) == expected

    @pytest.mark.parametrize("word", ["afal", "llaeth", "chwech", "ddoe", "mynd"])
    def test_leaves_words_that_do_not_nasalise(self, word: str) -> None:
        assert mutate(word, Mutation.NASAL) == word


class TestMutateAspirate:
    @pytest.mark.parametrize(
        ("word", "expected"),
        [("pen", "phen"), ("tad", "thad"), ("cath", "chath")],
    )
    def test_aspirates_the_initial_consonant(self, word: str, expected: str) -> None:
        assert mutate(word, Mutation.ASPIRATE) == expected

    @pytest.mark.parametrize("word", ["bara", "afal", "chwech", "phobl", "mynd"])
    def test_leaves_words_that_do_not_aspirate(self, word: str) -> None:
        assert mutate(word, Mutation.ASPIRATE) == word


class TestMutateHProthesis:
    @pytest.mark.parametrize(
        ("word", "expected"),
        [("afal", "hafal"), ("ysgol", "hysgol"), ("wy", "hwy"), ("ŵy", "hŵy")],
    )
    def test_adds_h_before_a_vowel(self, word: str, expected: str) -> None:
        assert mutate(word, Mutation.H_PROTHESIS) == expected

    @pytest.mark.parametrize("word", ["bara", "hen", "llaeth", ""])
    def test_leaves_consonant_initial_words(self, word: str) -> None:
        assert mutate(word, Mutation.H_PROTHESIS) == word


class TestMutateCapitalisation:
    @pytest.mark.parametrize(
        ("word", "mutation", "expected"),
        [
            ("Cymraeg", Mutation.SOFT, "Gymraeg"),
            ("Gwaith", Mutation.SOFT, "Waith"),
            ("Llan", Mutation.SOFT, "Lan"),
            ("Rhedeg", Mutation.SOFT, "Redeg"),
            ("Pen", Mutation.NASAL, "Mhen"),
            ("Cath", Mutation.ASPIRATE, "Chath"),
            ("Afal", Mutation.H_PROTHESIS, "Hafal"),
            ("CYMRU", Mutation.SOFT, "GYMRU"),
        ],
    )
    def test_initial_capital_is_preserved(
        self, word: str, mutation: Mutation, expected: str
    ) -> None:
        assert mutate(word, mutation) == expected


class TestDemutate:
    @pytest.mark.parametrize(
        ("token", "expected"),
        [
            ("fynd", (as_is("fynd"), soft("bynd"), soft("mynd"))),
            ("Gymraeg", (as_is("Gymraeg"), soft("Cymraeg"))),
            ("ddysgu", (as_is("ddysgu"), soft("dysgu"))),
            ("dad", (as_is("dad"), soft("tad"))),
            ("fara", (as_is("fara"), soft("bara"), soft("mara"))),
            ("nghath", (as_is("nghath"), nasal("cath"))),
            ("ngardd", (as_is("ngardd"), nasal("gardd"))),
            ("mhen", (as_is("mhen"), nasal("pen"))),
            ("nhad", (as_is("nhad"), nasal("tad"))),
            ("mara", (as_is("mara"), nasal("bara"))),
            ("nysgu", (as_is("nysgu"), nasal("dysgu"))),
            ("phen", (as_is("phen"), aspirate("pen"))),
            ("thad", (as_is("thad"), aspirate("tad"))),
            ("chath", (as_is("chath"), aspirate("cath"))),
            ("hafal", (as_is("hafal"), h_prothesis("afal"))),
            ("Hysgol", (as_is("Hysgol"), h_prothesis("Ysgol"))),
        ],
    )
    def test_finds_every_plausible_radical(
        self, token: str, expected: tuple[Demutation, ...]
    ) -> None:
        assert demutate(token) == expected

    @pytest.mark.parametrize(
        ("token", "expected"),
        [
            ("ardd", (as_is("ardd"), soft("gardd"))),
            ("las", (as_is("las"), soft("glas"), soft("llas"))),
            ("redeg", (as_is("redeg"), soft("gredeg"), soft("rhedeg"))),
            ("waith", (as_is("waith"), soft("gwaith"))),
            ("Ardd", (as_is("Ardd"), soft("Gardd"))),
            ("ARDD", (as_is("ARDD"), soft("GARDD"))),
        ],
    )
    def test_restores_a_deleted_g(
        self, token: str, expected: tuple[Demutation, ...]
    ) -> None:
        assert demutate(token) == expected

    @pytest.mark.parametrize("token", ["llaw", "rhedeg", "ffenest", "sut"])
    def test_digraphs_and_unaffected_initials_only_read_as_they_are(
        self, token: str
    ) -> None:
        assert demutate(token) == (as_is(token),)

    def test_longest_prefix_wins(self) -> None:
        assert nasal("cath") in demutate("nghath")
        assert nasal("hath") not in demutate("nghath")
        assert nasal("tad") in demutate("nhad")
        assert nasal("dad") not in demutate("nhad")
        assert soft("dysgu") in demutate("ddysgu")
        assert soft("tysgu") not in demutate("ddysgu")

    def test_ambiguous_tokens_keep_every_reading(self) -> None:
        radicals = {demutation.radical for demutation in demutate("las")}
        assert {"las", "glas", "llas"} <= radicals

    def test_empty_token_has_only_the_unmutated_reading(self) -> None:
        assert demutate("") == (as_is(""),)

    @pytest.mark.parametrize("token", ["fynd", "las", "redeg", "hafal", "nghath", "x"])
    def test_ordering_is_deterministic(self, token: str) -> None:
        assert demutate(token) == demutate(token)

    @given(st.text(max_size=12))
    def test_the_unmutated_reading_comes_first_and_mutations_follow_enum_order(
        self, token: str
    ) -> None:
        demutations = demutate(token)
        assert demutations[0] == as_is(token)
        mutations = [demutation.mutation for demutation in demutations[1:]]
        assert None not in mutations
        order = list(Mutation)
        indices = [
            order.index(mutation) for mutation in mutations if mutation is not None
        ]
        assert indices == sorted(indices)
        assert len(set(demutations)) == len(demutations)


class TestRoundTrip:
    @pytest.mark.parametrize("mutation", list(Mutation))
    @given(word=radical_words())
    def test_demutating_a_mutated_word_recovers_the_radical(
        self, mutation: Mutation, word: str
    ) -> None:
        radicals = {
            demutation.radical for demutation in demutate(mutate(word, mutation))
        }
        assert word in radicals
