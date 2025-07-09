import re

import pytest

from tools._validate_directory import _validate_directory


class TestValidateDirectory:
    """_validate_directory 関数のテスト"""

    @pytest.mark.parametrize(
        "directory",
        [
            pytest.param(
                "sub", id="サブディレクトリ名である場合、ディレクトリ名が返されること"
            ),
            pytest.param("", id="空文字である場合、ディレクトリ名が返されること"),
        ],
    )
    def test_returns_directory_name_when_valid_directory_is_given(self, directory):
        # When
        result = _validate_directory(directory)

        # Then
        assert result == directory

    @pytest.mark.parametrize(
        "directory,expected_error",
        [
            pytest.param(
                "a" * 201,
                "ディレクトリ名が長すぎます",
                id="201文字以上である場合、ValueError が発生すること",
            ),
            pytest.param(
                "../parent",
                "ディレクトリ名にパストラバーサルが検出されました",
                id="親ディレクトリへのパスである場合、ValueError が発生すること",
            ),
            pytest.param(
                "/absolute/path",
                "ディレクトリ名にパストラバーサルが検出されました",
                id="絶対パスである場合、ValueError が発生すること",
            ),
            pytest.param(
                "test\x00dir",
                "ディレクトリ名に制御文字が含まれています",
                id="制御文字が含まれている場合、ValueError が発生すること",
            ),
        ],
    )
    def test_raises_value_error_when_invalid_directory_is_given(
        self, directory, expected_error
    ):
        # When, Then
        with pytest.raises(ValueError, match=expected_error):
            _validate_directory(directory)

    @pytest.mark.parametrize(
        "directory",
        [
            pytest.param(
                "a" * 200, id="200文字である場合、ディレクトリ名が返されること"
            ),
        ],
    )
    def test_returns_directory_name_when_boundary_value_directory_is_given(
        self, directory
    ):
        # When
        result = _validate_directory(directory)

        # Then
        assert result == directory

    @pytest.mark.parametrize(
        "dangerous_char",
        [
            pytest.param(
                ";", id="セミコロンが含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "&", id="アンパサンドが含まれている場合、ValueError が発生すること"
            ),
            pytest.param("|", id="パイプが含まれている場合、ValueError が発生すること"),
            pytest.param(
                "`", id="バッククォートが含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "$", id="ドル記号が含まれている場合、ValueError が発生すること"
            ),
            pytest.param("(", id="左括弧が含まれている場合、ValueError が発生すること"),
            pytest.param(")", id="右括弧が含まれている場合、ValueError が発生すること"),
            pytest.param(
                "{", id="左波括弧が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "}", id="右波括弧が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "[", id="左角括弧が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "]", id="右角括弧が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                ">", id="右不等号が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "<", id="左不等号が含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "!",
                id="エクスクラメーションが含まれている場合、ValueError が発生すること",
            ),
            pytest.param("~", id="チルダが含まれている場合、ValueError が発生すること"),
            pytest.param(
                "*", id="アスタリスクが含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "?",
                id="クエスチョンマークが含まれている場合、ValueError が発生すること",
            ),
            pytest.param(
                '"', id="ダブルクォートが含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "'", id="シングルクォートが含まれている場合、ValueError が発生すること"
            ),
            pytest.param(
                "\\", id="バックスラッシュが含まれている場合、ValueError が発生すること"
            ),
        ],
    )
    def test_raises_value_error_when_dangerous_character_is_included(
        self, dangerous_char
    ):
        # Given
        directory = f"test{dangerous_char}dir"

        # When, Then
        with pytest.raises(
            ValueError,
            match=f"ディレクトリ名に危険な文字が含まれています: {re.escape(dangerous_char)}",
        ):
            _validate_directory(directory)

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
    def test_raises_value_error_when_control_character_is_included(self, control_char):
        # Given
        directory = f"test{control_char}dir"

        # When, Then
        with pytest.raises(
            ValueError, match="ディレクトリ名に制御文字が含まれています"
        ):
            _validate_directory(directory)

    @pytest.mark.parametrize(
        "valid_directory",
        [
            pytest.param(
                "sub", id="短いディレクトリ名である場合、ディレクトリ名が返されること"
            ),
            pytest.param(
                "subdirectory",
                id="長いディレクトリ名である場合、ディレクトリ名が返されること",
            ),
            pytest.param(
                "sub-directory",
                id="ハイフンが含まれるディレクトリ名である場合、ディレクトリ名が返されること",
            ),
            pytest.param(
                "sub_directory",
                id="アンダースコアが含まれるディレクトリ名である場合、ディレクトリ名が返されること",
            ),
            pytest.param(
                "123",
                id="数字のみのディレクトリ名である場合、ディレクトリ名が返されること",
            ),
            pytest.param(
                "dir123",
                id="数字が含まれるディレクトリ名である場合、ディレクトリ名が返されること",
            ),
            pytest.param(
                "日本語ディレクトリ",
                id="日本語ディレクトリ名である場合、ディレクトリ名が返されること",
            ),
            pytest.param(
                "mixed123日本語",
                id="混在文字のディレクトリ名である場合、ディレクトリ名が返されること",
            ),
        ],
    )
    def test_returns_directory_name_when_various_valid_directories_are_given(
        self, valid_directory
    ):
        # Given, When
        result = _validate_directory(valid_directory)

        # Then
        assert result == valid_directory

    @pytest.mark.parametrize(
        "invalid_path",
        [
            pytest.param(
                "..", id="親ディレクトリ参照である場合、ValueError が発生すること"
            ),
            pytest.param(
                "../", id="親ディレクトリパスである場合、ValueError が発生すること"
            ),
            pytest.param(
                "sub/../parent",
                id="相対パスが含まれている場合、ValueError が発生すること",
            ),
            pytest.param(
                "sub/../../grandparent",
                id="複数階層の相対パスが含まれている場合、ValueError が発生すること",
            ),
            pytest.param(
                "/root",
                id="ルートディレクトリの絶対パスである場合、ValueError が発生すること",
            ),
            pytest.param(
                "/absolute/path", id="絶対パスである場合、ValueError が発生すること"
            ),
        ],
    )
    def test_raises_value_error_when_path_traversal_pattern_is_given(
        self, invalid_path
    ):
        # Given
        directory = invalid_path

        # When, Then
        with pytest.raises(
            ValueError, match="ディレクトリ名にパストラバーサルが検出されました"
        ):
            _validate_directory(directory)

    @pytest.mark.parametrize(
        "directory",
        [
            pytest.param(
                "フォルダ📁",
                id="絵文字が含まれている場合、ディレクトリ名が返されること",
            ),
            pytest.param(
                "test-dir_name",
                id="複数の区切り文字が含まれている場合、ディレクトリ名が返されること",
            ),
        ],
    )
    def test_returns_directory_name_when_other_valid_directories_are_given(
        self, directory
    ):
        # When
        result = _validate_directory(directory)

        # Then
        assert result == directory
