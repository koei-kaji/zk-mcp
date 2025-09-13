import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.zk_mcp.tools.get_linking_notes import get_linking_notes
from src.zk_mcp.tools.models import Note


class TestGetLinkingNotes:
    """get_linking_notes 関数のテスト"""

    def test_returns_linking_notes_when_valid_path_is_given(self) -> None:
        """正常なパスが与えられた場合、リンクノート情報が返されること"""
        # Given
        cwd = Path("/test/dir")
        path = "note1.md"

        link_to_notes = [Note(path=Path("linked1.md"), title="Linked 1", tags=[])]
        linked_by_notes = [Note(path=Path("linker1.md"), title="Linker 1", tags=[])]
        related_notes = [Note(path=Path("related1.md"), title="Related 1", tags=[])]

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes._validate_path") as mock_validate,
            patch("src.zk_mcp.tools.get_linking_notes.get_notes") as mock_get_notes,
        ):
            mock_validate.return_value = cwd / path
            mock_get_notes.side_effect = [link_to_notes, linked_by_notes, related_notes]

            result = get_linking_notes(cwd, path)

        # Then
        result_data = json.loads(result)
        assert len(result_data["link_to_notes"]) == 1
        assert len(result_data["linked_by_notes"]) == 1
        assert len(result_data["related_notes"]) == 1
        assert result_data["link_to_notes"][0]["path"] == "linked1.md"
        assert result_data["linked_by_notes"][0]["path"] == "linker1.md"
        assert result_data["related_notes"][0]["path"] == "related1.md"

        mock_validate.assert_called_once_with(path, cwd)
        assert mock_get_notes.call_count == 3

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
            "src.zk_mcp.tools.get_linking_notes._validate_path",
            side_effect=validation_error,
        ):
            with pytest.raises(RuntimeError, match=f"無効なパス: {validation_error}"):
                get_linking_notes(cwd, path)

    def test_executes_three_zk_commands_correctly(self) -> None:
        """3つのzkコマンドが正しく実行されること"""
        # Given
        cwd = Path("/test/dir")
        path = "note1.md"

        mock_notes = [Note(path=Path("test.md"), title="Test", tags=[])]

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes._validate_path") as mock_validate,
            patch("src.zk_mcp.tools.get_linking_notes.get_notes") as mock_get_notes,
        ):
            mock_validate.return_value = cwd / path
            mock_get_notes.return_value = mock_notes

            get_linking_notes(cwd, path)

        # Then
        expected_calls = [
            ((cwd, ["--link-to", path]),),
            ((cwd, ["--linked-by", path]),),
            ((cwd, ["--related", path]),),
        ]
        assert mock_get_notes.call_count == 3
        for i, expected_call in enumerate(expected_calls):
            assert mock_get_notes.call_args_list[i].args == expected_call[0]

    def test_sets_empty_lists_when_no_linking_notes_found(self) -> None:
        """空のリンクノートが返された場合、空のリストが設定されること"""
        # Given
        cwd = Path("/test/dir")
        path = "note1.md"
        empty_notes: list[Note] = []

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes._validate_path") as mock_validate,
            patch("src.zk_mcp.tools.get_linking_notes.get_notes") as mock_get_notes,
        ):
            mock_validate.return_value = cwd / path
            mock_get_notes.return_value = empty_notes

            result = get_linking_notes(cwd, path)

        # Then
        result_data = json.loads(result)
        assert result_data["link_to_notes"] == []
        assert result_data["linked_by_notes"] == []
        assert result_data["related_notes"] == []

    @pytest.mark.parametrize(
        "link_to_count,linked_by_count,related_count",
        [
            pytest.param(
                2,
                1,
                3,
                id="複数のリンクノートが返された場合、全てのノートが設定されること",
            ),
            pytest.param(
                1,
                1,
                1,
                id="単一のリンクノートが返された場合、全てのノートが設定されること",
            ),
            pytest.param(
                5,
                2,
                1,
                id="異なる数のリンクノートが返された場合、全てのノートが設定されること",
            ),
            pytest.param(
                0, 3, 2, id="一部のリンクタイプが空の場合、適切に設定されること"
            ),
        ],
    )
    def test_sets_all_notes_when_multiple_linking_notes_found(
        self, link_to_count: int, linked_by_count: int, related_count: int
    ) -> None:
        # Given
        cwd = Path("/test/dir")
        path = "note1.md"

        link_to_notes = [
            Note(path=Path(f"linked{i}.md"), title=f"Linked {i}", tags=[f"tag{i}"])
            for i in range(1, link_to_count + 1)
        ]
        linked_by_notes = [
            Note(path=Path(f"linker{i}.md"), title=f"Linker {i}", tags=[f"tag{i + 10}"])
            for i in range(1, linked_by_count + 1)
        ]
        related_notes = [
            Note(
                path=Path(f"related{i}.md"), title=f"Related {i}", tags=[f"tag{i + 20}"]
            )
            for i in range(1, related_count + 1)
        ]

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes._validate_path") as mock_validate,
            patch("src.zk_mcp.tools.get_linking_notes.get_notes") as mock_get_notes,
        ):
            mock_validate.return_value = cwd / path
            mock_get_notes.side_effect = [link_to_notes, linked_by_notes, related_notes]

            result = get_linking_notes(cwd, path)

        # Then
        result_data = json.loads(result)
        assert len(result_data["link_to_notes"]) == link_to_count
        assert len(result_data["linked_by_notes"]) == linked_by_count
        assert len(result_data["related_notes"]) == related_count

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
        ],
    )
    def test_processes_various_path_patterns_correctly(self, path: str) -> None:
        # Given
        cwd = Path("/test/dir")
        mock_notes = [Note(path=Path("test.md"), title="Test", tags=[])]

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes._validate_path") as mock_validate,
            patch("src.zk_mcp.tools.get_linking_notes.get_notes") as mock_get_notes,
        ):
            mock_validate.return_value = cwd / path
            mock_get_notes.return_value = mock_notes

            result = get_linking_notes(cwd, path)

        # Then
        mock_validate.assert_called_once_with(path, cwd)
        assert mock_get_notes.call_count == 3
        result_data = json.loads(result)
        assert "link_to_notes" in result_data
        assert "linked_by_notes" in result_data
        assert "related_notes" in result_data

    def test_serializes_json_correctly(self) -> None:
        """JSONシリアライズが正しく実行されること"""
        # Given
        cwd = Path("/test/dir")
        path = "note1.md"

        link_to_notes = [Note(path=Path("linked1.md"), title="Linked 1", tags=["tag1"])]
        linked_by_notes = [
            Note(path=Path("linker1.md"), title="Linker 1", tags=["tag2"])
        ]
        related_notes = [Note(path=Path("related1.md"), title="Related 1", tags=[])]

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes._validate_path") as mock_validate,
            patch("src.zk_mcp.tools.get_linking_notes.get_notes") as mock_get_notes,
        ):
            mock_validate.return_value = cwd / path
            mock_get_notes.side_effect = [link_to_notes, linked_by_notes, related_notes]

            result = get_linking_notes(cwd, path)

        # Then
        assert isinstance(result, str)
        result_data = json.loads(result)
        assert "link_to_notes" in result_data
        assert "linked_by_notes" in result_data
        assert "related_notes" in result_data
        assert result_data["link_to_notes"][0]["tags"] == ["tag1"]
        assert result_data["linked_by_notes"][0]["tags"] == ["tag2"]
        assert result_data["related_notes"][0]["tags"] == []

    def test_validates_path_correctly(self) -> None:
        """パス検証が正しく実行されること"""
        # Given
        cwd = Path("/test/dir")
        path = "note1.md"
        mock_notes = [Note(path=Path("test.md"), title="Test", tags=[])]

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes._validate_path") as mock_validate,
            patch("src.zk_mcp.tools.get_linking_notes.get_notes") as mock_get_notes,
        ):
            mock_validate.return_value = cwd / path
            mock_get_notes.return_value = mock_notes

            get_linking_notes(cwd, path)

        # Then
        mock_validate.assert_called_once_with(path, cwd)

    @pytest.mark.parametrize(
        "expected_keys",
        [
            pytest.param(
                ["link_to_notes", "linked_by_notes", "related_notes"],
                id="全てのリンクタイプが正しく設定されること",
            ),
        ],
    )
    def test_sets_link_types_correctly(self, expected_keys: list[str]) -> None:
        # Given
        cwd = Path("/test/dir")
        path = "note1.md"

        link_to_notes = [Note(path=Path("linked1.md"), title="Linked 1", tags=[])]
        linked_by_notes = [Note(path=Path("linker1.md"), title="Linker 1", tags=[])]
        related_notes = [Note(path=Path("related1.md"), title="Related 1", tags=[])]

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes._validate_path") as mock_validate,
            patch("src.zk_mcp.tools.get_linking_notes.get_notes") as mock_get_notes,
        ):
            mock_validate.return_value = cwd / path
            mock_get_notes.side_effect = [link_to_notes, linked_by_notes, related_notes]

            result = get_linking_notes(cwd, path)

        # Then
        result_data = json.loads(result)
        assert set(result_data.keys()) == set(expected_keys)
        assert isinstance(result_data["link_to_notes"], list)
        assert isinstance(result_data["linked_by_notes"], list)
        assert isinstance(result_data["related_notes"], list)

    @pytest.mark.parametrize(
        "command_option",
        [
            pytest.param("--link-to", id="link-toオプションが正しく設定されること"),
            pytest.param("--linked-by", id="linked-byオプションが正しく設定されること"),
            pytest.param("--related", id="relatedオプションが正しく設定されること"),
        ],
    )
    def test_sets_zk_command_options_correctly(self, command_option: str) -> None:
        # Given
        cwd = Path("/test/dir")
        path = "note1.md"
        mock_notes = [Note(path=Path("test.md"), title="Test", tags=[])]

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes._validate_path") as mock_validate,
            patch("src.zk_mcp.tools.get_linking_notes.get_notes") as mock_get_notes,
        ):
            mock_validate.return_value = cwd / path
            mock_get_notes.return_value = mock_notes

            get_linking_notes(cwd, path)

        # Then
        assert mock_get_notes.call_count == 3
        command_options = [call.args[1][0] for call in mock_get_notes.call_args_list]
        assert command_option in command_options
