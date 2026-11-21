import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str


class DockerSandbox:
    def __init__(self, image: str = "python:3.13-slim") -> None:
        self.image = image

    async def run(self, command: str, timeout: float = 15) -> SandboxResult:
        args = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            "64",
            self.image,
            "sh",
            "-c",
            command,
        ]
        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
        except TimeoutError:
            process.kill()
            await process.wait()
            raise TimeoutError("sandbox timed out") from None
        return SandboxResult(process.returncode or 0, stdout.decode(), stderr.decode())
