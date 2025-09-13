import pytest

from src.zk_mcp.tools._validate_title import _validate_title


class TestValidateTitle:
    """_validate_title 関数のテスト"""

    def test_returns_title_when_valid_title_is_given(self) -> None:
        """正常なタイトルが与えられた場合、タイトルが返されること"""
        # Given
        title = "正常なタイトル"

        # When
        result = _validate_title(title)

        # Then
        assert result == title

    @pytest.mark.parametrize(
        "title,expected_error",
        [
            pytest.param(
                "", "タイトルが空です", id="空文字である場合、ValueError が発生すること"
            ),
            pytest.param(
                "   ",
                "タイトルが空です",
                id="空白文字のみである場合、ValueError が発生すること",
            ),
            pytest.param(
                "a" * 501,
                "タイトルが長すぎます",
                id="501文字以上である場合、ValueError が発生すること",
            ),
            pytest.param(
                "タイトル\x00制御文字",
                "タイトルに制御文字が含まれています",
                id="制御文字が含まれている場合、ValueError が発生すること",
            ),
        ],
    )
    def test_raises_value_error_when_invalid_title_is_given(
        self, title: str, expected_error: str
    ) -> None:
        # When, Then
        with pytest.raises(ValueError, match=expected_error):
            _validate_title(title)

    @pytest.mark.parametrize(
        "title",
        [
            pytest.param("a" * 500, id="500文字である場合、タイトルが返されること"),
            pytest.param(
                "タイトル\tタブ\n改行\r復帰",
                id="タブ・改行・復帰文字が含まれている場合、タイトルが返されること",
            ),
        ],
    )
    def test_returns_title_when_valid_title_is_given_with_edge_cases(
        self, title: str
    ) -> None:
        # When
        result = _validate_title(title)

        # Then
        assert result == title

    @pytest.mark.parametrize(
        "control_char",
        [
            pytest.param(
                "\x00", id="NULL文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x01", id="SOH文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x02", id="STX文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x03", id="ETX文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x04", id="EOT文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x05", id="ENQ文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x06", id="ACK文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x07", id="BEL文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x08", id="BS文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x0b", id="VT文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x0c", id="FF文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x0e", id="SO文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x0f", id="SI文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x10", id="DLE文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x11", id="DC1文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x12", id="DC2文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x13", id="DC3文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x14", id="DC4文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x15", id="NAK文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x16", id="SYN文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x17", id="ETB文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x18", id="CAN文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x19", id="EM文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x1a", id="SUB文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x1b", id="ESC文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x1c", id="FS文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x1d", id="GS文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x1e", id="RS文字が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\x1f", id="US文字が含まれている場合、ValueError が発生すること"
            ),
        ],
    )
    def test_raises_value_error_when_title_contains_control_characters(
        self, control_char: str
    ) -> None:
        # Given
        title = f"タイトル{control_char}制御文字"

        # When, Then
        with pytest.raises(ValueError, match="タイトルに制御文字が含まれています"):
            _validate_title(title)

    @pytest.mark.parametrize(
        "valid_title",
        [
            pytest.param(
                "日本語タイトル", id="日本語タイトルである場合、タイトルが返されること"
            ),
            pytest.param(
                "English Title", id="英語タイトルである場合、タイトルが返されること"
            ),
            pytest.param(
                "タイトル with mixed language",
                id="混在言語タイトルである場合、タイトルが返されること",
            ),
            pytest.param(
                "タイトル-with-dash",
                id="ダッシュが含まれている場合、タイトルが返されること",
            ),
            pytest.param(
                "タイトル_with_underscore",
                id="アンダースコアが含まれている場合、タイトルが返されること",
            ),
            pytest.param(
                "タイトル with spaces",
                id="スペースが含まれている場合、タイトルが返されること",
            ),
            pytest.param("123456789", id="数字のみである場合、タイトルが返されること"),
            pytest.param(
                "特殊文字!@#$%^&*()+=[]{}|;:,.<>?/~`",
                id="特殊文字が含まれている場合、タイトルが返されること",
            ),
            pytest.param(
                "タイトル\tタブ",
                id="タブ文字が含まれている場合、タイトルが返されること",
            ),
            pytest.param(
                "タイトル\n改行",
                id="改行文字が含まれている場合、タイトルが返されること",
            ),
            pytest.param(
                "タイトル\r復帰",
                id="復帰文字が含まれている場合、タイトルが返されること",
            ),
        ],
    )
    def test_returns_title_when_various_valid_titles_are_given(
        self, valid_title: str
    ) -> None:
        # Given, When
        result = _validate_title(valid_title)

        # Then
        assert result == valid_title

    @pytest.mark.parametrize(
        "title",
        [
            pytest.param(
                "絵文字📝付きタイトル",
                id="絵文字が含まれている場合、タイトルが返されること",
            ),
            pytest.param(
                "  タイトル  ",
                id="前後に空白が含まれている場合、タイトルが返されること",
            ),
        ],
    )
    def test_returns_title_when_other_valid_titles_are_given(self, title: str) -> None:
        # When
        result = _validate_title(title)

        # Then
        assert result == title
