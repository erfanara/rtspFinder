from rtspFinder.modules.cli.inputs import port
from rtspFinder.modules import utils, workers
from rtspFinder import DEFAULT_ROUTES
import asyncio
import sys

from rtspFinder.modules.logs_handler import logs

# Bring the package onto the path
sys.path.append('./rtsp_finder')


def rtspFind(ip,
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
    asyncio.run(
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
    return logs.dict_log()


if __name__ == "__main__":
    print(rtspFind("192.168.1.2", username="admin"))
