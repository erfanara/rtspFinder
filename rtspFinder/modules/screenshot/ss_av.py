# TODO : this file is under development

import av

import logging
logger = logging.getLogger()
logger_is_enabled = logger.isEnabledFor(logging.DEBUG)

from rtspFinder.modules.utils import escape_chars
from rtspFinder.__main__ import PICS_FOLDER

MAX_SCREENSHOT_TRIES = 2

def _is_video_stream(stream):
    return (
        stream.profile is not None
        and stream.start_time is not None
        and stream.codec_context.format is not None
    )

def rtspGrab(url: str,timeOut:float,tries:int)->bool: 
    try:
        with av.open(url,timeout=timeOut) as cap:
            stream = cap.streams.video[0]
            
            if _is_video_stream(stream):
                file_name = escape_chars(f"{url.lstrip('rtsp://')}.jpg")
                file_path = PICS_FOLDER / file_name
                stream.thread_type = "AUTO"
                for frame in cap.decode(video=0):
                    frame.to_image().save(file_path)
                    break
            else:
                # There's a high possibility that this video stream is broken
                # or something else, so we try again just to make sure.
                if tries < MAX_SCREENSHOT_TRIES:
                    cap.close()
                    tries += 1
                    return rtspGrab(url, timeOut,tries)
                else:
                    if logger_is_enabled:
                        logger.debug(
                            f"Broken video stream or unknown issues with {url}"
                        )
                    return False
    except (MemoryError, PermissionError, av.InvalidDataError) as e:
        # These errors occur when there's too much SCREENSHOT_THREADS.
        if logger_is_enabled:
            logger.debug(f"Missed screenshot of {url}: {repr(e)}")
        # Try one more time in hope for luck.
        if tries < MAX_SCREENSHOT_TRIES:
            tries += 1
            console.print(
                f"[yellow]Retry to get a screenshot of the [underline]{url}"
            )
            return rtspGrab(url, timeOut,tries)
        else:
            console.print(
                f"[italic red]Missed screenshot of [underline]{rtsp_url}[/underline] - if you see this message a lot, consider reducing the number of screenshot threads",
            )
            return
    except Exception as e:
        if logger_is_enabled:
            logger.debug(f"get_screenshot failed with {rtsp_url}: {repr(e)}")
        return
    
    
    return True