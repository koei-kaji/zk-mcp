def _validate_title(title: str) -> str:
    """タイトルの安全性を検証し、コマンドインジェクション攻撃を防ぐ。

    Args:
        title: 検証するタイトル

    Returns:
        str: 検証済みの安全なタイトル

    Raises:
        ValueError: タイトルが安全でない場合
    """
    # 空文字列チェック
    if not title or not title.strip():
        raise ValueError("タイトルが空です")

    # タイトルの長さ制限
    if len(title) > 500:
        raise ValueError("タイトルが長すぎます")

    # 制御文字チェック
    if any(ord(char) < 32 for char in title if char not in ["\t", "\n", "\r"]):
        raise ValueError("タイトルに制御文字が含まれています")

    return title
