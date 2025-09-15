import subprocess
from pathlib import Path

from ..._base_models.base_model import BaseFrozenModel


class ZkClient(BaseFrozenModel):
    cwd: Path

    def get_lists(
        self,
        fmt: str = "",
        conditions: list[str] = [],
    ) -> list[str]:
        try:
            command = [
                "zk",
                "list",
                "--quiet",
                "--sort",
                "title",
                "--format",
                fmt,
            ]
            stdout = subprocess.run(
                [*command, *conditions],
                capture_output=True,
                text=True,
                cwd=self.cwd,
                check=True,
            )
            return stdout.stdout.strip().splitlines()

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error: {e.stderr}") from e

    def get_title(self, path: Path) -> str:
        command = [
            "zk",
            "list",
            "--quiet",
            "--format",
            "{{title}}",
            str(path),
        ]

        try:
            stdout = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self.cwd,
                check=True,
            )
            return stdout.stdout

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error: {e.stderr}") from e

    def get_content(self, path: Path) -> str:
        command = [
            "zk",
            "list",
            "--quiet",
            "--format",
            "{{raw-content}}",
            str(path),
        ]

        try:
            stdout = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self.cwd,
                check=True,
            )
            return stdout.stdout

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error: {e.stderr}") from e
