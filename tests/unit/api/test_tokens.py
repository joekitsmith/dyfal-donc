from api.tokens import hash_token, new_token


class TestNewToken:
    def test_tokens_are_long_and_differ(self) -> None:
        tokens = {new_token() for _ in range(50)}

        assert len(tokens) == 50
        assert all(len(token) >= 40 for token in tokens)


class TestHashToken:
    def test_the_same_token_gives_the_same_hash(self) -> None:
        assert hash_token("abc") == hash_token("abc")

    def test_different_tokens_give_different_hashes(self) -> None:
        assert hash_token("abc") != hash_token("abd")

    def test_the_hash_is_not_the_token(self) -> None:
        assert b"abc" not in hash_token("abc")
        assert len(hash_token("abc")) == 32
