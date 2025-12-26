import argparse
import sys
import os

# Force UTF-8 encoding for stdout to handle emojis
sys.stdout.reconfigure(encoding='utf-8')

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.workflows.new_idea_chain import run_new_idea_chain
from src.workflows.earnings_season_chain import run_earnings_season_chain

def main():
    parser = argparse.ArgumentParser(description="Institutional GVD Investment Engine")
    subparsers = parser.add_subparsers(dest="command", help="Available workflows")

    # Workflow A
    parser_idea = subparsers.add_parser("new_idea", help="Run Workflow A: The 'New Idea' Chain")
    parser_idea.add_argument("--input", type=str, default="Start the Compounder Hunt", help="Input for @Originator")

    # Workflow B
    parser_earnings = subparsers.add_parser("earnings", help="Run Workflow B: The 'Earnings Season' Chain")
    parser_earnings.add_argument("--file", type=str, required=True, help="Path to 10-K PDF")

    args = parser.parse_args()

    if args.command == "new_idea":
        run_new_idea_chain(args.input)
    elif args.command == "earnings":
        run_earnings_season_chain(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
