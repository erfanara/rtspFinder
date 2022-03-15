import socket
from enum import Enum
from typing import List, Union
import re
from rtspFinder.modules.logs_handler import logs

from rtspFinder.modules.rtsp.packet import describe
MAX_RETRIES = 2

ROUTE_OK_CODES = ["RTSP/1.0 200", "RTSP/2.0 200", ]
CODES_404 = ["RTSP/1.0 404", "RTSP/2.0 404"]
AUTH_CODES = ["RTSP/1.0 401", "RTSP/2.0 401", "RTSP/1.0 403", "RTSP/2.0 403"]

reg = {
    "realm": re.compile(r'realm="(.*?)"'),
    "nonce": re.compile(r'nonce="(.*?)"'),
}


def find(var: str, response: str):
    """Searches for `var` in `response`."""
    match = reg[var].search(response)
    if match:
        return match.group(1)
    else:
        return ""


class AuthMethod(Enum):
    NONE = 0
    BASIC = 1
    DIGEST = 2


class Status(Enum):
    CONNECTED = 0
    TIMEOUT = 1
    UNIDENTIFIED = 100
    NONE = -1

    @classmethod
    def from_exception(cls, exception: Exception):
        if type(exception) is type(socket.timeout()) or type(exception) is type(
            TimeoutError()
        ):
            return cls.TIMEOUT
        else:
            return cls.UNIDENTIFIED


class RTSPClient:
    __slots__ = (
        "ip",
        "port",
        "credentials",
        "paths",
        "status",
        "auth_method",
        "last_error",
        "realm",
        "nonce",
        "socket",
        "timeout",
        "authorizeAttempts",
        "maxAuthorizeAttempts",
        "packet",
        "cseq",
        "data",
    )

    def __init__(
        self,
        ip: str,
        port: int = 554,
        credentials: str = ":",
        timeout: int = 3,
        maxAuthorizeAttempts: int = 1,
    ):
        self.ip = ip
        self.port = port
        self.credentials = credentials
        self.paths: List[str] = []
        self.status: Status = Status.NONE
        self.auth_method: AuthMethod = AuthMethod.NONE
        self.last_error: Union[Exception, None] = None
        self.realm: str = ""
        self.nonce: str = ""
        self.socket = None
        self.timeout = timeout
        self.authorizeAttempts: int = 0
        self.maxAuthorizeAttempts: int = maxAuthorizeAttempts
        self.packet = ""
        self.cseq = 0
        self.data = ""
        if not self._connect():
            raise ConnectionError("no connection to the host")

    @property
    def path(self):
        if len(self.paths) > 0:
            return self.paths[0]
        else:
            return ""

    @property
    def is_connected(self):
        return self.status is Status.CONNECTED

    @property
    def is_authorized(self):
        return "200" in self.data

    def _connect(self):
        self.packet = ""
        self.cseq = 0
        self.data = ""
        retry = 0
        while retry < MAX_RETRIES:
            try:
                self.socket = socket.create_connection(
                    (self.ip, self.port), self.timeout)
            except OSError as e:
                self.status = Status.from_exception(e)
                self.last_error = e
                logs.print_err(str(self.last_error))

                retry += 1
                # TODO: sleep needed?
                # sleep(1.5)
            else:
                self.status = Status.CONNECTED
                self.last_error = None
                return True
            
        return False

    def checkResponse(self, path: str, num: int = 1):
        if not self.data:
            raise ConnectionError("No Data Recieved!!")

        c = 0
        if any(code in self.data for code in CODES_404):
            c = 404
        elif any(code in self.data for code in ROUTE_OK_CODES):
            c = 200
        elif any(code in self.data for code in AUTH_CODES):
            c = 401
        else:
            c = -1

        if c in [404, -1]:
            return False
        elif c in [401] and num != 1:
            # TODO : (only for verbosity ,)(silent if credential worked for one of urls...)
            # logs.print_err(f"401: it seems the credentials is wrong for {path}, but also it can be false posetive")
            return False
        elif c in [200]:
            return True

    async def authorize(self, path: str):
        # create a new connection if maxAuthorizeAttempts exceeded
        if self.maxAuthorizeAttempts < self.authorizeAttempts:
            self._connect()
            self.authorizeAttempts = 0

        url = f"rtsp://{self.ip}:{self.port}{path}"

        async def send_and_recv(url: str, credentials: str):
            self.cseq += 1
            self.packet = describe(
                url, self.cseq, credentials, self.realm, self.nonce)
            try:
                self.socket.sendall(self.packet.encode())
                self.data = self.socket.recv(1024).decode()
            except OSError as e:
                self.status = Status.from_exception(e)
                self.last_error = e
                self.socket.close()
                return False

        await send_and_recv(url, ":")

        res = self.checkResponse(path)
        if res is not None:
            return res

        if "Basic" in self.data:
            self.auth_method = AuthMethod.BASIC
            await send_and_recv(url, self.credentials)
            self.authorizeAttempts += 1
        elif "Digest" in self.data:
            self.auth_method = AuthMethod.DIGEST
            self.realm = find("realm", self.data)
            self.nonce = find("nonce", self.data)
            await send_and_recv(url, self.credentials)
            self.authorizeAttempts += 1
        else:
            self.auth_method = AuthMethod.NONE

        res = self.checkResponse(path, 2)
        if res is not None:
            return res

    @staticmethod
    def get_rtsp_url(
        ip: str, port: Union[str, int] = 554, credentials: str = ":", route: str = "/"
    ):
        """Return URL in RTSP format."""
        if credentials != ":":
            ip_prefix = f"{credentials}@"
        else:
            ip_prefix = ""
        return f"rtsp://{ip_prefix}{ip}:{port}{route}"

    def __str__(self) -> str:
        x = self.get_rtsp_url(self.ip, self.port, self.credentials, self.path)
        return x

    def __rich__(self) -> str:
        return f"[underline cyan]{self.__str__()}[/underline cyan]"
