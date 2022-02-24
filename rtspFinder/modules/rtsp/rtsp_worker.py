import asyncio
from rtspFinder.modules.logs_handler import logs
from rtspFinder.modules.rtsp.rtsp import RTSPClient


paths_worked = 0


async def rtsp_worker(
    queue1: asyncio.Queue,
    queue2: asyncio.Queue,
    ip: str,
    port,
    credentials: str = ":",
    timeout: int = 3,
    maxAuthorizeAttempts: int = 1,
):
    global paths_worked

    if port is None:
        port = 554

    try:
        rc = RTSPClient(ip, port, credentials, timeout, maxAuthorizeAttempts)
    except ConnectionError:
        return False
    while True:
        if queue1.empty():
            return True
        path: str = await queue1.get()

        if await rc.authorize(path):
            logs.print_err(f"\"{path}\" >>>> WORKED !!")
            await queue2.put(f"rtsp://{credentials}@{ip}:{port}{path}")
            paths_worked += 1

        queue1.task_done()

def get_paths_worked():
    global paths_worked
    return paths_worked