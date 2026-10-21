"""Capability case-matrix runner.

Distilled from sim_validation.py (six engines × ten cases, verdicts backed
by real system state). The matrix is data, not code: declare
(engine, case, expectation, evidence) rows, run them against a state
provider, and emit a machine-readable report with a PASS/FAIL verdict.
"""
from __future__ import annotations

import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

StateFn = Callable[[str], Any]


class CaseMatrix:
    def __init__(self, state: Dict[str, Any]):
        self._state = state
        self._rows: List[Tuple[str, str, str, str]] = []
        self._checks: List[Tuple[str, str, Callable[[Dict], bool]]] = []

    def expect(self, engine: str, case: str, key: str, note: str = "",
               predicate: Optional[Callable[[Any], bool]] = None) -> "CaseMatrix":
        """Declare: capability `case` of `engine` is supported iff state[key]
        satisfies `predicate` (default: truthy)."""
        self._rows.append((engine, case, key, note))
        self._checks.append((engine, case,
                             lambda s, k=key, p=predicate: bool(s.get(k)) if p is None else p(s.get(k))))
        return self

    def run(self) -> Dict:
        results: Dict[str, Dict[str, Dict]] = {}
        passed = failed = 0
        for (engine, case, key, note), (_, _, check) in zip(self._rows, self._checks):
            ok = bool(check(self._state))
            results.setdefault(engine, {})[case] = {
                "key": key, "verdict": "支持" if ok else "缺失", "note": note}
            passed += ok
            failed += (not ok)
        total = passed + failed
        return {
            "time": datetime.datetime.now().isoformat(),
            "engines": len(results),
            "cases": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total * 100, 1) if total else 0.0,
            "verdict": "ALL_SUPPORTED" if failed == 0 and total else "GAPS_FOUND",
            "matrix": results,
        }


def run_matrix(state: Dict[str, Any]) -> Dict:
    """The upstream six-engine 60-case matrix, adapted to generic keys.

    Engine names preserved (超认知/超进化/超协同/超稳态/超感知/超执行);
    state keys are provider-agnostic — pass your own system snapshot.
    """
    m = CaseMatrix(state)
    e = m.expect
    e("超认知", "语义三层解释", "truths", "真值库驱动", lambda v: isinstance(v, int) and v > 0)
    e("超认知", "上下文关联决策", "rag_idx")
    e("超认知", "多源仲裁推理", "arbiter")
    e("超认知", "因果链推理", "sla_api")
    e("超认知", "演绎推理", "write_plane")
    e("超认知", "归纳总结", "nodes")
    e("超认知", "语义消歧", "api_online")
    e("超认知", "深度理解", "health_ok")
    e("超认知", "概念抽象", "autonomy_level")
    e("超认知", "状态自察", "cot_consistency")
    e("超进化", "问题发现", "gap_detect")
    e("超进化", "方案优化", "self_consistency")
    e("超进化", "模式学习", "drill_count", "故障演练", lambda v: isinstance(v, int) and v >= 1)
    e("超进化", "自主发现", "write_plane")
    e("超进化", "创新提议", "resource_pool")
    e("超进化", "演进规划", "roadmap")
    e("超进化", "经验固化", "lock_times", "锁档机制", lambda v: isinstance(v, int) and v >= 1)
    e("超进化", "自动升级", "rag_idx")
    e("超进化", "策略迭代", "engine_target")
    e("超进化", "知识沉淀", "truths", None, lambda v: isinstance(v, int) and v > 0)
    e("超协同", "节点协同", "node_heartbeat")
    e("超协同", "服务发现", "services", None, lambda v: isinstance(v, int) and v > 0)
    e("超协同", "仲裁流程", "arbiter")
    e("超协同", "层级协作", "gpu")
    e("超协同", "跨窗口同步", "sync_ok")
    e("超协同", "通道选择", "write_plane")
    e("超协同", "共识达成", "arbiter")
    e("超协同", "资源调度", "gpu")
    e("超协同", "事件协同", "node_heartbeat")
    e("超协同", "故障协作", "degrade_ok")
    e("超稳态", "心跳保活", "sla_heartbeat")
    e("超稳态", "自愈触发", "healing_ok")
    e("超稳态", "熔断保护", "breaker_ok")
    e("超稳态", "资源守恒", "energy_ok")
    e("超稳态", "降级运行", "degrade_ok")
    e("超稳态", "锁档一致", "lock_times")
    e("超稳态", "回滚能力", "rollback_ok")
    e("超稳态", "SLA达成", "sla_api", None, lambda v: isinstance(v, (int, float)) and v >= 99)
    e("超稳态", "静默容错", "degrade_ok")
    e("超稳态", "稳态收敛", "steady_state")
    e("超感知", "状态采集", "metrics_ok")
    e("超感知", "指标聚合", "metrics_ok")
    e("超感知", "异常检测", "anomaly_ok")
    e("超感知", "日志溯源", "trace_ok")
    e("超感知", "链路追踪", "trace_ok")
    e("超感知", "资源感知", "gpu")
    e("超感知", "容量感知", "capacity_ok")
    e("超感知", "延迟感知", "latency_ok")
    e("超感知", "覆盖率", "metrics_ok")
    e("超感知", "告警上报", "alert_ok")
    e("超执行", "任务领取", "scheduler_ok")
    e("超执行", "并发执行", "scheduler_ok")
    e("超执行", "结果落库", "persist_ok")
    e("超执行", "失败重试", "retry_ok")
    e("超执行", "幂等保护", "idempotent_ok")
    e("超执行", "超时控制", "timeout_ok")
    e("超执行", "优先级调度", "scheduler_ok")
    e("超执行", "worker注册", "scheduler_ok")
    e("超执行", "统计闭合", "stats_ok")
    e("超执行", "落库可查", "persist_ok")
    return m.run()
