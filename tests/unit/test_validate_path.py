from pathlib import Path

import pytest

from src.zk_mcp.tools._validate_path import _validate_path


class TestValidatePath:
    """_validate_path 関数のテスト"""

    @pytest.mark.parametrize(
        "path",
        [
            pytest.param(
                "test.md", id="単一ファイルパスである場合、パスが返されること"
            ),
            pytest.param(
                "sub/test.md", id="サブディレクトリのパスである場合、パスが返されること"
            ),
        ],
    )
    def test_returns_path_when_valid_path_is_given(self, path: str) -> None:
        # Given
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            if "/" in path:
                sub_dir = base_dir / "sub"
                sub_dir.mkdir()
                test_file = sub_dir / "test.md"
                test_file.touch()
            else:
                test_file = base_dir / path
                test_file.touch()

            # When
            result = _validate_path(path, base_dir)

            # Then
            assert result == base_dir / path

    @pytest.mark.parametrize(
        "path,expected_error",
        [
            pytest.param(
                "", "パスが空です", id="空文字である場合、ValueError が発生すること"
            ),
            pytest.param(
                "   ",
                "パスが空です",
                id="空白文字のみである場合、ValueError が発生すること",
            ),
            pytest.param(
                "a" * 1001,
                "パスが長すぎます",
                id="1001文字以上である場合、ValueError が発生すること",
            ),
            pytest.param(
                "../outside.md",
                "指定されたパスはzkディレクトリ外です",
                id="親ディレクトリへの相対パスである場合、ValueError が発生すること",
            ),
            pytest.param(
                "/absolute/path.md",
                "指定されたパスはzkディレクトリ外です",
                id="絶対パスである場合、ValueError が発生すること",
            ),
        ],
    )
    def test_raises_value_error_when_invalid_path_is_given(
        self, path: str, expected_error: str
    ) -> None:
        # Given
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)

            # When, Then
            with pytest.raises(ValueError, match=expected_error):
                _validate_path(path, base_dir)

    @pytest.mark.parametrize(
        "dangerous_path",
        [
            pytest.param(
                "../../../etc/passwd",
                id="複数階層上のパスである場合、ValueError が発生すること",
            ),
            pytest.param(
                "../../outside.md",
                id="2階層上のパスである場合、ValueError が発生すること",
            ),
            pytest.param(
                "/etc/passwd",
                id="システムファイルの絶対パスである場合、ValueError が発生すること",
            ),
            pytest.param(
                "/tmp/outside.md",
                id="外部ディレクトリの絶対パスである場合、ValueError が発生すること",
            ),
        ],
    )
    def test_raises_value_error_when_dangerous_path_is_given(
        self, dangerous_path: str
    ) -> None:
        # Given
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)

            # When, Then
            with pytest.raises(
                ValueError, match="指定されたパスはzkディレクトリ外です"
            ):
                _validate_path(dangerous_path, base_dir)

    @pytest.mark.parametrize(
        "valid_path",
        [
            pytest.param(
                "note.md", id="単純なファイル名である場合、パスが返されること"
            ),
            pytest.param(
                "sub/note.md",
                id="サブディレクトリのファイルパスである場合、パスが返されること",
            ),
            pytest.param(
                "deep/sub/note.md",
                id="深いサブディレクトリのファイルパスである場合、パスが返されること",
            ),
            pytest.param(
                "note-with-dash.md",
                id="ダッシュが含まれるファイル名である場合、パスが返されること",
            ),
            pytest.param(
                "note_with_underscore.md",
                id="アンダースコアが含まれるファイル名である場合、パスが返されること",
            ),
            pytest.param(
                "note with spaces.md",
                id="スペースが含まれるファイル名である場合、パスが返されること",
            ),
            pytest.param(
                "123.md", id="数字のみのファイル名である場合、パスが返されること"
            ),
        ],
    )
    def test_returns_path_when_various_valid_paths_are_given(
        self, valid_path: str
    ) -> None:
        # Given
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)

            # When
            result = _validate_path(valid_path, base_dir)

            # Then
            assert result == base_dir / valid_path

    @pytest.mark.parametrize(
        "path",
        [
            pytest.param("a" * 1000, id="1000文字のパスである場合、パスが返されること"),
            pytest.param(
                "sub/../note.md", id="相対パス形式である場合、パスが返されること"
            ),
        ],
    )
    def test_returns_path_when_other_valid_paths_are_given(self, path: str) -> None:
        # Given
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)

            # When
            result = _validate_path(path, base_dir)

            # Then
            assert result == base_dir / path
