"""Console script for snapchat_dl."""
import argparse
import concurrent.futures
import os
import re
import sys
from time import sleep
from time import time

import pyperclip
from colorama import init
from termcolor import colored

from snapchat_dl import SnapchatDL


def main():  # pragma: no cover
    """Console script for snapchat_dl."""
    init(autoreset=True)
    parser = argparse.ArgumentParser(prog="snapchat-dl")

    parser.add_argument(
        "usernames",
        action="store",
        nargs="*",
        help="Atleast one or more usernames to download stories for.",
    )

    parser.add_argument(
        "-c",
        "--scan-clipboard",
        action="store_true",
        help="Scan clipboard for story links"
        " with the format of 'https://story.snapchat.com/s/<username>'",
        dest="scan_clipboard",
    )

    parser.add_argument(
        "-i",
        "--batch-file",
        action="store",
        default=None,
        help="Read usernames from file",
        metavar="BATCH_FILENAME",
        dest="batch_file",
    )

    parser.add_argument(
        "-P",
        "--directory-prefix",
        action="store",
        default=os.getcwd(),
        help="Directory Prefix for downloading stories",
        metavar="DIRECTORY_PREFIX",
        dest="save_prefix",
    )

    parser.add_argument(
        "-l",
        "--limit-story-count",
        action="store",
        default=-1,
        help="Set maximum number of stories to download.",
        metavar="NUM_STORY",
        dest="limit_story",
        type=int,
    )

    parser.add_argument(
        "-j",
        "--max-concurrent-downloads",
        action="store",
        default=1,
        help="Set maximum number of parallel downloads.",
        metavar="MAX_WORKERS",
        dest="max_workers",
        type=int,
    )

    parser.add_argument(
        "-s",
        "--scan-from-prefix",
        action="store_true",
        help="Scan usernames (as directory name) from prefix directory.",
        dest="scan_prefix",
    )

    parser.add_argument(
        "-u",
        "--check-for-update",
        action="store_true",
        help="Periodically check for new stories.",
        dest="check_update",
    )

    parser.add_argument(
        "-t",
        "--update-interval",
        action="store",
        default=60 * 10,
        help="Set the update interval for new story in seconds. (Default: 10m)",
        metavar="INTERVAL",
        dest="interval",
        type=int,
    )

    args = parser.parse_args()

    """Append usernames from BATCH_FILE to args.usernames list"""
    if args.scan_prefix is False and args.batch_file is not None:
        if os.path.isfile(args.batch_file) is False:
            raise os.error(
                colored("Invalid Batch File at {}".format(args.batch_file), "red")
            )
        with open(args.batch_file, "r") as f:
            for username in f.read().split("\n"):
                if len(username.strip()) > 0:
                    args.usernames.append(username.strip())

    args.save_prefix = os.path.normpath(args.save_prefix)

    if args.scan_prefix:
        count = 0
        for username in [
            o
            for o in os.listdir(args.save_prefix)
            if os.path.isdir(os.path.join(args.save_prefix, o)) and o not in [".", ".."]
        ]:
            if username not in args.usernames:
                args.usernames.append(username)
                count += 1
        print("Added {} usernames from {}".format(count, args.save_prefix))

    downlaoder = SnapchatDL(
        directory_prefix=args.save_prefix,
        max_workers=args.max_workers,
        limit_story=args.limit_story,
    )

    history = list()
    seconds_tick_start = int(time())
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.max_workers
    ) as executor:

        def download_users(users, respect_history=False):
            for user in users:
                if respect_history and username not in history:
                    history.append(username)
                    executor.submit(downlaoder.download, user)
                else:
                    executor.submit(downlaoder.download, user)

        download_users(args.usernames, respect_history=False)

        if args.check_update and args.scan_clipboard is False:
            while True:
                sleep(args.interval)
                download_users(args.usernames, respect_history=False)

        if args.scan_clipboard:
            while True:
                for username in re.findall(
                    r"https://story.snapchat.com/s/([\w_\.]+)", pyperclip.paste()
                ):
                    if username not in history:
                        executor.submit(downlaoder.download, username)
                        history.append(username)
                if int(time()) - seconds_tick_start >= args.interval:
                    seconds_tick_start = int(time())
                    print("Checking for new stories")
                    download_users(history, respect_history=True)
                sleep(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
