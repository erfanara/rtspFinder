from rtspFinder.modules.cli.inputs import port
from rtspFinder.modules import utils, workers
from rtspFinder import DEFAULT_ROUTES
import asyncio
import sys

from rtspFinder.modules.logs_handler import logs

# Bring the package onto the path
sys.path.append('./rtsp_finder')


"""
example of returned json for a successful discovery:
    {
    'success': True,
    'description': 'onvif not worked',
    'rtsp': ['rtsp://admin:@192.168.1.2:554/user=admin_password=_channel=1_stream=0.sdp?real_stream']
    }

example of returned json for a failed discovery:
    {
    'success': False,
    'error': 113,
    'description': 'no route to host',
    'rtsp': []
    }

entities :
    'success'       -> bool
    'rtsp'          -> str
    'description'   -> str
    'error'         -> int  (just if success was False)

error codes:
    113 -> no route to host
    111 -> connection refused (maybe port is wrong)
    401 -> auth failed
    -1  -> unknown error, rtsp url not found
    -2  -> timeout
"""


async def rtspFind(ip,
                   rtsp_port=554,
                   onvif_port=80,
                   username="",
                   password="",
                   dummy_timeout=7.0,
                   stop_after_first_success=True,
                   only_onvif=False,
                   no_onvif=False,
                   ):
    logs.set_quiet(True)
    task = asyncio.create_task(
        workers.main(
            ip,
            port(rtsp_port),
            port(onvif_port),
            username,
            password,
            utils.load_paths(DEFAULT_ROUTES),
            ss_timeout=dummy_timeout,
            stop_all_workers_after_first_success=stop_after_first_success,
            only_onvif=only_onvif,
            no_onvif=no_onvif,
            dont_store=True
        )
    )
    try:
        # TODO : idk why timeout does not work!
        await asyncio.wait_for(task, timeout=20.0)
    except asyncio.TimeoutError:
        return {"success": False, "Error": -2, "description": "timeout", "rtsp": []}
    return logs.dict_log()


if __name__ == "__main__":
    print(asyncio.run(rtspFind("192.168.1.2", username="admin")))
