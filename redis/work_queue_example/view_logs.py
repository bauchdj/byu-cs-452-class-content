#!/usr/bin/env python3

"""
Script to view recent logs from Redis
"""

import logger
import json


def main():
    print("Recent Application Logs:")
    print("=" * 50)

    logs = logger.get_recent_logs(20)  # Get the 20 most recent logs

    if not logs:
        print("No logs found.")
        return

    # Display logs in reverse order (oldest first)
    for log in reversed(logs):
        print(
            f"[{log['timestamp_formatted']}] {log['server_name']} ({log['script_name']}): {log['action']}"
        )


if __name__ == "__main__":
    main()
