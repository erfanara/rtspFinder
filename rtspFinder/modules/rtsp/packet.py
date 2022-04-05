import base64
import functools

from rtspFinder.modules.rtsp.digcalc import digestCalcResponse


@functools.lru_cache(maxsize=15)
def _basic_auth(credentials):
    encoded_cred = base64.b64encode(credentials.encode("ascii"))
    return f"Authorization: Basic {str(encoded_cred, 'utf-8')}"


def _digest_auth(method, url, credentials, realm, nonce):
    username, password = credentials.split(":")
    response = digestCalcResponse(
        "md5", username, realm, password, nonce, "", "", "", method, url, "")

    return(
        "Authorization: Digest "
        f'username="{username}", '
        f'realm="{realm}", '
        f'nonce="{nonce}", '
        f'uri="{url}", '
        f'response="{response}"'
    )


def describe(url, cseq, credentials, realm=None, nonce=None):
    if credentials == ":":
        auth_str = ""
    elif realm:
        auth_str = f"{_digest_auth('DESCRIBE', url, credentials, realm, nonce)}\r\n"
    else:
        auth_str = f"{_basic_auth(credentials)}\r\n"

    return (
        f"DESCRIBE {url} RTSP/1.0\r\n"
        "Accept: application/sdp\r\n"
        f"CSeq: {cseq}\r\n"
        "User-Agent: Lavf58.74.100\r\n"
        f"{auth_str}"
        "\r\n"
    )


def options(url, cseq,credentials,realm,nonce):
    if credentials == ":":
        auth_str = ""
    elif realm:
        auth_str = f"{_digest_auth('DESCRIBE', url, credentials, realm, nonce)}\r\n"
    else:
        auth_str = f"{_basic_auth(credentials)}\r\n"

    return (
        f"OPTIONS {url} RTSP/1.0\r\n"
        f"CSeq: {cseq}\r\n"
        "User-Agent: Lavf58.74.100\r\n"
        f"{auth_str}"
        "\r\n"
    )
