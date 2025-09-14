from pathlib import Path


def _validate_path(path: str, base_dir: Path) -> Path:
    """パスの安全性を検証し、ディレクトリトラバーサル攻撃を防ぐ。

    Args:
        path: 検証するパス文字列

    Returns:
        Path: 検証済みの安全なパス

    Raises:
        ValueError: パスが安全でない場合
    """
    # 空文字列チェック
    if not path or not path.strip():
        raise ValueError("パスが空です")

    # パス長制限
    if len(path) > 1000:
        raise ValueError("パスが長すぎます")

    # 相対パスに変換
    normalized_path = (base_dir / path).resolve()
    zk_dir_resolved = base_dir.resolve()

    # zkディレクトリ内のパスかチェック
    try:
        normalized_path.relative_to(zk_dir_resolved)
    except ValueError:
        raise ValueError("指定されたパスはzkディレクトリ外です")

    # 実際のファイルパスを返す
    return base_dir / path
