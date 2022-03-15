
import asyncio
from asyncio.exceptions import InvalidStateError
import concurrent.futures
from urllib.parse import urlparse
from webbrowser import get
from rtspFinder.modules.logs_handler import logs
import rtspFinder.modules.onvif.onvifRtsp as onvifRtsp
from rtspFinder.modules.rtsp.rtsp_worker import rtsp_worker, get_paths_worked
from rtspFinder.modules.screenshot.screenshot_worker import screenshot_worker


async def main(
    ip: str,
    rtsp_port: int = 554,
    onvif_port: int = 80,
    user: str = "",
    password: str = "",
    paths: list[str] = [],
    ss_timeout: float = 7.0,
    rtsp_worker_maxWorkers: int = 30,
    ss_maxWorkers=10,
    stop_all_workers_after_first_success: bool = True,
    no_onvif: bool = False,
    only_onvif: bool = False,
    dont_store: bool = False,
):
    queue1 = asyncio.Queue()
    queue2 = asyncio.Queue()
    rtsp_tasks = []
    found_urls_onvif = []

    if not no_onvif:
        logs.print_err("Checking for onvif")
        # check for Onvif
        found_urls_onvif = onvifRtsp.getRtsp(
            ip, onvif_port, user, password)

    if not only_onvif and len(found_urls_onvif) == 0:
        # Onvif not worked
        # check for errors then terminate if needed
        # TODO:remove these ugly codes , we need more dynamic code for error handlings
        if not no_onvif and "[Errno 113]" in logs._LOG["onvifRtsp.py"]["errors"][0]:
            logs.print_err("[Errno 113] No route to Host")
            logs.print_err("Stopping Everything.")
            return
        if not no_onvif and "[Errno 401]" in logs._LOG["onvifRtsp.py"]["errors"][0]:
            logs.print_err("[Errno 401] auth failed")
            logs.print_err("Stopping Everything.")
            return

        # then add the urls to the queue1
        for path in paths:
            await queue1.put(path)

        # Create worker tasks to process the queue concurrently.
        logs.print_err("Starting rtsp_workers!!")
        for _ in range(rtsp_worker_maxWorkers):
            task = asyncio.create_task(rtsp_worker(queue1, queue2, str(
                ip), rtsp_port, f"{str() if user is None else user}:{str() if password is None else password}"))
            task.exception
            rtsp_tasks.append(task)
    else:
        # onvif worked
        only_onvif = True
        for url in found_urls_onvif:
            await queue2.put(f"rtsp://{user}:{password}@{ip}:{rtsp_port}{urlparse(url).path}")

    # initial things for ss_workers
    logs.print_err("Starting screenshot_worker!!")
    ss_loop = asyncio.get_running_loop()
    ss_pool = concurrent.futures.ThreadPoolExecutor(ss_maxWorkers)
    ss_task = asyncio.create_task(screenshot_worker(
        queue2, ss_loop, ss_pool, ss_timeout, stop_all_workers_after_first_success, dont_store))

    connection_error = True
    # Wait until all worker tasks are cancelled. (here blockage occurs)
    results = await asyncio.gather(*rtsp_tasks, return_exceptions=True)
    for r in results:
        if r:
            connection_error = False

    # Wait until the queue1 is fully processed.
    # await queue1.join()

    if not connection_error:
        if not only_onvif and get_paths_worked() == 0:
            logs.print_err(
                "Nothing Found, you should try a better route list, or maybe your credentials is wrong.")
            logs.return_status(False)
        if get_paths_worked() > len(paths)/2:
            logs.print_err(
                "seems that this RTSP server is so stubborn and these routes probably are false positives, ... it may take a few minutes to verify!")
            # TODO: Now change the ss_timeout and ss_workers for faster verification

        # Wait until the queue2 is fully processed.
        await queue2.join()

    # cancel rtsp and ScreenShot tasks now
    logs.print_err("Stopping Everything.")
    for task in rtsp_tasks:
        task.cancel()
    ss_task.cancel()

    ss_pool.shutdown(True)
