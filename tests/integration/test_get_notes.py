import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.zk_mcp.tools.get_notes import get_notes


class TestGetNotes:
    """get_notes 関数のテスト"""

    def test_returns_note_list_when_zk_command_succeeds(self) -> None:
        """zkコマンドが成功した場合、ノートリストが返されること"""
        # Given
        cwd = Path("/test/dir")
        cmd_args: list[str] = ["--match", "test"]
        mock_stdout = "note1.md|Note 1|tag1,tag2\nnote2.md|Note 2|\n"

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_notes(cwd, cmd_args)

        # Then
        assert len(result) == 2
        assert result[0].path == Path("note1.md")
        assert result[0].title == "Note 1"
        assert result[0].tags == ["tag1", "tag2"]
        assert result[1].path == Path("note2.md")
        assert result[1].title == "Note 2"
        assert result[1].tags == []

    @pytest.mark.parametrize(
        "mock_stdout,expected_length",
        [
            pytest.param("", 0, id="空の結果が返された場合、空のリストが返されること"),
            pytest.param(
                "   ", 0, id="空白のみの結果が返された場合、空のリストが返されること"
            ),
            pytest.param(
                "\n\n", 0, id="改行のみの結果が返された場合、空のリストが返されること"
            ),
        ],
    )
    def test_returns_empty_list_when_zk_command_returns_empty_result(
        self, mock_stdout: str, expected_length: int
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        cmd_args: list[str] = []

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_notes(cwd, cmd_args)

        # Then
        assert len(result) == expected_length

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
                "Invalid argument",
                id="無効な引数エラーが発生した場合、RuntimeError が発生すること",
            ),
        ],
    )
    def test_raises_runtime_error_when_zk_command_fails(
        self, error_message: str
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        cmd_args: list[str] = ["--match", "test"]

        mock_error = subprocess.CalledProcessError(1, ["zk"])
        mock_error.stderr = error_message

        # When, Then
        with patch("subprocess.run", side_effect=mock_error):
            with pytest.raises(
                RuntimeError, match=f"zkコマンド実行エラー: {error_message}"
            ):
                get_notes(cwd, cmd_args)

    @pytest.mark.parametrize(
        "mock_stdout,expected_tags",
        [
            pytest.param(
                "note1.md|Note 1|\n",
                [],
                id="タグが空の場合、空のリストが設定されること",
            ),
            pytest.param(
                "note1.md|Note 1|tag1\n",
                ["tag1"],
                id="単一のタグが含まれる場合、タグリストが正しく設定されること",
            ),
            pytest.param(
                "note1.md|Note 1|tag1,tag2,tag3\n",
                ["tag1", "tag2", "tag3"],
                id="複数のタグが含まれる場合、タグリストが正しく分割されること",
            ),
            pytest.param(
                "note1.md|Note 1|tag1,tag2,tag3,tag4,tag5\n",
                ["tag1", "tag2", "tag3", "tag4", "tag5"],
                id="多数のタグが含まれる場合、タグリストが正しく分割されること",
            ),
        ],
    )
    def test_processes_tags_correctly(
        self, mock_stdout: str, expected_tags: list[str]
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        cmd_args: list[str] = []

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_notes(cwd, cmd_args)

        # Then
        assert len(result) == 1
        assert result[0].tags == expected_tags

    @pytest.mark.parametrize(
        "cmd_args,expected_args",
        [
            pytest.param(
                [],
                [
                    "zk",
                    "list",
                    "--quiet",
                    "--sort",
                    "modified-",
                    "--limit",
                    "50",
                    "--format",
                    '{{path}}|{{title}}|{{join tags ","}}',
                ],
                id="引数が空の場合、基本的なzkコマンドが実行されること",
            ),
            pytest.param(
                ["--match", "test"],
                [
                    "zk",
                    "list",
                    "--quiet",
                    "--sort",
                    "modified-",
                    "--limit",
                    "50",
                    "--format",
                    '{{path}}|{{title}}|{{join tags ","}}',
                    "--match",
                    "test",
                ],
                id="matchオプションが含まれる場合、正しいzkコマンドが実行されること",
            ),
            pytest.param(
                ["--tag", "important"],
                [
                    "zk",
                    "list",
                    "--quiet",
                    "--sort",
                    "modified-",
                    "--limit",
                    "50",
                    "--format",
                    '{{path}}|{{title}}|{{join tags ","}}',
                    "--tag",
                    "important",
                ],
                id="tagオプションが含まれる場合、正しいzkコマンドが実行されること",
            ),
            pytest.param(
                ["--match", "test", "--tag", "important"],
                [
                    "zk",
                    "list",
                    "--quiet",
                    "--sort",
                    "modified-",
                    "--limit",
                    "50",
                    "--format",
                    '{{path}}|{{title}}|{{join tags ","}}',
                    "--match",
                    "test",
                    "--tag",
                    "important",
                ],
                id="複数のオプションが含まれる場合、正しいzkコマンドが実行されること",
            ),
        ],
    )
    def test_executes_correct_zk_command_with_various_arguments(
        self, cmd_args: list[str], expected_args: list[str]
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        mock_stdout = "note1.md|Note 1|tag1\n"

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            get_notes(cwd, cmd_args)

        # Then
        mock_run.assert_called_once_with(
            expected_args,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True,
        )

    @pytest.mark.parametrize(
        "mock_stdout,expected_title",
        [
            pytest.param(
                "note1.md|Title with | pipe|tag1\n",
                "Title with | pipe",
                id="パイプ文字を含むタイトルが正しく処理されること",
            ),
            pytest.param(
                "note1.md|Title with || double pipe|tag1\n",
                "Title with || double pipe",
                id="複数のパイプ文字を含むタイトルが正しく処理されること",
            ),
            pytest.param(
                "note1.md|Normal Title|tag1\n",
                "Normal Title",
                id="通常のタイトルが正しく処理されること",
            ),
            pytest.param(
                "note1.md|Title with special chars @#$%|tag1\n",
                "Title with special chars @#$%",
                id="特殊文字を含むタイトルが正しく処理されること",
            ),
            pytest.param(
                "note1.md|日本語タイトル|tag1\n",
                "日本語タイトル",
                id="日本語タイトルが正しく処理されること",
            ),
        ],
    )
    def test_processes_titles_with_special_characters_correctly(
        self, mock_stdout: str, expected_title: str
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        cmd_args: list[str] = []

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_notes(cwd, cmd_args)

        # Then
        assert len(result) == 1
        assert result[0].title == expected_title

    @pytest.mark.parametrize(
        "mock_stdout,expected_count",
        [
            pytest.param(
                "note1.md|Note 1|tag1\n", 1, id="単一行の結果が正しく処理されること"
            ),
            pytest.param(
                "note1.md|Note 1|tag1\nnote2.md|Note 2|tag2\n",
                2,
                id="複数行の結果が正しく処理されること",
            ),
            pytest.param(
                "note1.md|Note 1|tag1\nnote2.md|Note 2|tag2\nnote3.md|Note 3|\n",
                3,
                id="3行の結果が正しく処理されること",
            ),
            pytest.param(
                (
                    "note1.md|Note 1|tag1\nnote2.md|Note 2|tag2\n"
                    "note3.md|Note 3|\nnote4.md|Note 4|tag4\n"
                    "note5.md|Note 5|tag5\n"
                ),
                5,
                id="多数行の結果が正しく処理されること",
            ),
        ],
    )
    def test_processes_multiple_lines_correctly(
        self, mock_stdout: str, expected_count: int
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        cmd_args: list[str] = []

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_notes(cwd, cmd_args)

        # Then
        assert len(result) == expected_count

    @pytest.mark.parametrize(
        "mock_stdout,expected_path",
        [
            pytest.param(
                "note1.md|Note 1|tag1\n",
                Path("note1.md"),
                id="単一ファイルのパスが正しく処理されること",
            ),
            pytest.param(
                "sub/note1.md|Note 1|tag1\n",
                Path("sub/note1.md"),
                id="サブディレクトリのパスが正しく処理されること",
            ),
            pytest.param(
                "sub/dir/note1.md|Note 1|tag1\n",
                Path("sub/dir/note1.md"),
                id="深いサブディレクトリのパスが正しく処理されること",
            ),
            pytest.param(
                "path with spaces/note1.md|Note 1|tag1\n",
                Path("path with spaces/note1.md"),
                id="スペースを含むパスが正しく処理されること",
            ),
            pytest.param(
                "日本語パス/note1.md|Note 1|tag1\n",
                Path("日本語パス/note1.md"),
                id="日本語を含むパスが正しく処理されること",
            ),
        ],
    )
    def test_processes_paths_with_separators_correctly(
        self, mock_stdout: str, expected_path: Path
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        cmd_args: list[str] = []

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result):
            result = get_notes(cwd, cmd_args)

        # Then
        assert len(result) == 1
        assert result[0].path == expected_path

    @pytest.mark.parametrize(
        "cmd_args",
        [
            pytest.param(
                ["--match", "test"],
                id="matchオプションが含まれる場合、正しいSubprocessが呼ばれること",
            ),
            pytest.param(
                ["--tag", "important"],
                id="tagオプションが含まれる場合、正しいSubprocessが呼ばれること",
            ),
            pytest.param(
                ["--sort", "created"],
                id="sortオプションが含まれる場合、正しいSubprocessが呼ばれること",
            ),
            pytest.param(
                ["--limit", "100"],
                id="limitオプションが含まれる場合、正しいSubprocessが呼ばれること",
            ),
        ],
    )
    def test_calls_subprocess_with_correct_parameters(
        self, cmd_args: list[str]
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        mock_stdout = "note1.md|Note 1|tag1\n"

        mock_result = MagicMock()
        mock_result.stdout = mock_stdout
        mock_result.returncode = 0

        # When
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            get_notes(cwd, cmd_args)

        # Then
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[1]["capture_output"] is True
        assert call_args[1]["text"] is True
        assert call_args[1]["cwd"] == cwd
        assert call_args[1]["check"] is True
