"""CLI interface for Vibe Agents."""

import argparse
import sys

from vibe_agents.__about__ import __version__


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="vibe-agents",
        description="AI 에이전트 바이브코딩 실험 프로젝트",
    )
    
    parser.add_argument(
        "--version",
        action="version", 
        version=f"vibe-agents {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령")
    
    # placeholder for future agent commands
    agent_parser = subparsers.add_parser("agent", help="에이전트 관리")
    agent_parser.add_argument("action", choices=["list", "create", "run"], help="에이전트 작업")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    if args.command == "agent":
        print(f"에이전트 {args.action} 명령이 구현되지 않았습니다.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())