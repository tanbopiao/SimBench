"""In-process concurrent task-queue simulation.

Distilled from simulation_test.py (which drove a live HTTP scheduler with
5 workers × 30 tasks). Here the queue is a plain object with the same
claim/complete protocol, so the same assertions — no pending residue,
terminal-state closure, persisted-count match, stats consistency — run
offline and deterministically (fail-rate injectable).
"""
from __future__ import annotations

import threading
from typing import Callable, Dict, List, Optional


class TaskQueue:
    """Minimal scheduler core: submit / claim / complete with stats."""

    def __init__(self, capabilities: Optional[Dict[str, List[str]]] = None):
        self._lock = threading.Lock()
        self._seq = 0
        self.tasks: Dict[str, Dict] = {}
        self.workers: Dict[str, Dict] = {}
        self._caps = capabilities or {}

    # -- API (mirrors the upstream HTTP endpoints) --------------------------
    def register_worker(self, worker_id: str, *, capabilities: Optional[List[str]] = None,
                        max_concurrent: int = 2) -> str:
        with self._lock:
            self.workers[worker_id] = {"capabilities": capabilities or [],
                                       "max_concurrent": max_concurrent,
                                       "in_flight": 0}
            return worker_id

    def submit(self, task_type: str, priority: int = 1,
               payload: Optional[Dict] = None) -> str:
        with self._lock:
            self._seq += 1
            tid = f"task-{self._seq:05d}"
            self.tasks[tid] = {"task_id": tid, "task_type": task_type,
                               "priority": priority, "payload": payload or {},
                               "status": "pending"}
            return tid

    def claim(self, worker_id: str) -> Optional[Dict]:
        with self._lock:
            w = self.workers.get(worker_id)
            if not w or w["in_flight"] >= w["max_concurrent"]:
                return None
            pending = [t for t in self.tasks.values()
                       if t["status"] == "pending"]
            if not pending:
                return None
            pending.sort(key=lambda t: (-t["priority"], t["task_id"]))
            t = pending[0]
            t["status"] = "claimed"
            t["worker"] = worker_id
            w["in_flight"] += 1
            return dict(t)

    def complete(self, task_id: str, *, ok: bool,
                 result: Optional[Dict] = None, error: Optional[str] = None) -> bool:
        with self._lock:
            t = self.tasks.get(task_id)
            if not t or t["status"] != "claimed":
                return False
            t["status"] = "completed" if ok else "failed"
            t["result"], t["error"] = result, error
            w = self.workers.get(t.get("worker", ""))
            if w:
                w["in_flight"] -= 1
            return True

    def stats(self) -> Dict[str, int]:
        with self._lock:
            s = {"pending": 0, "claimed": 0, "completed": 0, "failed": 0}
            for t in self.tasks.values():
                s[t["status"]] = s.get(t["status"], 0) + 1
            return s


def run_simulation(n_workers: int = 5, n_tasks: int = 30,
                   fail_rate_fn: Optional[Callable[[], bool]] = None,
                   work_fn: Optional[Callable[[], None]] = None) -> Dict:
    """Run one full production-line simulation and assert closure.

    ``fail_rate_fn`` — return True to fail the task (default: never fail).
    Returns a machine-readable report; raises AssertionError on any broken
    invariant (pending residue, count mismatch, stats divergence).
    """
    import time

    q = TaskQueue()
    workers = [q.register_worker(f"sim-w{i:02d}", max_concurrent=2)
               for i in range(n_workers)]
    task_ids = [q.submit("video_render", priority=(i % 3) + 1)
                for i in range(n_tasks)]

    counted = {"completed": 0, "failed": 0}
    lock = threading.Lock()

    def worker_loop(wid: str) -> None:
        while True:
            claim = q.claim(wid)
            if claim is None:
                return
            if work_fn:
                work_fn()
            ok = fail_rate_fn() is False if fail_rate_fn else True
            q.complete(claim["task_id"], ok=ok,
                       result={"rendered": True} if ok else None,
                       error=None if ok else "render_timeout")
            with lock:
                counted["completed" if ok else "failed"] += 1

    threads = [threading.Thread(target=worker_loop, args=(w,)) for w in workers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    stats = q.stats()
    # ---- closure assertions (carried over verbatim from upstream) ----
    assert stats["pending"] == 0, f"pending residue: {stats['pending']}"
    assert stats["completed"] + stats["failed"] == n_tasks, "task count not closed"
    assert stats["completed"] == counted["completed"], "stats divergence (completed)"
    assert stats["failed"] == counted["failed"], "stats divergence (failed)"
    assert len(q.tasks) == n_tasks, "persisted count mismatch"

    return {"workers": n_workers, "tasks": n_tasks,
            "completed": stats["completed"], "failed": stats["failed"],
            "success_rate": round(stats["completed"] / n_tasks * 100, 1),
            "pending_residue": stats["pending"],
            "persisted": len(q.tasks), "assertions": "ALL_PASSED",
            "elapsed_hint": time.strftime("%Y-%m-%dT%H:%M:%S")}
