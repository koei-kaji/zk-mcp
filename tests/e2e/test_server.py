import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

import src.zk_mcp.server as server


class TestServer:
    """server.py のE2Eテスト"""

    def setup_method(self) -> None:
        """各テストメソッドの前に実行される設定"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_zk_dir = Path(self.temp_dir)

    def test_returns_note_paths_when_called_with_include_str(self) -> None:
        """include_strを指定してget_note_paths関数を呼び出した場合、正しい結果が返されること"""
        # Given
        include_str = ["test"]
        expected_result = (
            '{"notes": [{"path": "test.md", "title": "Test", "tags": ["tag1"]}]}'
        )

        # When
        with (
            patch("src.zk_mcp.tools.get_note_paths") as mock_get_note_paths,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_get_note_paths.return_value = expected_result
            result = server.get_note_paths(include_str=include_str)

        # Then
        assert result == expected_result
        mock_get_note_paths.assert_called_once_with(
            self.test_zk_dir,
            None,
            include_str,
            "AND",
            [],
            [],
            "AND",
            [],
        )

    def test_passes_default_parameters_to_get_note_paths_when_no_arguments_given(
        self,
    ) -> None:
        """引数を指定しない場合、get_note_paths関数にデフォルトパラメータが渡されること"""
        # Given
        expected_result = '{"notes": []}'

        # When
        with (
            patch("src.zk_mcp.tools.get_note_paths") as mock_get_note_paths,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_get_note_paths.return_value = expected_result
            result = server.get_note_paths()

        # Then
        assert result == expected_result
        mock_get_note_paths.assert_called_once_with(
            self.test_zk_dir,
            None,
            [],
            "AND",
            [],
            [],
            "AND",
            [],
        )

    def test_returns_linking_notes_when_called_with_valid_path(self) -> None:
        """有効なパスを指定してget_linking_notes関数を呼び出した場合、正しい結果が返されること"""
        # Given
        path = "test.md"
        expected_result = (
            '{"link_to_notes": [], "linked_by_notes": [], "related_notes": []}'
        )

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes") as mock_get_linking_notes,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_get_linking_notes.return_value = expected_result
            result = server.get_linking_notes(path)

        # Then
        assert result == expected_result
        mock_get_linking_notes.assert_called_once_with(self.test_zk_dir, path)

    def test_returns_tags_when_get_tags_function_is_called(self) -> None:
        """get_tags関数を呼び出した場合、正しい結果が返されること"""
        # Given
        expected_result = '{"tags": ["tag1", "tag2", "tag3"]}'

        # When
        with (
            patch("src.zk_mcp.tools.get_tags") as mock_get_tags,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_get_tags.return_value = expected_result
            result = server.get_tags()

        # Then
        assert result == expected_result
        mock_get_tags.assert_called_once_with(self.test_zk_dir)

    def test_returns_note_content_when_called_with_valid_path(self) -> None:
        """有効なパスを指定してget_note関数を呼び出した場合、正しい結果が返されること"""
        # Given
        path = "test.md"
        expected_result = "# Test Note\n\nThis is a test note."

        # When
        with (
            patch("src.zk_mcp.tools.get_note") as mock_get_note,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_get_note.return_value = expected_result
            result = server.get_note(path)

        # Then
        assert result == expected_result
        mock_get_note.assert_called_once_with(self.test_zk_dir, path)

    def test_creates_note_when_called_with_title_and_empty_directory(self) -> None:
        """タイトルと空のディレクトリを指定してcreate_note関数を呼び出した場合、正しい結果が返されること"""
        # Given
        title = "New Note"
        directory = ""
        expected_result = '{"path": "new-note.md", "title": "New Note"}'

        # When
        with (
            patch("src.zk_mcp.tools.create_note") as mock_create_note,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_create_note.return_value = expected_result
            result = server.create_note(title, directory)

        # Then
        assert result == expected_result
        mock_create_note.assert_called_once_with(self.test_zk_dir, title, directory)

    def test_creates_note_when_called_with_title_and_directory(self) -> None:
        """タイトルとディレクトリを指定してcreate_note関数を呼び出した場合、正しい結果が返されること"""
        # Given
        title = "New Note"
        directory = "sub"
        expected_result = '{"path": "sub/new-note.md", "title": "New Note"}'

        # When
        with (
            patch("src.zk_mcp.tools.create_note") as mock_create_note,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_create_note.return_value = expected_result
            result = server.create_note(title, directory)

        # Then
        assert result == expected_result
        mock_create_note.assert_called_once_with(self.test_zk_dir, title, directory)

    @pytest.mark.parametrize(
        (
            "include_str, include_str_operand, exclude_str, "
            "include_tags, include_tags_operand, exclude_tags"
        ),
        [
            pytest.param(
                ["test"],
                "AND",
                [],
                [],
                "AND",
                [],
                id="include_strのみを指定した場合、正しくパラメータが渡されること",
            ),
            pytest.param(
                [],
                "AND",
                ["draft"],
                [],
                "AND",
                [],
                id="exclude_strのみを指定した場合、正しくパラメータが渡されること",
            ),
            pytest.param(
                [],
                "AND",
                [],
                ["important"],
                "AND",
                [],
                id="include_tagsのみを指定した場合、正しくパラメータが渡されること",
            ),
            pytest.param(
                [],
                "AND",
                [],
                [],
                "AND",
                ["temp"],
                id="exclude_tagsのみを指定した場合、正しくパラメータが渡されること",
            ),
            pytest.param(
                ["test"],
                "OR",
                ["draft"],
                ["important"],
                "OR",
                ["temp"],
                id="全てのパラメータを指定した場合、正しくパラメータが渡されること",
            ),
        ],
    )
    def test_passes_various_parameters_to_get_note_paths_correctly(
        self,
        include_str: list[str],
        include_str_operand: str,
        exclude_str: list[str],
        include_tags: list[str],
        include_tags_operand: str,
        exclude_tags: list[str],
    ) -> None:
        # Given
        expected_result = '{"notes": []}'

        # When
        with (
            patch("src.zk_mcp.tools.get_note_paths") as mock_get_note_paths,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_get_note_paths.return_value = expected_result
            result = server.get_note_paths(
                include_str=include_str,
                include_str_operand=include_str_operand,
                exclude_str=exclude_str,
                include_tags=include_tags,
                include_tags_operand=include_tags_operand,
                exclude_tags=exclude_tags,
            )

        # Then
        assert result == expected_result
        mock_get_note_paths.assert_called_once_with(
            self.test_zk_dir,
            None,
            include_str,
            include_str_operand,
            exclude_str,
            include_tags,
            include_tags_operand,
            exclude_tags,
        )

    @pytest.mark.parametrize(
        "path",
        [
            pytest.param(
                "note.md", id="単一ファイルのパスである場合、正しく動作すること"
            ),
            pytest.param(
                "sub/note.md", id="サブディレクトリのパスである場合、正しく動作すること"
            ),
            pytest.param(
                "deep/sub/note.md",
                id="深いサブディレクトリのパスである場合、正しく動作すること",
            ),
            pytest.param(
                "note with spaces.md",
                id="スペースを含むパスである場合、正しく動作すること",
            ),
            pytest.param(
                "日本語ノート.md", id="日本語を含むパスである場合、正しく動作すること"
            ),
        ],
    )
    def test_processes_various_path_patterns_for_get_linking_notes_correctly(
        self, path: str
    ) -> None:
        # Given
        expected_result = (
            '{"link_to_notes": [], "linked_by_notes": [], "related_notes": []}'
        )

        # When
        with (
            patch("src.zk_mcp.tools.get_linking_notes") as mock_get_linking_notes,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_get_linking_notes.return_value = expected_result
            result = server.get_linking_notes(path)

        # Then
        assert result == expected_result
        mock_get_linking_notes.assert_called_once_with(self.test_zk_dir, path)

    @pytest.mark.parametrize(
        "path",
        [
            pytest.param(
                "note.md", id="単一ファイルのパスである場合、正しく動作すること"
            ),
            pytest.param(
                "sub/note.md", id="サブディレクトリのパスである場合、正しく動作すること"
            ),
            pytest.param(
                "deep/sub/note.md",
                id="深いサブディレクトリのパスである場合、正しく動作すること",
            ),
            pytest.param(
                "note with spaces.md",
                id="スペースを含むパスである場合、正しく動作すること",
            ),
            pytest.param(
                "日本語ノート.md", id="日本語を含むパスである場合、正しく動作すること"
            ),
        ],
    )
    def test_processes_various_path_patterns_for_get_note_correctly(
        self, path: str
    ) -> None:
        # Given
        expected_result = "Note content"

        # When
        with (
            patch("src.zk_mcp.tools.get_note") as mock_get_note,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_get_note.return_value = expected_result
            result = server.get_note(path)

        # Then
        assert result == expected_result
        mock_get_note.assert_called_once_with(self.test_zk_dir, path)

    @pytest.mark.parametrize(
        "title, directory",
        [
            pytest.param(
                "Simple Title",
                "",
                id="英語のタイトルと空のディレクトリである場合、正しく動作すること",
            ),
            pytest.param(
                "タイトル",
                "",
                id="日本語のタイトルと空のディレクトリである場合、正しく動作すること",
            ),
            pytest.param(
                "Title with spaces",
                "sub",
                id="スペースを含むタイトルとサブディレクトリである場合、正しく動作すること",
            ),
            pytest.param(
                "Another Title",
                "deep/sub",
                id="タイトルと深いサブディレクトリである場合、正しく動作すること",
            ),
        ],
    )
    def test_creates_note_with_various_parameters_correctly(
        self, title: str, directory: str
    ) -> None:
        # Given
        path_part = f"{directory}/" if directory else ""
        filename = f"{title.lower().replace(' ', '-')}.md"
        expected_result = f'{{"path": "{path_part}{filename}", "title": "{title}"}}'

        # When
        with (
            patch("src.zk_mcp.tools.create_note") as mock_create_note,
            patch("src.zk_mcp.server.settings.zk_dir", self.test_zk_dir),
        ):
            mock_create_note.return_value = expected_result
            result = server.create_note(title, directory)

        # Then
        assert result == expected_result
        mock_create_note.assert_called_once_with(self.test_zk_dir, title, directory)

    def test_uses_settings_object_correctly(self) -> None:
        """Settingsオブジェクトが正しく使用されること"""
        # Given
        expected_result = '{"notes": []}'

        # When
        with (
            patch("src.zk_mcp.tools.get_note_paths") as mock_get_note_paths,
            patch("src.zk_mcp.server.settings") as mock_settings,
        ):
            mock_settings.zk_dir = self.test_zk_dir
            mock_get_note_paths.return_value = expected_result
            server.get_note_paths()

        # Then
        mock_get_note_paths.assert_called_once_with(
            self.test_zk_dir,
            None,
            [],
            "AND",
            [],
            [],
            "AND",
            [],
        )

    def test_imports_tools_module_correctly(self) -> None:
        """toolsモジュールが正しくインポートされること"""
        # Given, When, Then
        assert hasattr(server, "tools")
        assert hasattr(server.tools, "get_note_paths")
        assert hasattr(server.tools, "get_linking_notes")
        assert hasattr(server.tools, "get_tags")
        assert hasattr(server.tools, "get_note")
        assert hasattr(server.tools, "create_note")

    def test_imports_settings_module_correctly(self) -> None:
        """settingsモジュールが正しくインポートされること"""
        # Given, When, Then
        assert hasattr(server, "settings")
        assert hasattr(server.settings, "zk_dir")

    def test_initializes_mcp_object_correctly(self) -> None:
        """mcpオブジェクトが正しく初期化されること"""
        # Given, When, Then
        assert hasattr(server, "mcp")
        assert server.mcp is not None

    def test_registers_all_tool_functions_as_mcp_tools(self) -> None:
        """全てのツール関数がmcpツールとして登録されていること"""
        # Given, When, Then
        # FastMCPのツール登録は@mcp.tool()デコレータで行われるため
        # 関数が存在し呼び出し可能であることを確認
        assert callable(server.get_note_paths)
        assert callable(server.get_linking_notes)
        assert callable(server.get_tags)
        assert callable(server.get_note)
        assert callable(server.create_note)
