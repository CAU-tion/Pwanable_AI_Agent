#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from providers import create_provider
from reliability import run_agent_reliable


DEFAULT_MODEL = "gemini-3.6-flash"


PWNABLE_SYSTEM_PROMPT = """
You are an AI agent for solving authorized pwnable and CTF challenges.

Your goal is to analyze the challenge systematically and use available
tools when evidence is needed.

Rules:
- Work only on authorized CTF or pwnable challenge environments.
- Use tools to inspect evidence when necessary.
- Do not invent command outputs, file contents, addresses, offsets,
  protections, vulnerabilities, or tool results.
- Base conclusions on evidence obtained from the challenge and tools.
- After each tool result, reassess the current hypothesis before
  choosing the next action.
- Keep track of useful findings such as protections, vulnerabilities,
  addresses, offsets, and failed attempts.
- When enough evidence is available, explain the final result clearly.

Typical workflow:
1. Identify the provided challenge files.
2. Inspect file type, architecture, and security protections.
3. Analyze program behavior and relevant code paths.
4. Identify candidate vulnerabilities.
5. Verify assumptions using available tools.
6. Build and test an exploit incrementally when appropriate.
7. Record failed attempts and avoid repeating them.

When challenge files are provided, inspect the actual files using tools.
Never assume their contents from their filenames alone.
""".strip()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pwnable-agent",
        description="Gemini-based AI agent for authorized pwnable/CTF challenges.",
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini model to use (default: {DEFAULT_MODEL})",
    )

    parser.add_argument(
        "--file",
        "-f",
        action="append",
        default=[],
        help="Challenge file path. Can be specified multiple times.",
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode.",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Hide tool execution trace.",
    )

    parser.add_argument(
        "task",
        nargs="*",
        help="Pwnable/CTF challenge description or task.",
    )

    return parser


def resolve_files(paths: list[str]) -> list[Path]:
    """
    Validate the given file or directory paths.
    If a directory is provided, recursively collect all files inside it.
    """
    resolved_files: list[Path] = []

    for input_path in paths:
        path = Path(input_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"Path does not exist: {input_path}"
            )

        # Single file
        if path.is_file():
            resolved_files.append(path)
            continue

        # Directory
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file():
                    resolved_files.append(child.resolve())

            continue

        raise ValueError(
            f"Unsupported path: {input_path}"
        )

    # Remove duplicate paths while preserving order
    resolved_files = list(dict.fromkeys(resolved_files))

    return resolved_files

def build_task(task: str, files: list[Path]) -> str:
    """
    사용자 요청과 challenge 파일 정보를 하나의 Agent task로 합친다.
    """
    parts = []

    if task:
        parts.append(task)

    if files:
        parts.append("\nProvided challenge files:")

        for path in files:
            parts.append(f"- {path}")

        parts.append(
            "\nInspect these files using the available tools before "
            "drawing conclusions."
        )

    return "\n".join(parts)


def run_task(
    task: str,
    model: str,
    files: list[Path] | None = None,
    verbose: bool = True,
) -> str:

    if files is None:
        files = []

    full_task = build_task(
        task=task,
        files=files,
    )

    provider = create_provider(
        "gemini",
        model,
    )

    return run_agent_reliable(
        task=full_task,
        provider=provider,
        system_prompt=PWNABLE_SYSTEM_PROMPT,
        verbose=verbose,
    )


def run_interactive(
    model: str,
    files: list[Path] | None = None,
    verbose: bool = True,
) -> None:

    if files is None:
        files = []

    print("Pwnable Agent interactive mode")

    if files:
        print("\nChallenge files:")

        for path in files:
            print(f"  - {path}")

    print("\nType 'exit' to quit.\n")

    while True:
        try:
            task = input("Challenge> ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if task.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break

        if not task:
            continue

        try:
            answer = run_task(
                task=task,
                model=model,
                files=files,
                verbose=verbose,
            )

            print(f"\nAgent: {answer}\n")

        except Exception as e:
            print(f"\nError: {e}\n")


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    verbose = not args.quiet

    try:
        challenge_files = resolve_files(args.file)

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("=" * 46)
    print("          Pwnable AI Agent")
    print("=" * 46)
    print("Provider : Gemini")
    print(f"Model    : {args.model}")

    if challenge_files:
        print("Files    :")

        for path in challenge_files:
            print(f"           {path}")

    print()

    if args.interactive:
        run_interactive(
            model=args.model,
            files=challenge_files,
            verbose=verbose,
        )
        return

    task = " ".join(args.task).strip()

    if not task and not challenge_files:
        parser.print_help()
        sys.exit(0)

    # 파일만 넣고 task를 생략해도 동작
    if not task:
        task = (
            "Analyze the provided pwnable challenge files and "
            "identify the vulnerability."
        )

    print(f"Task: {task}\n")

    try:
        answer = run_task(
            task=task,
            model=args.model,
            files=challenge_files,
            verbose=verbose,
        )

        print(f"\nAnswer: {answer}\n")

    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)

    except Exception as e:
        print(f"\nError: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()