from abc import ABC
from sys import stderr
import inspect
import os
import json


class logs(ABC):
    _quiet_switch = True
    _LOG = {}
    _LOG["urls"] = []

    @staticmethod
    def set_quiet(switch: bool):
        logs.quiet_switch = switch

    @staticmethod
    def print_err(msg: str):
        caller_filename_only = os.path.basename(inspect.stack()[1].filename)

        # add error message to json
        if logs._LOG.get(caller_filename_only) is None:
            logs._LOG[caller_filename_only] = {}
            logs._LOG[caller_filename_only]["errors"] = []
        logs._LOG[caller_filename_only]["errors"].append(msg)

        # print error message
        if not logs.quiet_switch:
            print(caller_filename_only + ": " + msg, file=stderr)

    @staticmethod
    def print_url(url: str):
        logs._LOG["success"] = True
        logs._LOG["urls"].append(url)

        if not logs.quiet_switch:
            caller_filename_only = os.path.basename(
                inspect.stack()[1].filename)
            print(caller_filename_only + ": " + url + " Captured!!!")

    @staticmethod
    def return_status(success: bool):
        caller_filename_only = os.path.basename(inspect.stack()[1].filename)

        if logs._LOG.get(caller_filename_only) is None:
            logs._LOG[caller_filename_only] = {}
            logs._LOG[caller_filename_only]["errors"] = []
        logs._LOG[caller_filename_only]["success"] = success

        # print success status
        if not logs.quiet_switch:
            print(caller_filename_only + ": success=" +
                  str(success), file=stderr)

    @staticmethod
    def dict_log():
        d = {}
        if logs._LOG.get("success") is None:
            d["success"] = False
        else:
            d["success"] = True
        d["rtsp"] = logs._LOG["urls"]

        return d
