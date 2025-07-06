def _validate_directory(directory: str) -> str:
    """ディレクトリ名の安全性を検証し、コマンドインジェクション攻撃を防ぐ。

    Args:
        directory: 検証するディレクトリ名

    Returns:
        str: 検証済みの安全なディレクトリ名

    Raises:
        ValueError: ディレクトリ名が安全でない場合
    """
    # 空文字列の場合は許可
    if not directory:
        return directory

    # ディレクトリ名の長さ制限
    if len(directory) > 200:
        raise ValueError("ディレクトリ名が長すぎます")

    # 危険な文字をチェック
    dangerous_chars = [
        ";",
        "&",
        "|",
        "`",
        "$",
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        ">",
        "<",
        "!",
        "~",
        "*",
        "?",
        '"',
        "'",
        "\\",
    ]
    for char in dangerous_chars:
        if char in directory:
            raise ValueError(f"ディレクトリ名に危険な文字が含まれています: {char}")

    # パストラバーサル防止
    if ".." in directory or directory.startswith("/"):
        raise ValueError("ディレクトリ名にパストラバーサルが検出されました")

    # 制御文字チェック
    if any(ord(char) < 32 for char in directory):
        raise ValueError("ディレクトリ名に制御文字が含まれています")

    return directory
