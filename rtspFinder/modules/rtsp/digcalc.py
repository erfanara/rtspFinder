from hashlib import md5
import functools
# http auth digest calculator based on digcalc.c from rfc2617

# calculate H(A1) as per spec
# @functools.lru_cache()
def digestCalcHA1(alg: str,
                  username: str,
                  realm: str,
                  password: str,
                  nonce: str,
                  cNonce: str):
    concat = username + ":" + realm + ":" + password
    if alg.lower == "md5-sess":
        concat += ":" + nonce + ":" + cNonce

    return md5(concat.encode("ascii")).hexdigest()


# calculate H(A2) as per spec
@functools.lru_cache(15)
def digestCalcHA2(qop: str,
                  method: str,
                  digestUri: str,
                  hEntity: str):
    concat = method + ":" + digestUri
    if qop.lower() == "auth-int":
        concat += ":" + hEntity
    return md5(concat.encode("ascii")).hexdigest()


# calculate request-digest/response-digest as per HTTP Digest spec
def digestCalcResponse(alg: str,
                       username: str,
                       realm: str,
                       password: str,
                       nonce: str,                       # nonce from server
                       nonceCount: str,                  # 8 hex digits
                       cNonce: str,                      # client nonce
                       qop: str,                         # qop-value: "", "auth", "auth-int"
                       method: str,                      # method from the request
                       digestUri: str,                   # requested URL
                       hEntity: str):             # H(entity body) if qop="auth-int"
    concat = str(digestCalcHA1(alg, username, realm,
                 password, nonce, cNonce)) + ":" + nonce + ":"
    if qop is not None and qop != "":
        concat += nonceCount+":"+cNonce+":"+qop+":"
    concat += str(digestCalcHA2(qop, method, digestUri, hEntity))

    # return request-digest or response-digest
    return md5(concat.encode("ascii")).hexdigest()


# test
if __name__ == "__main__":
    Nonce = ""
    CNonce = ""
    User = ""
    Realm = ""
    Pass = ""
    Alg = "md5"
    nonceCount = ""
    Method = ""
    Qop = ""
    URI = ""
    
    print(digestCalcResponse(Alg, User, Realm, Pass, Nonce, nonceCount,
                             CNonce, Qop, Method, URI, ""))
