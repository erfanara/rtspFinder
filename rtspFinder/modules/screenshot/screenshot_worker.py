import asyncio
from rtspFinder.modules.logs_handler import logs
from rtspFinder.modules.screenshot.ss_cv2 import screenShot

from rtspFinder.modules.utils import append_result


async def screenshot_worker(
    queue2: asyncio.Queue,
    loop, pool,
    ss_timeout: float,
    stop_all_workers_after_first_success: bool = True,
    dont_store_picture: bool = True
):
    lock = asyncio.Lock()
    while True:
        url: str = await queue2.get()

        try:
            image_path = await asyncio.wait_for(loop.run_in_executor(
                pool, screenShot, url, dont_store_picture), ss_timeout)
            if image_path is not None:
                logs.print_url(url)
                if not dont_store_picture:
                    async with lock:
                        append_result(image_path, url)
                if stop_all_workers_after_first_success:
                    queue2.task_done()
                    while not queue2.empty():
                        await queue2.get()
                        queue2.task_done()
                    return
            else:
                logs.print_err(f"{url} >>>> ScreenShot Failed.")

        except asyncio.TimeoutError as e:
            # TODO: try again if ...?
            logs.print_err(
                f"{url}  >>>> ({ss_timeout}s) TimeOut Exceeded.")

        queue2.task_done()
