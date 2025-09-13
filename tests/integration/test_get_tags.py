import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.zk_mcp.tools.get_tags import get_tags


class TestGetTags:
    """get_tags 関数のテスト"""

    def test_returns_tag_list_when_zk_command_succeeds(self) -> None:
        """zkコマンドが成功した場合、タグリストが返されること"""
        # Given
        cwd = Path("/test/dir")
        mock_stdout = "tag1\ntag2\ntag3\n"

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_tags(cwd)

        # Then
        result_data = json.loads(result)
        assert result_data["tags"] == ["tag1", "tag2", "tag3"]

    @pytest.mark.parametrize(
        "mock_stdout,expected_tags",
        [
            pytest.param(
                "", [], id="空の結果が返された場合、空のタグリストが返されること"
            ),
            pytest.param(
                "   ",
                [],
                id="空白のみの結果が返された場合、空のタグリストが返されること",
            ),
            pytest.param(
                "\n\n",
                [],
                id="改行のみの結果が返された場合、空のタグリストが返されること",
            ),
            pytest.param(
                "   \n   ",
                [],
                id="複数の空白行が返された場合、空のタグリストが返されること",
            ),
        ],
    )
    def test_returns_empty_tag_list_when_zk_command_returns_empty_result(
        self, mock_stdout: str, expected_tags: list[str]
    ) -> None:
        # Given
        cwd = Path("/test/dir")

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_tags(cwd)

        # Then
        result_data = json.loads(result)
        assert result_data["tags"] == expected_tags

    @pytest.mark.parametrize(
        "error_message",
        [
            pytest.param(
                "zk command failed",
                id="一般的なエラーが発生した場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "File not found",
                id="ファイルが見つからない場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "Permission denied",
                id="権限エラーが発生した場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "Invalid command",
                id="無効なコマンドエラーが発生した場合、RuntimeError が発生すること",
            ),
        ],
    )
    def test_raises_runtime_error_when_zk_command_fails(
        self, error_message: str
    ) -> None:
        # Given
        cwd = Path("/test/dir")

        mock_error = subprocess.CalledProcessError(1, ["zk"])
        mock_error.stderr = error_message

        # When, Then
        with patch("subprocess.run", side_effect=mock_error):
            with pytest.raises(
                RuntimeError, match=f"zkコマンド実行エラー: {error_message}"
            ):
                get_tags(cwd)

    @pytest.mark.parametrize(
        "mock_stdout,expected_tags",
        [
            pytest.param(
                "important\n",
                ["important"],
                id="1つのタグが返された場合、1つのタグが設定されること",
            ),
            pytest.param(
                "important\nurgent\n",
                ["important", "urgent"],
                id="2つのタグが返された場合、2つのタグが設定されること",
            ),
            pytest.param(
                "important\nurgent\ndraft\ntodo\n",
                ["important", "urgent", "draft", "todo"],
                id="複数のタグが返された場合、全てのタグが設定されること",
            ),
            pytest.param(
                "tag1\ntag2\ntag3\ntag4\ntag5\ntag6\ntag7\n",
                ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"],
                id="多数のタグが返された場合、全てのタグが設定されること",
            ),
        ],
    )
    def test_processes_multiple_tags_correctly(
        self, mock_stdout: str, expected_tags: list[str]
    ) -> None:
        # Given
        cwd = Path("/test/dir")

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_tags(cwd)

        # Then
        result_data = json.loads(result)
        assert result_data["tags"] == expected_tags

    @pytest.mark.parametrize(
        "mock_stdout,expected_tags",
        [
            pytest.param(
                "tag-with-dash\n",
                ["tag-with-dash"],
                id="ハイフンを含むタグが正しく処理されること",
            ),
            pytest.param(
                "tag_with_underscore\n",
                ["tag_with_underscore"],
                id="アンダースコアを含むタグが正しく処理されること",
            ),
            pytest.param(
                "tag.with.dot\n",
                ["tag.with.dot"],
                id="ドットを含むタグが正しく処理されること",
            ),
            pytest.param(
                "tag-with-dash\ntag_with_underscore\ntag.with.dot\n",
                ["tag-with-dash", "tag_with_underscore", "tag.with.dot"],
                id="特殊文字を含む複数のタグが正しく処理されること",
            ),
            pytest.param(
                "tag@email.com\n",
                ["tag@email.com"],
                id="アットマークを含むタグが正しく処理されること",
            ),
            pytest.param(
                "tag#hash\n",
                ["tag#hash"],
                id="ハッシュを含むタグが正しく処理されること",
            ),
        ],
    )
    def test_processes_tags_with_special_characters_correctly(
        self, mock_stdout: str, expected_tags: list[str]
    ) -> None:
        # Given
        cwd = Path("/test/dir")

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_tags(cwd)

        # Then
        result_data = json.loads(result)
        assert result_data["tags"] == expected_tags

    @pytest.mark.parametrize(
        "mock_stdout,expected_tags",
        [
            pytest.param("重要\n", ["重要"], id="日本語タグが正しく処理されること"),
            pytest.param(
                "重要\n緊急\n下書き\n",
                ["重要", "緊急", "下書き"],
                id="複数の日本語タグが正しく処理されること",
            ),
            pytest.param(
                "タグ📝\n", ["タグ📝"], id="絵文字を含むタグが正しく処理されること"
            ),
            pytest.param(
                "English\n日本語\n한국어\n",
                ["English", "日本語", "한국어"],
                id="複数言語のタグが正しく処理されること",
            ),
            pytest.param(
                "タグ with spaces\n",
                ["タグ with spaces"],
                id="スペースを含むタグが正しく処理されること",
            ),
        ],
    )
    def test_processes_tags_with_unicode_characters_correctly(
        self, mock_stdout: str, expected_tags: list[str]
    ) -> None:
        # Given
        cwd = Path("/test/dir")

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_tags(cwd)

        # Then
        result_data = json.loads(result)
        assert result_data["tags"] == expected_tags

    @pytest.mark.parametrize(
        "mock_stdout,expected_tags",
        [
            pytest.param(
                "tag1\ntag2\ntag3\n",
                ["tag1", "tag2", "tag3"],
                id="末尾に改行がある場合、正しく処理されること",
            ),
            pytest.param(
                "tag1\ntag2\ntag3",
                ["tag1", "tag2", "tag3"],
                id="末尾に改行がない場合、正しく処理されること",
            ),
            pytest.param(
                "tag1\ntag2\ntag3\n\n",
                ["tag1", "tag2", "tag3"],
                id="末尾に複数の改行がある場合、正しく処理されること",
            ),
            pytest.param(
                "\ntag1\ntag2\ntag3\n",
                ["tag1", "tag2", "tag3"],
                id="先頭に改行がある場合、正しく処理されること",
            ),
        ],
    )
    def test_handles_newlines_correctly(
        self, mock_stdout: str, expected_tags: list[str]
    ) -> None:
        # Given
        cwd = Path("/test/dir")

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_tags(cwd)

        # Then
        result_data = json.loads(result)
        assert result_data["tags"] == expected_tags

    @pytest.mark.parametrize(
        "mock_stdout,expected_tags",
        [
            pytest.param(
                "tag1\n\ntag2\n\ntag3\n",
                ["tag1", "", "tag2", "", "tag3"],
                id="空行が含まれる場合、空文字列として処理されること",
            ),
            pytest.param(
                "tag1\n  \ntag2\n",
                ["tag1", "  ", "tag2"],
                id="空白のみの行が含まれる場合、空白文字列として処理されること",
            ),
            pytest.param(
                "\n\ntag1\n\n",
                ["tag1"],
                id="先頭と末尾に空行がある場合、空文字列として処理されること",
            ),
        ],
    )
    def test_handles_empty_lines_correctly(
        self, mock_stdout: str, expected_tags: list[str]
    ) -> None:
        # Given
        cwd = Path("/test/dir")

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_tags(cwd)

        # Then
        result_data = json.loads(result)
        assert result_data["tags"] == expected_tags

    @pytest.mark.parametrize(
        "cwd",
        [
            pytest.param(Path("/test/dir"), id="通常のパスが正しく処理されること"),
            pytest.param(
                Path("/another/test/dir"), id="別のパスが正しく処理されること"
            ),
            pytest.param(
                Path("/home/user/notes"),
                id="ユーザーディレクトリのパスが正しく処理されること",
            ),
            pytest.param(
                Path("/tmp/zk-test"), id="一時ディレクトリのパスが正しく処理されること"
            ),
            pytest.param(
                Path("/path with spaces"), id="スペースを含むパスが正しく処理されること"
            ),
            pytest.param(
                Path("/日本語パス"), id="日本語を含むパスが正しく処理されること"
            ),
        ],
    )
    def test_processes_various_cwd_paths_correctly(self, cwd: Path) -> None:
        # Given
        mock_stdout = "tag1\ntag2\n"

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_tags(cwd)

        # Then
        result_data = json.loads(result)
        assert result_data["tags"] == ["tag1", "tag2"]

    def test_serializes_json_correctly(self) -> None:
        """JSONシリアライズが正しく実行されること"""
        # Given
        cwd = Path("/test/dir")
        mock_stdout = "tag1\ntag2\n"

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_tags(cwd)

        # Then
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert "tags" in result_data
        assert isinstance(result_data["tags"], list)
        assert result_data["tags"] == ["tag1", "tag2"]

    def test_sets_zk_command_format_correctly(self) -> None:
        """zkコマンドのフォーマットが正しく設定されること"""
        # Given
        cwd = Path("/test/dir")
        mock_stdout = "tag1\n"

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            get_tags(cwd)

        # Then
        expected_command = ["zk", "tag", "list", "--format", "{{name}}"]
        mock_run.assert_called_once_with(
            expected_command,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            check=True,
        )

    @pytest.mark.parametrize(
        "command_part",
        [
            pytest.param("zk", id="zkコマンドが正しく設定されること"),
            pytest.param("tag", id="tagサブコマンドが正しく設定されること"),
            pytest.param("list", id="listサブコマンドが正しく設定されること"),
            pytest.param("--format", id="formatオプションが正しく設定されること"),
            pytest.param("{{name}}", id="nameフォーマットが正しく設定されること"),
        ],
    )
    def test_sets_individual_command_parts_correctly(self, command_part: str) -> None:
        # Given
        cwd = Path("/test/dir")
        mock_stdout = "tag1\n"

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            get_tags(cwd)

        # Then
        called_command = mock_run.call_args[0][0]
        assert command_part in called_command

    @pytest.mark.parametrize(
        "subprocess_param,expected_value",
        [
            pytest.param(
                "capture_output", True, id="capture_outputが正しく設定されること"
            ),
            pytest.param("text", True, id="textが正しく設定されること"),
            pytest.param("check", True, id="checkが正しく設定されること"),
        ],
    )
    def test_calls_subprocess_with_correct_parameters(
        self, subprocess_param: str, expected_value: bool
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        mock_stdout = "tag1\n"

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            get_tags(cwd)

        # Then
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs[subprocess_param] == expected_value
