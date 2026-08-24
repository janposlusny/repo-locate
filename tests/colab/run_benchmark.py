from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SOURCE = REPO_ROOT / "tests/fixtures/beam-ranking/repo"
ORACLE_PATH = REPO_ROOT / "tests/benchmarks/beam-ranking.json"
WRAPPER = REPO_ROOT / "scripts/repo-locate.sh"


def prepare_fixture(destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(FIXTURE_SOURCE, destination)
    subprocess.run(["git", "init", "-q"], cwd=destination, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=destination, check=True)
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=destination, check=True)
    subprocess.run(["git", "add", "."], cwd=destination, check=True)
    subprocess.run(["git", "commit", "-qm", "synthetic localization fixture"], cwd=destination, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the public repo-locate FastContext benchmark")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--fixture-dir", default="/tmp/repo-locate-beam-ranking")
    args = parser.parse_args()

    oracle = json.loads(ORACLE_PATH.read_text())
    required = oracle["required_files"]
    support = oracle["support_files"]
    query = oracle["query"]

    fixture = Path(args.fixture_dir).resolve()
    prepare_fixture(fixture)

    env = os.environ.copy()
    env.setdefault("BASE_URL", "http://127.0.0.1:8000/v1")
    env.setdefault("MODEL", "qwen3-fastcontext-sft")
    env.setdefault("API_KEY", "local")
    env.setdefault("FASTCONTEXT_MAX_TURNS", "8")
    env.setdefault("FASTCONTEXT_MAX_TOKENS", "4000")
    env.setdefault("FASTCONTEXT_TRAJ_DIR", "/tmp/fastcontext-trajectories")

    print("QUERY\n-----")
    print(query)
    print("\nRequired targets:", required)
    print("Support targets:", support)

    results: list[dict[str, object]] = []
    for run in range(1, args.runs + 1):
        started = time.time()
        proc = subprocess.run(
            ["bash", str(WRAPPER), query],
            cwd=fixture,
            env=env,
            text=True,
            capture_output=True,
        )
        elapsed = round(time.time() - started, 1)
        output = proc.stdout.strip()
        stderr = proc.stderr.strip()
        required_hits = {path: path in output for path in required}
        support_hits = {path: path in output for path in support}

        # FastContext catches endpoint failures and prints them as a normal final
        # answer, so the process can still exit 0. Do not count a dead server or
        # transport failure as a model/localization failure.
        infrastructure_error = (
            "LLM API call failed" in output
            or "Connection error" in output
            or proc.returncode != 0
        )
        passed = not infrastructure_error and all(required_hits.values())
        results.append(
            {
                "run": run,
                "returncode": proc.returncode,
                "seconds": elapsed,
                "required_hits": required_hits,
                "support_hits": support_hits,
                "passed": passed,
                "infrastructure_error": infrastructure_error,
            }
        )
        print(f"\n=== RUN {run} ({elapsed}s) ===")
        print(output or "<no stdout>")
        if stderr:
            print("\n[stderr tail]")
            print(stderr[-3000:])

    valid_results = [result for result in results if not result["infrastructure_error"]]
    passes = sum(bool(result["passed"]) for result in valid_results)
    errors = len(results) - len(valid_results)

    print("\nRESULTS\n=======")
    for result in results:
        req = [p for p, hit in result["required_hits"].items() if hit]
        sup = [p for p, hit in result["support_hits"].items() if hit]
        if result["infrastructure_error"]:
            status = "ERROR"
        else:
            status = "PASS" if result["passed"] else "FAIL"
        print(
            f"run {result['run']}: {status} | "
            f"required={req or 'none'} | support={sup or 'none'} | {result['seconds']}s"
        )

    valid_count = len(valid_results)
    if valid_count == 0:
        verdict = "INFRA ERROR - no valid localization runs completed"
    elif valid_count == 1 and passes == 1:
        verdict = "PASS - one successful localization run; more valid runs needed"
    elif valid_count >= 3 and passes == valid_count:
        verdict = "STRONG PASS - reliable on this synthetic localization task"
    elif passes >= max(2, (valid_count + 1) // 2):
        verdict = "PROMISING - useful but stochastic or still a small sample"
    elif passes:
        verdict = "WEAK - occasional localization success"
    else:
        verdict = "FAIL - production + test targets were not reliably recovered"

    print(f"\nRequired-target reliability: {passes}/{valid_count} valid runs")
    if errors:
        print(f"Infrastructure errors: {errors}/{args.runs} requested runs")
    print("Verdict:", verdict)
    print("Trajectories:", env["FASTCONTEXT_TRAJ_DIR"])

    if valid_count == 0:
        return 2
    return 0 if passes else 1


if __name__ == "__main__":
    raise SystemExit(main())
