# SPDX-License-Identifier: GPL-3.0-or-later
"""Observable cross-process persistence contract for the CODEMIND guard."""

import importlib.util
import multiprocessing
from pathlib import Path


def _load_guard():
    source = Path(__file__).resolve().parents[2] / "src" / "serena" / "codemind" / "learning.py"
    spec = importlib.util.spec_from_file_location("codemind_guard_concurrency_test", source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.FailureGuard


def _record_failures(db_path: str, begin, repeats: int) -> None:
    guard = _load_guard()(Path(db_path))
    if not begin.wait(timeout=15):
        raise RuntimeError("Concurrent failure recorder start timed out")
    for _ in range(repeats):
        guard.failure("project", "find_symbol", {"name_path": "Sample"}, ValueError("same error"))


def test_equivalent_failures_are_counted_across_processes(tmp_path: Path):
    db_path = tmp_path / "failures.db"
    guard = _load_guard()(db_path)
    context = multiprocessing.get_context("spawn")
    begin = context.Event()
    workers = [context.Process(target=_record_failures, args=(str(db_path), begin, 35)) for _ in range(8)]
    try:
        for worker in workers:
            worker.start()
        begin.set()
        for worker in workers:
            worker.join(timeout=25)
        assert all(not worker.is_alive() and worker.exitcode == 0 for worker in workers)
        status = guard.status("project", "find_symbol", {"name_path": "Sample"})
        assert status["consecutive_failures"] == 280
        assert status["strategy_change_required"] is True
    finally:
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
                worker.join(timeout=5)
