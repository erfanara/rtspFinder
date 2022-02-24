from rtspFinder.__main__ import PICS_FOLDER
from rtspFinder.modules.utils import escape_chars
from pathlib import Path
from sys import stderr
import cv2
cv2.setLogLevel(0)


def screenShot(url: str,no_report:bool):
    try:
        cap = cv2.VideoCapture()

        # cap.open(url) should raise Exception if needed
        cap.setExceptionMode(True)
        cap.open(url)

        # Now try to capture image from that rtsp url
        ret, frame = cap.read()
        if not no_report:
            file_name = escape_chars(f"{url.lstrip('rtsp://')}.jpg")
            file_path = PICS_FOLDER / file_name
            cv2.imwrite(file_path.__str__(), frame)
            return file_path

        cap.release()
        return True

    except cv2.error as e:
        print(e.err, file=stderr)
        return None
