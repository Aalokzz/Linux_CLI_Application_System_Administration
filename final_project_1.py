#!/usr/bin/python3

import argparse

# Aalok

# Function to check CPU and Memory Usage
def system_usage(args):
    print("[INFO] CPU and Memory monitoring requested.")
    print(f"Arguments: {args}")

# Function to check Disk Space Usage
def disk_space_usage(args):
    print("[INFO] Disk space monitoring requested.")
    print(f"Directory: {args.dir}, Threshold: {args.threshold}%")

# Function to manage processes
def process_management(args):
    print("[INFO] Process management requested.")
    print(f"Filter by name: {args.name}")

def get_parser():
    main_parser = argparse.ArgumentParser(prog="final_project", usage="./sub_program.. [subcommand]")

    # Setup the subcommands
    sub_programs = main_parser.add_subparsers()

    # Adding the 'monitor' subcommand
    monitor_sp = sub_programs.add_parser("monitor", help="Monitor system health.")

    # Monitor options
    monitor_sp.add_argument("--system", action="store_true", help="Monitor CPU and memory usage.")
    monitor_sp.add_argument("--disk", action="store_true", help="Check disk usage.")
    monitor_sp.add_argument("--dir", type=str, help="Directory to check for disk usage.")
    monitor_sp.add_argument("--threshold", type=int, help="Disk usage threshold percentage.")
    monitor_sp.set_defaults(func=disk_space_usage)  # Default to disk space handling

    return main_parser

def main():
    try:
        parser = get_parser()
        args = parser.parse_args()

        if hasattr(args, "func"):
            args.func(args)
        else:
            print("[ERROR] No valid subcommand provided. Use --help for guidance.")

    except Exception as ex:
        print(f"There was an error: {ex}")

if __name__ == "__main__":
    main()
