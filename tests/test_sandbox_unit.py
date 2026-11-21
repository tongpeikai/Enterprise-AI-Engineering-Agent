import asyncio

import pytest

from backend.app.tools.sandbox import DockerSandbox


class _Process:
    returncode = 0

    async def communicate(self) -> tuple[bytes, bytes]:
        return b"ok", b""

    async def wait(self) -> None:
        return None

    def kill(self) -> None:
        return None


class _BlockedProcess(_Process):
    async def communicate(self) -> tuple[bytes, bytes]:
        await asyncio.sleep(1)
        return b"", b""


@pytest.mark.asyncio
async def test_sandbox_command_result_is_normalized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_spawn(*args: object, **kwargs: object) -> _Process:
        return _Process()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_spawn)
    result = await DockerSandbox().run("printf ok")
    assert result.exit_code == 0
    assert result.stdout == "ok"
    assert result.stderr == ""


@pytest.mark.asyncio
async def test_sandbox_timeout_cancels_process(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_spawn(*args: object, **kwargs: object) -> _Process:
        return _BlockedProcess()
    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_spawn)
    with pytest.raises(TimeoutError, match="sandbox timed out"):
        await DockerSandbox().run("sleep 1", timeout=0.001)
