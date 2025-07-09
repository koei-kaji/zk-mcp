import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tools.create_note import create_note


class TestCreateNote:
    """create_note 関数のテスト"""

    def test_creates_note_when_valid_title_is_given(self):
        """正常なタイトルが与えられた場合、ノートが作成されること"""
        # Given
        cwd = Path("/test/dir")
        title = "Test Note"
        mock_created_path = "/test/dir/test-note.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_created_path
        mock_result.returncode = 0

        # When
        with (
            patch(
                "tools.create_note._validate_title", return_value=title
            ) as mock_validate_title,
            patch(
                "tools.create_note._validate_directory", return_value=""
            ) as mock_validate_dir,
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            result = create_note(cwd, title)

        # Then
        result_data = json.loads(result)
        assert result_data["title"] == title
        assert result_data["path"] == "test-note.md"

        mock_validate_title.assert_called_once_with(title)
        mock_validate_dir.assert_called_once_with("")
        mock_run.assert_called_once_with(
            ["zk", "new", "--print-path", "--title", title],
            capture_output=True,
            text=True,
            cwd=str(cwd),
            check=True,
        )

    def test_creates_note_in_directory_when_directory_is_specified(self):
        """ディレクトリが指定された場合、ディレクトリ内にノートが作成されること"""
        # Given
        cwd = Path("/test/dir")
        title = "Test Note"
        directory = "sub"
        mock_created_path = "/test/dir/sub/test-note.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_created_path
        mock_result.returncode = 0

        # When
        with (
            patch(
                "tools.create_note._validate_title", return_value=title
            ) as mock_validate_title,
            patch(
                "tools.create_note._validate_directory", return_value=directory
            ) as mock_validate_dir,
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            result = create_note(cwd, title, directory)

        # Then
        result_data = json.loads(result)
        assert result_data["title"] == title
        assert result_data["path"] == "sub/test-note.md"

        mock_validate_title.assert_called_once_with(title)
        mock_validate_dir.assert_called_once_with(directory)
        mock_run.assert_called_once_with(
            ["zk", "new", "--print-path", "--title", title, directory],
            capture_output=True,
            text=True,
            cwd=str(cwd),
            check=True,
        )

    @pytest.mark.parametrize(
        "title,validation_error",
        [
            pytest.param(
                "",
                ValueError("タイトルが空です"),
                id="空のタイトルである場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "",
                ValueError("タイトルが長すぎます"),
                id="長すぎるタイトルである場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "",
                ValueError("タイトルに制御文字が含まれています"),
                id="制御文字を含むタイトルである場合、RuntimeError が発生すること",
            ),
        ],
    )
    def test_raises_runtime_error_when_title_validation_fails(
        self, title, validation_error
    ):
        # Given
        cwd = Path("/test/dir")

        # When, Then
        with patch("tools.create_note._validate_title", side_effect=validation_error):
            with pytest.raises(RuntimeError, match=f"入力値エラー: {validation_error}"):
                create_note(cwd, title)

    @pytest.mark.parametrize(
        "directory,validation_error",
        [
            pytest.param(
                "../invalid",
                ValueError("無効なディレクトリ"),
                id="無効なディレクトリである場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "very_long_directory_name",
                ValueError("ディレクトリ名が長すぎます"),
                id="長すぎるディレクトリ名である場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "dir;",
                ValueError("ディレクトリ名に危険な文字が含まれています"),
                id="危険な文字を含むディレクトリ名である場合、RuntimeError が発生すること",
            ),
        ],
    )
    def test_raises_runtime_error_when_directory_validation_fails(
        self, directory, validation_error
    ):
        # Given
        cwd = Path("/test/dir")
        title = "Test Note"

        # When, Then
        with (
            patch("tools.create_note._validate_title", return_value=title),
            patch(
                "tools.create_note._validate_directory", side_effect=validation_error
            ),
        ):
            with pytest.raises(RuntimeError, match=f"入力値エラー: {validation_error}"):
                create_note(cwd, title, directory)

    @pytest.mark.parametrize(
        "error_message",
        [
            pytest.param(
                "Failed to create note",
                id="zkコマンドが失敗した場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "Permission denied",
                id="権限エラーが発生した場合、RuntimeError が発生すること",
            ),
            pytest.param(
                "Directory not found",
                id="ディレクトリが見つからない場合、RuntimeError が発生すること",
            ),
        ],
    )
    def test_raises_runtime_error_when_zk_command_fails(self, error_message):
        # Given
        cwd = Path("/test/dir")
        title = "Test Note"

        mock_error = subprocess.CalledProcessError(1, ["zk"])
        mock_error.stderr = error_message

        # When, Then
        with (
            patch("tools.create_note._validate_title", return_value=title),
            patch("tools.create_note._validate_directory", return_value=""),
            patch("subprocess.run", side_effect=mock_error),
        ):
            with pytest.raises(
                RuntimeError, match=f"ノート作成エラー: {error_message}"
            ):
                create_note(cwd, title)

    def test_calculates_relative_path_correctly(self):
        """相対パスが正しく計算されること"""
        # Given
        cwd = Path("/test/dir")
        title = "Test Note"
        mock_created_path = "/test/dir/sub/deep/test-note.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_created_path
        mock_result.returncode = 0

        # When
        with (
            patch("tools.create_note._validate_title", return_value=title),
            patch("tools.create_note._validate_directory", return_value=""),
            patch("subprocess.run", return_value=mock_result),
        ):
            result = create_note(cwd, title)

        # Then
        result_data = json.loads(result)
        assert result_data["path"] == "sub/deep/test-note.md"

    @pytest.mark.parametrize(
        "title,expected_title",
        [
            pytest.param(
                "Simple Title",
                "Simple Title",
                id="英語タイトルである場合、正しく処理されること",
            ),
            pytest.param(
                "タイトル",
                "タイトル",
                id="日本語タイトルである場合、正しく処理されること",
            ),
            pytest.param(
                "Title with spaces",
                "Title with spaces",
                id="スペースを含むタイトルである場合、正しく処理されること",
            ),
            pytest.param(
                "Title-with-dash",
                "Title-with-dash",
                id="ハイフンを含むタイトルである場合、正しく処理されること",
            ),
            pytest.param(
                "Title_with_underscore",
                "Title_with_underscore",
                id="アンダースコアを含むタイトルである場合、正しく処理されること",
            ),
            pytest.param(
                "123456",
                "123456",
                id="数字のみのタイトルである場合、正しく処理されること",
            ),
            pytest.param(
                "Mixed123日本語",
                "Mixed123日本語",
                id="混在文字のタイトルである場合、正しく処理されること",
            ),
        ],
    )
    def test_processes_various_title_patterns_correctly(self, title, expected_title):
        # Given
        cwd = Path("/test/dir")
        mock_created_path = "/test/dir/note.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_created_path
        mock_result.returncode = 0

        # When
        with (
            patch(
                "tools.create_note._validate_title", return_value=expected_title
            ) as mock_validate_title,
            patch("tools.create_note._validate_directory", return_value=""),
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            result = create_note(cwd, title)

        # Then
        result_data = json.loads(result)
        assert result_data["title"] == expected_title

        mock_validate_title.assert_called_once_with(title)
        mock_run.assert_called_once_with(
            ["zk", "new", "--print-path", "--title", expected_title],
            capture_output=True,
            text=True,
            cwd=str(cwd),
            check=True,
        )

    @pytest.mark.parametrize(
        "directory,expected_directory",
        [
            pytest.param("", "", id="空のディレクトリである場合、正しく処理されること"),
            pytest.param(
                "sub", "sub", id="サブディレクトリである場合、正しく処理されること"
            ),
            pytest.param(
                "deep/sub",
                "deep/sub",
                id="深いサブディレクトリである場合、正しく処理されること",
            ),
            pytest.param(
                "sub-dir",
                "sub-dir",
                id="ハイフンを含むディレクトリである場合、正しく処理されること",
            ),
            pytest.param(
                "sub_dir",
                "sub_dir",
                id="アンダースコアを含むディレクトリである場合、正しく処理されること",
            ),
        ],
    )
    def test_processes_various_directory_patterns_correctly(
        self, directory, expected_directory
    ):
        # Given
        cwd = Path("/test/dir")
        title = "Test Note"
        if expected_directory:
            mock_created_path = f"/test/dir/{expected_directory}/note.md"
        else:
            mock_created_path = "/test/dir/note.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_created_path
        mock_result.returncode = 0

        # When
        with (
            patch("tools.create_note._validate_title", return_value=title),
            patch(
                "tools.create_note._validate_directory", return_value=expected_directory
            ) as mock_validate_dir,
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            create_note(cwd, title, directory)

        # Then
        mock_validate_dir.assert_called_once_with(directory)

        if expected_directory:
            expected_command = [
                "zk",
                "new",
                "--print-path",
                "--title",
                title,
                expected_directory,
            ]
        else:
            expected_command = ["zk", "new", "--print-path", "--title", title]

        mock_run.assert_called_once_with(
            expected_command,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            check=True,
        )

    def test_serializes_json_correctly(self):
        """JSONシリアライズが正しく実行されること"""
        # Given
        cwd = Path("/test/dir")
        title = "Test Note"
        mock_created_path = "/test/dir/test-note.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_created_path
        mock_result.returncode = 0

        # When
        with (
            patch("tools.create_note._validate_title", return_value=title),
            patch("tools.create_note._validate_directory", return_value=""),
            patch("subprocess.run", return_value=mock_result),
        ):
            result = create_note(cwd, title)

        # Then
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert "path" in result_data
        assert "title" in result_data
        assert result_data["path"] == "test-note.md"
        assert result_data["title"] == title

    @pytest.mark.parametrize(
        "directory,expected_command",
        [
            pytest.param(
                "",
                ["zk", "new", "--print-path", "--title", "Test Note"],
                id="ディレクトリが空である場合、正しいコマンドが設定されること",
            ),
            pytest.param(
                "sub",
                ["zk", "new", "--print-path", "--title", "Test Note", "sub"],
                id="ディレクトリが指定された場合、正しいコマンドが設定されること",
            ),
            pytest.param(
                "deep/sub",
                ["zk", "new", "--print-path", "--title", "Test Note", "deep/sub"],
                id="深いディレクトリが指定された場合、正しいコマンドが設定されること",
            ),
        ],
    )
    def test_sets_zk_command_arguments_correctly(self, directory, expected_command):
        # Given
        cwd = Path("/test/dir")
        title = "Test Note"
        mock_created_path = "/test/dir/test-note.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_created_path
        mock_result.returncode = 0

        # When
        with (
            patch("tools.create_note._validate_title", return_value=title),
            patch("tools.create_note._validate_directory", return_value=directory),
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):
            create_note(cwd, title, directory if directory else "")

        # Then
        mock_run.assert_called_once_with(
            expected_command,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            check=True,
        )

    @pytest.mark.parametrize(
        "mock_created_path,expected_path",
        [
            pytest.param(
                "/test/dir/test-note.md\n",
                "test-note.md",
                id="末尾に改行がある場合、正しく処理されること",
            ),
            pytest.param(
                "/test/dir/test-note.md\n\n",
                "test-note.md",
                id="末尾に複数の改行がある場合、正しく処理されること",
            ),
            pytest.param(
                "/test/dir/test-note.md",
                "test-note.md",
                id="末尾に改行がない場合、正しく処理されること",
            ),
            pytest.param(
                "/test/dir/sub/test-note.md\n",
                "sub/test-note.md",
                id="サブディレクトリで末尾に改行がある場合、正しく処理されること",
            ),
        ],
    )
    def test_handles_path_with_trailing_newlines_correctly(
        self, mock_created_path, expected_path
    ):
        # Given
        cwd = Path("/test/dir")
        title = "Test Note"

        mock_result = MagicMock()
        mock_result.stdout = mock_created_path
        mock_result.returncode = 0

        # When
        with (
            patch("tools.create_note._validate_title", return_value=title),
            patch("tools.create_note._validate_directory", return_value=""),
            patch("subprocess.run", return_value=mock_result),
        ):
            result = create_note(cwd, title)

        # Then
        result_data = json.loads(result)
        assert result_data["path"] == expected_path

    def test_executes_both_validations_correctly(self):
        """両方の検証が正しく実行されること"""
        # Given
        cwd = Path("/test/dir")
        title = "Test Note"
        directory = "sub"
        mock_created_path = "/test/dir/sub/test-note.md"

        mock_result = MagicMock()
        mock_result.stdout = mock_created_path
        mock_result.returncode = 0

        # When
        with (
            patch(
                "tools.create_note._validate_title", return_value=title
            ) as mock_validate_title,
            patch(
                "tools.create_note._validate_directory", return_value=directory
            ) as mock_validate_dir,
            patch("subprocess.run", return_value=mock_result),
        ):
            create_note(cwd, title, directory)

        # Then
        mock_validate_title.assert_called_once_with(title)
        mock_validate_dir.assert_called_once_with(directory)
