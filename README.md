# SimBench

> **Offline, deterministic simulation harness for agent schedulers and capability claims.**
>
> 调度器量产仿真 + 六引擎能力用例矩阵——离线、确定性、零依赖。

[English](#english) | [中文](#中文)

---

## English

When you claim "my agent scheduler sustains 30 concurrent tasks with zero pending residue" or "all six capability engines are supported", that claim is only as good as the harness behind it. SimBench distills the ZONGYUAN-ROOT verification harnesses into a dependency-free library:

| Harness | What it proves |
|---|---|
| **`scheduler`** | In-process concurrent queue: N workers × M tasks with claim/complete protocol; asserts **terminal-state closure** (no pending residue), **count consistency** (claimed+failed == submitted), **stats divergence** (per-thread counters match global stats), **persistence** (every task queryable) |
| **`engines`** | Six-engine × 10-case capability matrix (超认知/超进化/超协同/超稳态/超感知/超执行) evaluated against your real system snapshot → machine-readable `ALL_SUPPORTED` / `GAPS_FOUND` verdict |

### Design principles (carried over from upstream)

- **Deterministic**: no network, no sleeps-as-logic; failure rate is injectable, so CI runs are reproducible
- **Assertions are the product**: the value is not "it ran" but the four closure invariants that must hold
- **Data, not code**: the capability matrix is declared rows — add your own engine/case without touching the runner

### 60-second tour

```python
from simbench import run_simulation, run_matrix

# 1. Scheduler simulation — 5 workers, 30 tasks, ~10% failures
report = run_simulation(n_workers=5, n_tasks=30,
                        fail_rate_fn=lambda: random.random() < 0.1)
assert report["assertions"] == "ALL_PASSED"
print(report["success_rate"])        # e.g. 90.0

# 2. Capability matrix — pass YOUR system snapshot
state = {"truths": 32765, "nodes": 6, "sla_api": 100.0, "gpu": True, ...}
verdict = run_matrix(state)
print(verdict["verdict"])            # ALL_SUPPORTED / GAPS_FOUND
print(verdict["pass_rate"])          # 100.0
```

Requirements: Python 3.10+, **zero dependencies**.

---

## 中文

当你声称「调度器可承载 30 个并发任务且零 pending 残留」「六引擎能力全部支持」时，这种声称的价值取决于背后的验证基准。SimBench 将 ZONGYUAN-ROOT 的仿真验证机制提炼为零依赖库：

| 基准 | 验证什么 |
|---|---|
| **`scheduler`** | 进程内并发队列：N worker × M 任务，claim/complete 协议；断言**终态闭合**（无 pending 残留）、**计数闭合**（完成+失败=提交）、**统计一致**（线程本地计数与全局统计吻合）、**落库可查** |
| **`engines`** | 六引擎 × 10 用例能力矩阵（超认知/超进化/超协同/超稳态/超感知/超执行），对照真实系统快照评估 → 机器可读判定 `ALL_SUPPORTED` / `GAPS_FOUND` |

### 设计原则（承袭上游）

- **确定性**：无网络、无 sleep 即逻辑；失败率可注入，CI 可复现
- **断言即产品**：价值不在「跑过」，而在四条必须成立的闭合不变式
- **数据非代码**：能力矩阵是声明式行——新增引擎/用例无需改运行器

### 快速上手

```python
from simbench import run_simulation, run_matrix

report = run_simulation(n_workers=5, n_tasks=30,
                        fail_rate_fn=lambda: random.random() < 0.1)
assert report["assertions"] == "ALL_PASSED"

state = {"truths": 32765, "nodes": 6, "sla_api": 100.0, "gpu": True, ...}
verdict = run_matrix(state)
print(verdict["verdict"], verdict["pass_rate"])
```

依赖：Python 3.10+，**零第三方依赖**。

---

## 来源与治理

- 本仓库从 [ZONGYUAN-ROOT](https://atomgit.com/zongyuangen/ZONGYUAN-ROOT)（branch `converge-20260928`）提炼：`07_代码与脚本/simulation_test.py` · `sim_validation.py`
- 提炼中移除：硬编码本地服务端点（`127.0.0.1:8310`）、私有沙盒输出路径；HTTP 调度器改为进程内等价协议，六引擎判定矩阵改为通用状态键
- 遵循「元极恒一」治理规范：基准资产只读、衍生独立建库
- 许可：Apache-2.0
---

> **种子档归一**（2026-11-03 谳定）：本仓原随附的 `YUANSHEN-SEED.md` / `YUANSHEN-SEED.json` 已归一至 [Replicore 种子正仓](https://github.com/tanbopiao/Replicore)，正本唯一，本仓不再另存副本。
