from __future__ import annotations

import argparse
import asyncio
import os

from fastcontext.agent.agent_factory import make_fastcontext_agent


def main() -> None:
    parser = argparse.ArgumentParser(description="repo-locate FastContext launcher")
    parser.add_argument("--query", "-q", required=True)
    parser.add_argument("--traj", "-t", default=None)
    parser.add_argument("--max-turns", type=int, default=8)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--citation", action="store_true")
    args = parser.parse_args()

    agent = make_fastcontext_agent(
        trajectory_file=args.traj,
        work_dir=os.getcwd(),
    )

    # Upstream FastContext defaults to temperature=1.0 and its CLI currently
    # exposes no temperature flag. The SFT checkpoint is substantially more
    # stable at 0.6 in local serving, so repo-locate makes that integration
    # setting explicit while allowing experiments to override it.
    agent.llm.temperature = float(os.getenv("FASTCONTEXT_TEMPERATURE", "0.6"))

    output = asyncio.run(
        agent.run(
            prompt=args.query,
            max_turns=args.max_turns,
            verbose=args.verbose,
            citation=args.citation,
        )
    )
    print(output)


if __name__ == "__main__":
    main()
