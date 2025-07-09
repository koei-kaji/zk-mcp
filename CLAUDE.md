# CLAUDE.md

## プロジェクト概要

これは`zk`プレーンテキストノート取りシステムと統合するMCP（Model Context Protocol）サーバーです。このサーバーはLLMがzkで管理されたナレッジベースにアクセスしクエリを実行するためのツールを提供します。

## 主要コマンド

### 開発
- `make run` - ZK_DIR=.でMCPサーバーを開発モードで実行
- `make format` - ruffを使用してコードをフォーマット（インポート + フォーマット）
- `make lint` - ruffでリント、mypyで型チェックを実行
- `make test` - テストを実行（開発依存関係のpytestを使用）
- `make pre-commit` - formatとlintの両方を実行（コミット前推奨）

### パッケージ管理
- `uv add <package>` - ランタイム依存関係を追加
- `uv add --dev <package>` - 開発依存関係を追加
- `uv run <command>` - 仮想環境でコマンドを実行

## アーキテクチャ

### コアコンポーネント

1. **server.py** - FastMCPを使用したメインのMCPサーバー実装
   - 5つのMCPツールを定義: `get_note_paths`, `get_linking_notes`, `get_tags`, `get_note`, `create_note`
   - `zk` CLIとのやり取りにsubprocessを使用
   - 全ツールはPydanticモデルを使用してJSONレスポンスを返す

2. **tools/** - 各MCPツールの実装
   - `get_note_paths.py` - 複雑なフィルタリングでノートをクエリ
   - `get_linking_notes.py` - ノートのリンク関係を分析
   - `get_tags.py` - 利用可能なタグをリスト
   - `get_note.py` - 特定のノートの内容を読み取り
   - `create_note.py` - 新しいノートを作成
   - `models.py` - APIレスポンス用のPydanticデータモデル

3. **settings.py** - pydantic-settingsを使用した設定
   - `zk_dir` - zkノートディレクトリへのパス（ZK_DIR環境変数で設定）

### MCPツール

#### `get_note_paths()`
複雑なフィルタリングでノートをクエリ：
- `include_str` - コンテンツまたはファイル名に含まれる文字列でフィルタ
- `include_str_operand` - 複数の文字列フィルタの論理演算子（AND/OR）
- `exclude_str` - 特定の文字列を含むノートを除外
- `include_tags` - タグでフィルタ
- `include_tags_operand` - 複数のタグフィルタの論理演算子（AND/OR）
- `exclude_tags` - 特定のタグを持つノートを除外

#### `get_linking_notes(path)`
特定のノートのリンク関係を分析：
- `link_to_notes` - 指定されたノートがリンクしているノート
- `linked_by_notes` - 指定されたノートにリンクしているノート
- `related_notes` - 指定されたノートと関連するノート

#### `get_tags()`
ノートブック内の利用可能なタグをすべてリスト

#### `get_note(path)`
特定のノートの完全なコンテンツを読み取り

#### `create_note(title, directory)`
新しいノートを作成（オプションでディレクトリを指定）

### 依存関係

- **ランタイム**: `mcp[cli]>=1.6.0`, `pydantic-settings>=2.8.1`
- **開発**: `mypy>=1.15.0`, `pytest>=8.3.5`, `ruff>=0.11.5`

## 構成

サーバーには以下が必要：
1. `zk` CLIツールがインストールされPATHに含まれていること
2. zkノートディレクトリを指す`ZK_DIR`環境変数
3. MCPクライアント設定（servers.json設定についてはREADME.mdを参照）

### MCPクライアント設定例
```json
{
  "mcpServers": {
    "zk": {
      "alwaysAllow": [
        "get_note",
        "get_note_paths",
        "get_linking_notes",
        "get_tags",
        "create_note"
      ],
      "args": [
        "--directory",
        "/path/to/zk-mcp/",
        "run",
        "server.py"
      ],
      "command": "uv",
      "env": {
        "ZK_DIR": "/path/to/your/zk-note-directory/"
      }
    }
  }
}
```

## コードスタイル

- リントとフォーマットにruffを使用
- mypyで型ヒントを強制
- ドキュメント用にserver.pyに日本語コメント

## テストスタイル

- テストメソッド名は英語で記述
- pytest.mark.parametrizeを積極的に使用
- parametrizeのパターンは `pytest.param(..., id="AAAである場合、BBBであること")` の形式で日本語説明を付与
- parametrizeを使用していないテストメソッドには日本語のdocstringを追加してテスト内容を説明
