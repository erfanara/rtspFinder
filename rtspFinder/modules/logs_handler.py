from abc import ABC
from sys import stderr
import inspect
import os


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
        if url != "":
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
        d["description"] = ""
        if logs._LOG.get("success") is None:
            d["success"] = False
            # Err 113 : no route to host
            if "[Errno 113]" in logs._LOG["onvifRtsp.py"]["errors"][0]:
                d["error"] = 113
                d["description"] = "no route to host"
            # Err 401 : auth failed
            elif "[Errno 401]" in logs._LOG["onvifRtsp.py"]["errors"][0]:
                d["error"] = 401
                d["description"] = "auth failed"
            # Err 111 : connection refused (maybe wrong port)
            elif "[Errno 111]" in logs._LOG["rtsp.py"]["errors"][0]:
                d["error"] = 111
                d["description"] = "connection refused, maybe rtsp port is wrong"
            else:
                # err -1, unknown error
                d["error"] = -1
                d["description"] = "unknown error, rtsp url not found"
        else:
            d["success"] = True
            if 'Nothing found using Onvif' in logs._LOG["onvifRtsp.py"]["errors"][0]:
                d["description"] = "onvif not worked"
            # Err 111 : connection refused (maybe wrong port)
            if "[Errno 111]" in logs._LOG["onvifRtsp.py"]["errors"][0]:
                d["error"] = 111
                d["description"] = "connection refused, maybe onvif port is wrong"
        d["rtsp"] = logs._LOG["urls"]

        return d
