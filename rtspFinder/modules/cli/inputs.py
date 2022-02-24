import argparse
from pathlib import Path
from typing import Any

from rtspFinder import DEFAULT_ROUTES


class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=99)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ", ".join(action.option_strings) + " " + args_string


def file_path(value: Any):
    if Path(value).exists():
        return Path(value)
    else:
        raise argparse.ArgumentTypeError(f"{value} is not a valid path")


def port(value: Any):
    if int(value) in range(65536):
        return int(value)
    else:
        raise argparse.ArgumentTypeError(f"{value} is not a valid port")


parser = argparse.ArgumentParser(
    prog="rtspFinder",
    description="Tool for RTSP that brute-forces routes assuming that you only have one target and you have credentials",
    formatter_class=lambda prog: CustomHelpFormatter(prog),
)
parser.add_argument(
    "-i",
    "--ip",
    type=str,
    required=True,
    help="target ip, example: \"192.168.1.2\"",
)
parser.add_argument(
    "-rp",
    "--rtsp-port",
    type=int,
    default=554,
    help="target rtsp port, default: 554"
)
parser.add_argument(
    "-op",
    "--onvif-port",
    type=int,
    default=80,
    help="target onvif port, default: 80"
)
parser.add_argument(
    "-u",
    "--username",
    type=str,
    default="",
    help="username, example: \"admin\"",
)
parser.add_argument(
    "-p",
    "--password",
    type=str,
    default="",
    help="password, example: \"123456\"",
)
parser.add_argument(
    "-r",
    "--routes",
    type=file_path,
    default=DEFAULT_ROUTES,
    help="the path on which to load a custom routes",
)
parser.add_argument(
    "-T", "--timeout", default=7.0, type=float, help="the timeout to capture a url"
)
parser.add_argument(
    "--only-onvif", default=False, action="store_true", help="only use onvif and don't use rtsp_quick_scan"
)
parser.add_argument(
    "--no-onvif", default=False, action="store_true", help="don't use onvif for first try and only use rtsp_quick_scan"
)
parser.add_argument(
    "--dont-stop", default=False, action="store_true", help="don't stop after first success"
)

parser.add_argument("-q", "--quiet", action="store_true",
                    help="only print the paths found")
parser.add_argument("--no-report", action="store_true",
                    help="don't store reports and screenshots")
