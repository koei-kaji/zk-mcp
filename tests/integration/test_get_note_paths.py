import json
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.get_note_paths import get_note_paths
from tools.models import Note


class TestGetNotePaths:
    """get_note_paths 関数のテスト"""

    def test_returns_all_notes_when_default_parameters_are_used(self):
        """デフォルトパラメータの場合、全てのノートが取得されること"""
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [
            Note(path=Path("note1.md"), title="Note 1", tags=["tag1"]),
            Note(path=Path("note2.md"), title="Note 2", tags=["tag2"]),
        ]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            result = get_note_paths(cwd)

        # Then
        result_data = json.loads(result)
        assert len(result_data["notes"]) == 2
        assert result_data["notes"][0]["path"] == "note1.md"
        assert result_data["notes"][0]["title"] == "Note 1"
        assert result_data["notes"][0]["tags"] == ["tag1"]

        mock_get_notes.assert_called_once_with(cwd, [])

    @pytest.mark.parametrize(
        "include_str,expected_match",
        [
            pytest.param(
                ["test"],
                "test",
                id="単一のinclude_strが指定された場合、matchオプションが追加されること",
            ),
            pytest.param(
                ["hello"],
                "hello",
                id="別の単一のinclude_strが指定された場合、matchオプションが追加されること",
            ),
            pytest.param(
                ["日本語"],
                "日本語",
                id="日本語のinclude_strが指定された場合、matchオプションが追加されること",
            ),
        ],
    )
    def test_adds_match_option_when_single_include_str_is_specified(
        self, include_str, expected_match
    ):
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [Note(path=Path("note1.md"), title="Note 1", tags=[])]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            get_note_paths(cwd, include_str=include_str)

        # Then
        mock_get_notes.assert_called_once_with(cwd, ["--match", expected_match])

    @pytest.mark.parametrize(
        "include_str,include_str_operand,expected_match",
        [
            pytest.param(
                ["test", "note"],
                "AND",
                "test note",
                id="複数のinclude_strでAND演算子が指定された場合、スペース区切りでmatchオプションが追加されること",
            ),
            pytest.param(
                ["test", "note"],
                "OR",
                "test OR note",
                id="複数のinclude_strでOR演算子が指定された場合、OR区切りでmatchオプションが追加されること",
            ),
            pytest.param(
                ["test", "note", "doc"],
                "AND",
                "test note doc",
                id="3つのinclude_strでAND演算子が指定された場合、スペース区切りでmatchオプションが追加されること",
            ),
            pytest.param(
                ["test", "note", "doc"],
                "OR",
                "test OR note OR doc",
                id="3つのinclude_strでOR演算子が指定された場合、OR区切りでmatchオプションが追加されること",
            ),
        ],
    )
    def test_adds_match_option_when_multiple_include_str_are_specified(
        self, include_str, include_str_operand, expected_match
    ):
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [Note(path=Path("note1.md"), title="Note 1", tags=[])]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            get_note_paths(
                cwd,
                include_str=include_str,
                include_str_operand=include_str_operand,
            )

        # Then
        mock_get_notes.assert_called_once_with(cwd, ["--match", expected_match])

    @pytest.mark.parametrize(
        "exclude_str,expected_match",
        [
            pytest.param(
                ["draft"],
                "draft-",
                id="単一のexclude_strが指定された場合、除外条件でmatchオプションが追加されること",
            ),
            pytest.param(
                ["draft", "temp"],
                "draft- AND temp-",
                id="複数のexclude_strが指定された場合、AND区切りで除外条件が追加されること",
            ),
            pytest.param(
                ["draft", "temp", "test"],
                "draft- AND temp- AND test-",
                id="3つのexclude_strが指定された場合、AND区切りで除外条件が追加されること",
            ),
        ],
    )
    def test_adds_exclude_match_option_when_exclude_str_is_specified(
        self, exclude_str, expected_match
    ):
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [Note(path=Path("note1.md"), title="Note 1", tags=[])]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            get_note_paths(cwd, exclude_str=exclude_str)

        # Then
        mock_get_notes.assert_called_once_with(cwd, ["--match", expected_match])

    @pytest.mark.parametrize(
        "include_tags,expected_tag",
        [
            pytest.param(
                ["important"],
                "important",
                id="単一のinclude_tagsが指定された場合、tagオプションが追加されること",
            ),
            pytest.param(
                ["urgent"],
                "urgent",
                id="別の単一のinclude_tagsが指定された場合、tagオプションが追加されること",
            ),
            pytest.param(
                ["日本語タグ"],
                "日本語タグ",
                id="日本語のinclude_tagsが指定された場合、tagオプションが追加されること",
            ),
        ],
    )
    def test_adds_tag_option_when_single_include_tags_is_specified(
        self, include_tags, expected_tag
    ):
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [
            Note(path=Path("note1.md"), title="Note 1", tags=include_tags)
        ]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            get_note_paths(cwd, include_tags=include_tags)

        # Then
        mock_get_notes.assert_called_once_with(cwd, ["--tag", expected_tag])

    @pytest.mark.parametrize(
        "include_tags,include_tags_operand,expected_tag",
        [
            pytest.param(
                ["important", "urgent"],
                "AND",
                "important, urgent",
                id="複数のinclude_tagsでAND演算子が指定された場合、カンマ区切りでtagオプションが追加されること",
            ),
            pytest.param(
                ["important", "urgent"],
                "OR",
                "important OR urgent",
                id="複数のinclude_tagsでOR演算子が指定された場合、OR区切りでtagオプションが追加されること",
            ),
            pytest.param(
                ["important", "urgent", "todo"],
                "AND",
                "important, urgent, todo",
                id="3つのinclude_tagsでAND演算子が指定された場合、カンマ区切りでtagオプションが追加されること",
            ),
            pytest.param(
                ["important", "urgent", "todo"],
                "OR",
                "important OR urgent OR todo",
                id="3つのinclude_tagsでOR演算子が指定された場合、OR区切りでtagオプションが追加されること",
            ),
        ],
    )
    def test_adds_tag_option_when_multiple_include_tags_are_specified(
        self, include_tags, include_tags_operand, expected_tag
    ):
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [
            Note(path=Path("note1.md"), title="Note 1", tags=include_tags)
        ]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            get_note_paths(
                cwd,
                include_tags=include_tags,
                include_tags_operand=include_tags_operand,
            )

        # Then
        mock_get_notes.assert_called_once_with(cwd, ["--tag", expected_tag])

    @pytest.mark.parametrize(
        "exclude_tags,expected_tag",
        [
            pytest.param(
                ["draft"],
                "-draft",
                id="単一のexclude_tagsが指定された場合、除外条件でtagオプションが追加されること",
            ),
            pytest.param(
                ["draft", "temp"],
                "-draft, -temp",
                id="複数のexclude_tagsが指定された場合、カンマ区切りで除外条件が追加されること",
            ),
            pytest.param(
                ["draft", "temp", "test"],
                "-draft, -temp, -test",
                id="3つのexclude_tagsが指定された場合、カンマ区切りで除外条件が追加されること",
            ),
        ],
    )
    def test_adds_exclude_tag_option_when_exclude_tags_is_specified(
        self, exclude_tags, expected_tag
    ):
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [Note(path=Path("note1.md"), title="Note 1", tags=[])]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            get_note_paths(cwd, exclude_tags=exclude_tags)

        # Then
        mock_get_notes.assert_called_once_with(cwd, ["--tag", expected_tag])

    def test_adds_all_options_when_all_filters_are_specified(self):
        """全てのフィルタが指定された場合、全てのオプションが追加されること"""
        # Given
        cwd = Path("/test/dir")
        include_str = ["test"]
        exclude_str = ["draft"]
        include_tags = ["important"]
        exclude_tags = ["temp"]
        mock_notes: list[Note] = [
            Note(path=Path("note1.md"), title="Note 1", tags=["important"])
        ]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            get_note_paths(
                cwd,
                include_str=include_str,
                exclude_str=exclude_str,
                include_tags=include_tags,
                exclude_tags=exclude_tags,
            )

        # Then
        mock_get_notes.assert_called_once_with(
            cwd,
            [
                "--match",
                "test",
                "--match",
                "draft-",
                "--tag",
                "important",
                "--tag",
                "-temp",
            ],
        )

    @pytest.mark.parametrize(
        "include_str,include_str_operand,expected_match",
        [
            pytest.param(
                ["test"],
                "AND",
                "test",
                id="単一のinclude_strでAND演算子が指定された場合、正しく処理されること",
            ),
            pytest.param(
                ["test"],
                "OR",
                "test",
                id="単一のinclude_strでOR演算子が指定された場合、正しく処理されること",
            ),
            pytest.param(
                ["test", "note"],
                "AND",
                "test note",
                id="複数のinclude_strでAND演算子が指定された場合、正しく処理されること",
            ),
            pytest.param(
                ["test", "note"],
                "OR",
                "test OR note",
                id="複数のinclude_strでOR演算子が指定された場合、正しく処理されること",
            ),
            pytest.param(
                ["test", "note", "doc"],
                "AND",
                "test note doc",
                id="3つのinclude_strでAND演算子が指定された場合、正しく処理されること",
            ),
            pytest.param(
                ["test", "note", "doc"],
                "OR",
                "test OR note OR doc",
                id="3つのinclude_strでOR演算子が指定された場合、正しく処理されること",
            ),
        ],
    )
    def test_processes_various_include_str_patterns_correctly(
        self, include_str, include_str_operand, expected_match
    ):
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [Note(path=Path("note1.md"), title="Note 1", tags=[])]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            get_note_paths(
                cwd, include_str=include_str, include_str_operand=include_str_operand
            )

        # Then
        mock_get_notes.assert_called_once_with(cwd, ["--match", expected_match])

    @pytest.mark.parametrize(
        "include_tags,include_tags_operand,expected_tag",
        [
            pytest.param(
                ["important"],
                "AND",
                "important",
                id="単一のinclude_tagsでAND演算子が指定された場合、正しく処理されること",
            ),
            pytest.param(
                ["important"],
                "OR",
                "important",
                id="単一のinclude_tagsでOR演算子が指定された場合、正しく処理されること",
            ),
            pytest.param(
                ["important", "urgent"],
                "AND",
                "important, urgent",
                id="複数のinclude_tagsでAND演算子が指定された場合、正しく処理されること",
            ),
            pytest.param(
                ["important", "urgent"],
                "OR",
                "important OR urgent",
                id="複数のinclude_tagsでOR演算子が指定された場合、正しく処理されること",
            ),
            pytest.param(
                ["important", "urgent", "todo"],
                "AND",
                "important, urgent, todo",
                id="3つのinclude_tagsでAND演算子が指定された場合、正しく処理されること",
            ),
            pytest.param(
                ["important", "urgent", "todo"],
                "OR",
                "important OR urgent OR todo",
                id="3つのinclude_tagsでOR演算子が指定された場合、正しく処理されること",
            ),
        ],
    )
    def test_processes_various_include_tags_patterns_correctly(
        self, include_tags, include_tags_operand, expected_tag
    ):
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [
            Note(path=Path("note1.md"), title="Note 1", tags=include_tags)
        ]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            get_note_paths(
                cwd,
                include_tags=include_tags,
                include_tags_operand=include_tags_operand,
            )

        # Then
        mock_get_notes.assert_called_once_with(cwd, ["--tag", expected_tag])

    def test_returns_empty_json_when_empty_list_is_returned(self):
        """空のリストが返された場合、空のJSONが返されること"""
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = []

        # When
        with patch("tools.get_note_paths.get_notes", return_value=mock_notes):
            result = get_note_paths(cwd)

        # Then
        result_data = json.loads(result)
        assert result_data["notes"] == []

    def test_serializes_json_correctly(self):
        """JSONシリアライズが正しく実行されること"""
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [
            Note(path=Path("note1.md"), title="Note 1", tags=["tag1", "tag2"]),
            Note(path=Path("sub/note2.md"), title="Note 2", tags=[]),
        ]

        # When
        with patch("tools.get_note_paths.get_notes", return_value=mock_notes):
            result = get_note_paths(cwd)

        # Then
        result_data = json.loads(result)
        assert isinstance(result, str)
        assert "notes" in result_data
        assert len(result_data["notes"]) == 2
        assert result_data["notes"][0]["path"] == "note1.md"
        assert result_data["notes"][0]["title"] == "Note 1"
        assert result_data["notes"][0]["tags"] == ["tag1", "tag2"]
        assert result_data["notes"][1]["path"] == "sub/note2.md"
        assert result_data["notes"][1]["title"] == "Note 2"
        assert result_data["notes"][1]["tags"] == []

    @pytest.mark.parametrize(
        "filter_combination",
        [
            pytest.param(
                {"include_str": ["test"], "include_tags": ["important"]},
                id="include_strとinclude_tagsの組み合わせが正しく処理されること",
            ),
            pytest.param(
                {"exclude_str": ["draft"], "exclude_tags": ["temp"]},
                id="exclude_strとexclude_tagsの組み合わせが正しく処理されること",
            ),
            pytest.param(
                {"include_str": ["test"], "exclude_str": ["draft"]},
                id="include_strとexclude_strの組み合わせが正しく処理されること",
            ),
            pytest.param(
                {"include_tags": ["important"], "exclude_tags": ["temp"]},
                id="include_tagsとexclude_tagsの組み合わせが正しく処理されること",
            ),
        ],
    )
    def test_processes_filter_combinations_correctly(self, filter_combination):
        # Given
        cwd = Path("/test/dir")
        mock_notes: list[Note] = [Note(path=Path("note1.md"), title="Note 1", tags=[])]

        # When
        with patch(
            "tools.get_note_paths.get_notes", return_value=mock_notes
        ) as mock_get_notes:
            get_note_paths(cwd, **filter_combination)

        # Then
        # 少なくとも1つのオプションが追加されていることを確認
        assert mock_get_notes.call_count == 1
        called_args = mock_get_notes.call_args[0][1]
        assert len(called_args) > 0
