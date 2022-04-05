from sys import stderr
from requests import request
import requests
from requests.auth import HTTPDigestAuth

import re

from requests.exceptions import RequestException
from requests.models import HTTPError

from rtspFinder.modules.logs_handler import logs

GET_PROFILE = """<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
  <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <GetProfiles xmlns="http://www.onvif.org/ver10/media/wsdl" />
  </s:Body>
</s:Envelope>"""

GED_DEVICE_INFO = "<s:Envelope xmlns:s=\"http://www.w3.org/2003/05/soap-envelope\"><s:Body xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\"><GetDeviceInformation xmlns=\"http://www.onvif.org/ver10/device/wsdl\"/></s:Body></s:Envelope>"

GET_STREAM_URI_RAW = """
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
  <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <GetStreamUri xmlns="http://www.onvif.org/ver10/media/wsdl">
      <StreamSetup>
        <Stream xmlns="http://www.onvif.org/ver10/schema">RTP-Unicast</Stream>
        <Transport xmlns="http://www.onvif.org/ver10/schema">
          <Protocol>RTSP</Protocol>
        </Transport>
      </StreamSetup>
      <ProfileToken>xx_prof_xx</ProfileToken>
    </GetStreamUri>
  </s:Body>
</s:Envelope>
"""

header1 = {
    'content-type': "application/xml",
    'cache-control': "no-cache",
}


def findProfileTokens(xmlData: str):
    return re.findall(r'Profiles .*? token="(.*?)"', xmlData)


def findUris(xmlData: str):
    # TODO : regex is true? (Uri ?)
    return re.findall(r'Uri>(rtsp://.*?)<', xmlData)


def getRtsp(ip: str, onvif_port: int, user: str, password: str):
    urls = []
    try:
        # Get Profiles first
        res = request('POST', f"http://{ip}:{onvif_port}/onvif/media_service", headers=header1,
                      data=GET_PROFILE.encode(), auth=HTTPDigestAuth(user, password))

        # (for debugging) print(res.content.decode())

        # Check if auth was not successful
        if res.status_code == 401 or res.status_code == 403:
            raise HTTPError("[Errno 401] auth failed")

        profList = findProfileTokens(res.content.decode())

        # Get stream link for every profile
        for prof in profList:
            GET_STREAM_URI = GET_STREAM_URI_RAW.replace('xx_prof_xx', prof)
            res = request('POST', f"http://{ip}/onvif/media_service", headers=header1,
                          data=GET_STREAM_URI.encode(), auth=HTTPDigestAuth(user, password))
            # TODO : remove this print
            # print(res.content.decode())
            urls.extend(findUris(res.content.decode()))
        if len(urls) == 0:
            logs.print_err("Nothing found using Onvif")
            logs.return_status(False)
        else:
            logs.print_url(urls[0])
            logs.return_status(True)

    except requests.exceptions.RequestException as e:
        logs.print_err(str(e))
        logs.return_status(False)

    for url in urls:
        logs.print_err(f"\"{url}\" >>>> Found !!")

    return urls


if __name__ == "__main__":
    print(getRtsp("192.168.1.99", 80, "ImageProcessing1", "Veerasense123."))
