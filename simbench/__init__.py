"""simbench — offline simulation harness for agent scheduler & capability claims.

Distilled from ZONGYUAN-ROOT (branch converge-20260928), files:
07_代码与脚本/simulation_test.py · sim_validation.py

Two harnesses:
    scheduler — in-process concurrent task-queue simulation (N workers × M
                tasks, claim/complete protocol, terminal-state + stats
                closure assertions). No HTTP, no server needed.
    engines   — capability case-matrix runner (engine × case × expected
                verdict), producing a machine-readable verdict report.

Everything is deterministic and offline; randomness is injectable.
"""
from .scheduler import TaskQueue, run_simulation
from .engines import CaseMatrix, run_matrix

__version__ = "0.1.0"
__all__ = ["TaskQueue", "run_simulation", "CaseMatrix", "run_matrix",
           "__version__"]
