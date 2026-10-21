import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from simbench import TaskQueue, run_simulation, run_matrix
from simbench.engines import CaseMatrix


class TestTaskQueue(unittest.TestCase):
    def test_claim_priority_and_exhaust(self):
        q = TaskQueue()
        q.register_worker("w", max_concurrent=10)
        q.submit("t", priority=1)
        hi = q.submit("t", priority=3)
        c = q.claim("w")
        self.assertEqual(c["task_id"], hi)

    def test_complete_state_machine(self):
        q = TaskQueue()
        q.register_worker("w")
        tid = q.submit("t")
        self.assertFalse(q.complete(tid, ok=True))   # not claimed yet
        q.claim("w")
        self.assertTrue(q.complete(tid, ok=False, error="x"))
        self.assertEqual(q.stats()["failed"], 1)

    def test_max_concurrent(self):
        q = TaskQueue()
        q.register_worker("w", max_concurrent=1)
        q.submit("t"); q.submit("t")
        self.assertIsNotNone(q.claim("w"))
        self.assertIsNone(q.claim("w"))              # capacity full


class TestSimulation(unittest.TestCase):
    def test_all_pass(self):
        r = run_simulation(n_workers=4, n_tasks=20)
        self.assertEqual(r["assertions"], "ALL_PASSED")
        self.assertEqual(r["success_rate"], 100.0)

    def test_with_failures(self):
        seq = iter([True, False] * 50)
        r = run_simulation(n_workers=4, n_tasks=30,
                           fail_rate_fn=lambda: next(seq))
        self.assertEqual(r["completed"] + r["failed"], 30)
        self.assertGreater(r["failed"], 0)

    def test_deterministic_closure(self):
        for _ in range(3):
            r = run_simulation(n_workers=2, n_tasks=8)
            self.assertEqual(r["pending_residue"], 0)


class TestMatrix(unittest.TestCase):
    UPSTREAM = {
        "truths": 32765, "nodes": 6, "services": 33, "sla_api": 100.0,
        "rag_idx": 32077, "gpu": True, "write_plane": "verified",
        "lock_times": 8, "cot_consistency": 100.0,
        "arbiter": "ok", "api_online": True, "health_ok": True,
        "autonomy_level": "Lv9", "gap_detect": True,
        "self_consistency": True, "drill_count": 3, "resource_pool": True,
        "roadmap": True, "engine_target": 86, "node_heartbeat": "alive",
        "sync_ok": True, "degrade_ok": True, "sla_heartbeat": "5/5",
        "healing_ok": True, "breaker_ok": True, "energy_ok": True,
        "rollback_ok": True, "steady_state": True, "metrics_ok": True,
        "anomaly_ok": True, "trace_ok": True, "capacity_ok": True,
        "latency_ok": True, "alert_ok": True, "scheduler_ok": True,
        "persist_ok": True, "retry_ok": True, "idempotent_ok": True,
        "timeout_ok": True, "stats_ok": True,
    }

    def test_full_matrix_all_pass(self):
        r = run_matrix(self.UPSTREAM)
        self.assertEqual(r["engines"], 6)
        self.assertEqual(r["cases"], 60)
        self.assertEqual(r["verdict"], "ALL_SUPPORTED")
        self.assertEqual(r["pass_rate"], 100.0)

    def test_gap_detection(self):
        s = dict(self.UPSTREAM, gpu=False)
        r = run_matrix(s)
        self.assertEqual(r["verdict"], "GAPS_FOUND")
        self.assertEqual(r["failed"], 3)   # gpu-backed cases

    def test_custom_matrix(self):
        m = CaseMatrix({"a": 1}).expect("E", "c1", "a")
        r = m.run()
        self.assertEqual(r["pass_rate"], 100.0)


if __name__ == "__main__":
    unittest.main()
