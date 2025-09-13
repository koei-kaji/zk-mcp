import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.zk_mcp.tools.get_note import get_note


class TestGetNote:
    """get_note 関数のテスト"""

    def test_returns_note_content_when_valid_path_is_given(self) -> None:
        """正常なパスが与えられた場合、ノートコンテンツが返されること"""
        # Given
        cwd = Path("/test/dir")
        path = "note1.md"
        mock_content = "# Test Note\n\nThis is a test note."

        mock_result = MagicMock()
        mock_result.stdout = mock_content
        mock_result.returncode = 0

        # When
        with (
            patch("src.zk_mcp.tools.get_note._validate_path") as mock_validate,
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            mock_validate.return_value = cwd / path
            result = get_note(cwd, path)

        # Then
        assert result == mock_content
        mock_validate.assert_called_once_with(path, cwd)
        mock_run.assert_called_once_with(
            ["zk", "list", "--quiet", "--format", "{{raw-content}}", path],
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True,
        )

    @pytest.mark.parametrize(
        "path,validation_error",
        [
            pytest.param(
                "../outside.md",
                ValueError("無効なパス"),
                id="親ディレクトリのパスである場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "/absolute/path.md",
                ValueError("絶対パス"),
                id="絶対パスである場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "",
                ValueError("空のパス"),
                id="空のパスである場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "very_long_path.md",
                ValueError("パスが長すぎます"),
                id="長すぎるパスである場合、RuntimeError が発生すること",
            ),
        ],
    )
    def test_raises_runtime_error_when_path_validation_fails(
        self, path: str, validation_error: ValueError
    ) -> None:
        # Given
        cwd = Path("/test/dir")

        # When, Then
        with patch(
            "src.zk_mcp.tools.get_note._validate_path", side_effect=validation_error
        ):
            with pytest.raises(
                RuntimeError, match=f"zkコマンド実行エラー: {validation_error}"
            ):
                get_note(cwd, path)

    @pytest.mark.parametrize(
        "error_message",
        [
            pytest.param(
                "File not found",
                id="ファイルが見つからない場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "Permission denied",
                id="権限エラーが発生した場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "Invalid format",
                id="フォーマットエラーが発生した場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "Command failed",
                id="コマンドが失敗した場合、RuntimeError が発生すること",
            ),
        ],
    )
    def test_raises_runtime_error_when_zk_command_fails(
        self, error_message: str
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        path = "note1.md"

        mock_error = subprocess.CalledProcessError(1, ["zk"])
        mock_error.stderr = error_message

        # When, Then
        with (
            patch("src.zk_mcp.tools.get_note._validate_path") as mock_validate,
            patch("subprocess.run", side_effect=mock_error),
        ):
            mock_validate.return_value = cwd / path
            with pytest.raises(
                RuntimeError, match=f"zkコマンド実行エラー: {error_message}"
            ):
                get_note(cwd, path)

    @pytest.mark.parametrize(
        "mock_content,expected_result",
        [
            pytest.param(
                "", "", id="空のノートコンテンツが返された場合、空文字列が返されること"
            ),
            pytest.param(
                "   ",
                "   ",
                id="空白のみのノートコンテンツが返された場合、空白文字列が返されること",
            ),
            pytest.param(
                "# Title",
                "# Title",
                id="シンプルなノートコンテンツが返された場合、コンテンツが返されること",
            ),
        ],
    )
    def test_returns_empty_string_when_empty_content_is_returned(
        self, mock_content: str, expected_result: str
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        path = "empty.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_content
        mock_result.returncode = 0

        # When
        with (
            patch("src.zk_mcp.tools.get_note._validate_path") as mock_validate,
            patch("subprocess.run", return_value=mock_result),
        ):
            mock_validate.return_value = cwd / path
            result = get_note(cwd, path)

        # Then
        assert result == expected_result

    @pytest.mark.parametrize(
        "mock_content",
        [
            pytest.param(
                """# Multi-line Note

This is a multi-line note.

## Section 1
Content of section 1.

## Section 2
Content of section 2.

- List item 1
- List item 2
- List item 3

Some **bold** text and *italic* text.
""",
                id="複数行のノートコンテンツが正しく返されること",
            ),
            pytest.param(
                """# 日本語ノート

これは日本語のテストノートです。

## セクション1
日本語のコンテンツです。

- アイテム1
- アイテム2
- アイテム3

絵文字も含まれます: 📝 📖 📚
""",
                id="Unicode文字が含まれるファイルコンテンツが正しく返されること",
            ),
            pytest.param(
                """# Special Characters

This note contains special characters:
- Quotes: "double" and 'single'
- Symbols: @#$%^&*()
- Brackets: [square] {curly} (round)
- Backslashes: \\ and \\n
- Pipes: | and ||
""",
                id="特殊文字が含まれるコンテンツが正しく返されること",
            ),
        ],
    )
    def test_returns_multiline_content_correctly(self, mock_content: str) -> None:
        # Given
        cwd = Path("/test/dir")
        path = "multiline.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_content
        mock_result.returncode = 0

        # When
        with (
            patch("src.zk_mcp.tools.get_note._validate_path") as mock_validate,
            patch("subprocess.run", return_value=mock_result),
        ):
            mock_validate.return_value = cwd / path
            result = get_note(cwd, path)

        # Then
        assert result == mock_content

    @pytest.mark.parametrize(
        "path",
        [
            pytest.param(
                "note1.md", id="単一ファイルのパスである場合、正しく処理されること"
            ),
            pytest.param(
                "sub/note2.md",
                id="サブディレクトリのパスである場合、正しく処理されること",
            ),
            pytest.param(
                "deep/sub/note3.md",
                id="深いサブディレクトリのパスである場合、正しく処理されること",
            ),
            pytest.param(
                "note with spaces.md",
                id="スペースを含むパスである場合、正しく処理されること",
            ),
            pytest.param(
                "日本語ノート.md", id="日本語を含むパスである場合、正しく処理されること"
            ),
            pytest.param(
                "note-with-dash.md",
                id="ハイフンを含むパスである場合、正しく処理されること",
            ),
            pytest.param(
                "note_with_underscore.md",
                id="アンダースコアを含むパスである場合、正しく処理されること",
            ),
            pytest.param(
                "note.with.dots.md",
                id="ドットを含むパスである場合、正しく処理されること",
            ),
        ],
    )
    def test_processes_various_path_patterns_correctly(self, path: str) -> None:
        # Given
        cwd = Path("/test/dir")
        mock_content = "Test content"

        mock_result = MagicMock()
        mock_result.stdout = mock_content
        mock_result.returncode = 0

        # When
        with (
            patch("src.zk_mcp.tools.get_note._validate_path") as mock_validate,
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            mock_validate.return_value = cwd / path
            result = get_note(cwd, path)

        # Then
        assert result == mock_content
        mock_validate.assert_called_once_with(path, cwd)
        mock_run.assert_called_once_with(
            ["zk", "list", "--quiet", "--format", "{{raw-content}}", path],
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True,
        )

    def test_sets_zk_command_arguments_correctly(self) -> None:
        """zkコマンドの引数が正しく設定されること"""
        # Given
        cwd = Path("/test/dir")
        path = "test.md"
        mock_content = "Test content"

        mock_result = MagicMock()
        mock_result.stdout = mock_content
        mock_result.returncode = 0

        # When
        with (
            patch("src.zk_mcp.tools.get_note._validate_path") as mock_validate,
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            mock_validate.return_value = cwd / path
            get_note(cwd, path)

        # Then
        expected_command = [
            "zk",
            "list",
            "--quiet",
            "--format",
            "{{raw-content}}",
            path,
        ]
        mock_run.assert_called_once_with(
            expected_command,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True,
        )

    def test_validates_path_correctly(self) -> None:
        """パス検証が正しく実行されること"""
        # Given
        cwd = Path("/test/dir")
        path = "test.md"
        mock_content = "Test content"

        mock_result = MagicMock()
        mock_result.stdout = mock_content
        mock_result.returncode = 0

        # When
        with (
            patch("src.zk_mcp.tools.get_note._validate_path") as mock_validate,
            patch("subprocess.run", return_value=mock_result),
        ):
            mock_validate.return_value = cwd / path
            get_note(cwd, path)

        # Then
        mock_validate.assert_called_once_with(path, cwd)

    @pytest.mark.parametrize(
        "mock_content,expected_result",
        [
            pytest.param(
                "Content with trailing newline\n",
                "Content with trailing newline\n",
                id="末尾に改行が含まれるコンテンツが正しく返されること",
            ),
            pytest.param(
                "Content with multiple newlines\n\n",
                "Content with multiple newlines\n\n",
                id="末尾に複数の改行が含まれるコンテンツが正しく返されること",
            ),
            pytest.param(
                "Content without newline",
                "Content without newline",
                id="末尾に改行がないコンテンツが正しく返されること",
            ),
            pytest.param(
                "\nContent with leading newline",
                "\nContent with leading newline",
                id="先頭に改行が含まれるコンテンツが正しく返されること",
            ),
        ],
    )
    def test_handles_content_with_newlines_correctly(
        self, mock_content: str, expected_result: str
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        path = "trailing-newline.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_content
        mock_result.returncode = 0

        # When
        with (
            patch("src.zk_mcp.tools.get_note._validate_path") as mock_validate,
            patch("subprocess.run", return_value=mock_result),
        ):
            mock_validate.return_value = cwd / path
            result = get_note(cwd, path)

        # Then
        assert result == expected_result

    @pytest.mark.parametrize(
        "command_parts",
        [
            pytest.param("zk", id="zkコマンドが正しく設定されること"),
            pytest.param("list", id="listサブコマンドが正しく設定されること"),
            pytest.param("--quiet", id="quietオプションが正しく設定されること"),
            pytest.param("--format", id="formatオプションが正しく設定されること"),
            pytest.param(
                "{{raw-content}}", id="raw-contentフォーマットが正しく設定されること"
            ),
        ],
    )
    def test_sets_individual_command_parts_correctly(self, command_parts: str) -> None:
        # Given
        cwd = Path("/test/dir")
        path = "test.md"
        mock_content = "Test content"

        mock_result = MagicMock()
        mock_result.stdout = mock_content
        mock_result.returncode = 0

        # When
        with (
            patch("src.zk_mcp.tools.get_note._validate_path") as mock_validate,
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            mock_validate.return_value = cwd / path
            get_note(cwd, path)

        # Then
        called_command = mock_run.call_args[0][0]
        assert command_parts in called_command
