import logging
from pathlib import Path
from typing import List
import re

RESULT_FILE: Path
HTML_FILE: Path

logger = logging.getLogger()

def generate_html(path: Path):
    html = (
        f"<!DOCTYPE html>\n<html>\n<head>\n<title>{path.parent.name}</title>\n"
        """<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>   
html{background-color: #141414}
p{text-align: center;color: white;font-family: monospace;}
img{cursor: pointer;border: 2px solid #707070;}
img:hover {border: 2px solid white;}
div.gallery img {width: 100%;height: auto;}
*{box-sizing: border-box;}
.responsive {padding: 6px 6px;float: left;width: 25%;}
@media only screen and (max-width: 700px){.responsive {width: 50%;margin: 1px 0;}}
@media only screen and (max-width: 500px){.responsive {width: 100%;}}
</style>
<link rel="shortcut icon" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAABmJLR0QAAAAAAAD5Q7t/AAAAB3RJTUUH5AcTDRQPB0SOwgAACdxJREFUWMOtVl1wE+cVPd/uSl6ttJa0kmxjmUYgEQv/EAKh2LLBJQKHnxBMDDjGg0PsNJN4OmAzbcqQB8pD+pC20Ok0Q5oOnjKZQH4K5SfQyTiFUgbKJDjGGPwTDDg2tsEY2ZIlWbK0un1gcOLYhLaTM7Mv+9177tnz3e/ux/AIKKIREi/yATXkiqmxpTFV/QkBT/AC/yOAkhhjIKIQI3ZL0umumI3Gf0yfNu2zlYu917t6uhN7P3zve/nZwxaMggEaJnAhGp2jUuLFBKNnBUF4TKfTaSRJAs/zWLRoEQDgwoULICJEIhGEQqExNR6/YTTIR2c5Xe/X/Wzr1aZLTYlfvfXr/07Asox8NNz6NwwayRZRx14lJF4RdbqMlJQUmM1mxONxBINByLKMffv2YWxsDJWVlQgEAkhOToYsy0gkEujv70dsbKx7uj3j3QVPzv9TW0f74L/On4OgER5uR0ZyKgBA0ohzeI77O8/zcafTSUuWLKG5c+eSzWYjjUZDjDF6/fXXKR6PUywWo9raWgJAjDESBIHS0tLI4/HQvHnzyGw2x11O5/F1a57PNsgG7HnzramL2/VpAACRT8rjGGvS6/Xk9XrJ6/WS2WwmAOPP3Llz6ebNm/QAX331FWVnZ0+IEQSBsrOzqbi4mNLS0sg5c+bFF9ZtWMi0Aup3/3Fi8ZWPLwE4Bn2S9CTHuGZFUai8vJwWLFhAPM9PIBZFkerr6+m72Lt3L2m12gmxAMjhcNCaNWsoIyODsrOyGqsrN+esWrkSX5+9+o0AvVaCWWdM5Tm+wWQyUXV1Nc2bN28SGQAqKSmhu3fvUl9fH42Ojo4L8Pl8tGLFiilzZsyYQaXr1lF6ejrlL8w7tr3u55ZXq14GAPAzzXaUZBaxi/2tvwDHNpeWlrLu7m6cP39+0jalpqZiz549SE1NRUNDA8LhMAKBAO7cuQObzQa73Y6TJ09idHR0Qt7w8DB0oojMzEx0dHQ4tUlJw+99cOB8dNAPPhofw7XhW08Go6G38vLzjXa7HUeOHEEikZgkoKamBlVVVRgcHMSBAwfAGMOJEydw4cIF2O12FBYWore3F59//vmk3Lt378LtdiOuqtywf9h5pan5lC/oH0Dfu2eYpBV/m5ycTDt27KCZM2dOaeOcOXPo+vXrRESkqiq1tLTQqVOn6OjRo3TixAkaHBwkIqL29nZyu91TcjgcDqqsrLy/JSVr3yQi8EcbTzsHA8M7PR6PTZZlNDQ0TFIviiJ27doFr9d7f3gwhr6+PuzcuRORSARFRUVwOBwAAKvVCsYYGhoaJrkYCoWQnZ2NcDiMaDSa3NrYdBLp1tTNYlLS6Pbt2ykvL29K5c899xwNDw9P6PqRkRFqaWmhQCAw6UTcu3ePnnnmmSm58vPzqaysjHJzc0PVlS+WcTE1XmS12USLxYLOzs5JX5+SkoK6ujoYjcbxd8FgED09PfD5fPjyyy/R1taGYDA4vq4oCurq6qAoyiS+np4eWCwWqKoqBUfDiwVieMJutyMajcLv909K2LRpExUWFjIA8Pv9OHz4MA4ePIgrV64gEAgAAIxGI3JyclBeXo61a9fCaDTi6aefRnl5Od5+++0JfH6/H4IgQBRFRCLRXExLmza8evVq2r59+yS7srKyYp2dnTEiohs3btDGjRvJYDBMaS0AkmWZKioqqKuri4iIWltbKTMzc0KMVqulmpoaKiwspNXPru7ieJ6TZFlGLBaboDQpKQm1tbW80+kUbt++ja1bt+L48eMoKCiAJEmTnDKZTPB4PDh06BBqa2tx584dzJ49GzU1NdBoNONxRDTOzwu8jeMFgRhj0Gq1EwiXLVuGDRs2MABobm7GmTNnYDAYYLVaUVpaCrfbDUVRYLFYkJubi5KSEuj1ephMJpw+fRotLS0AgIqKChQVFY3zchwHrVYLjuPAMZYQJJ0uEIlErIqiQBAExONx2Gw2bNu2bbzxCgoK8NJLL+HAgQNoamqCy+VCQUEBOI4DEUFVVQwMDODmzZuIx+NUVVWFvLw8BgAWiwXbtm1DY2MjhoaGoNVqIUkSiAgcxw0Iep3U7ff7rRaLBbIsY2hoCJs2bRq/bACAwWDArl27oCgK9u/fjy+++AKSJEGn0wEARkdHEQ6HIUkStmzZktiyZQsMBgP/IN/r9aKsrAzvvPMOFEWBKIpQVRUaQdPNP+6a9dRIKDi/oKAAbW1tMJvN2L17N6xW66Rh5PF4sHDhQmg0GgSDwfGZn56ejuXLl+ONN95AWVkZJ0kS9+1cnucxY8YMfPrpp3A4HJg+fTp6enqgmEx/E0yy8bPgaGhjb1+fvri4GA6HAy6XC1NBo9HA4/EgLy8PgUBgwjGUZRkcx+FhyM7ORl1dHbq7uzEwMACdKAYEjjvNL3oqzzcSCXtD4ZB98+bNWLp06aSG/C4YYxBFEUajEUajEaIogjGGR+HBGD537hz0ktQocvzvuD+ffK/fIEkfR6NRMplMMBgM40flhwQRQa/Xw+l0Qq/XJ0SN9tCQRhgQKoo3IDIa+UgxKxVnz56dm0gkcPnyZVy8ePF7Lf1fUVhYCEVR0NrairTU1JbbX/f8Va8mIBi4JFzydXbP1vC7jx87tre3t1fvdrvxySefoL29/Qcpnp+fD5fLhYaGBvT19oZlnfR7zmbuFoZGwDdebUbJ4mIka6RrY1BTfcNDT1ksFrZq1Sp0dnbi9u3b/3dhjuOwZMkSVFdXo6enB193dZEk6uo18fgefiwWq//oA/AAsHpWHga4SFzLCZcSoMzBe4OPG41GlJSUIBaLoaura9KofhQURcHGjRuxfv16dHV1oaOjAwLPH9MCv4wzzucQefzz0uX7As60NWKhax6i2vgIT9xFlRKZQ8NDM1VVZcuXL8f8+fMRiUQwNDSEsbGxhxZljMFms8Hr9eK1115DVlYWrl69ihs3bhAjnOBV2qLy3C31Zj/+cPzI/ZxvE7yyohIhcwy8yqYzDb9T1EvlVqtVmjVrFtLS0jAwMIDm5ma0t7ejv78f4XAYjDHIsgy73Q63242cnBwYDAbcunUL165dg8/nC3NE73MJ2sV4vjfuH8H+o4e/Ef3dr/jp4lWIpZvA1IQUF7j1Wl1SrUGWcxVF4adNm4aUlBRIkgTGGBKJBIgIjDGoqjp+Q+7r64PP50uMRaMtPGGPhvBxDBR2qRx2HNw/0bWH2fly6QvI6BhBV65pOvHcOkGrKRVFMVfU6WSdTsdEUQTP8yAiRKPRB/8DikQiwXgsdpUDDmsY+3DrPW13vUXFb/+yb+pte1QzVT2/AXxgFBGzZGUa4cfgWCHAchjPZWgEIYVAFI/F71KCehlDG8+xszxw4TEdP+hPMPrNu/Xfy/8fHhSgRu908UEAAAAldEVYdGRhdGU6Y3JlYXRlADIwMjAtMDctMTlUMTM6MjA6MTUtMDQ6MDCjf0cuAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDIwLTA3LTE5VDEzOjIwOjE1LTA0OjAw0iL/kgAAAABJRU5ErkJggg=="/>
</head><body>
<script>window.onload = function () {
var totalNumberOfImages = document.querySelectorAll("div.responsive").length;
document.getElementById("total").innerHTML = ":: Total images: " + totalNumberOfImages + " ::";};
function f(img){
navigator.clipboard.writeText(img.alt);}
</script>
<p id="total"></p>
<p>:: With Javascript enabled: Click on the image to get the corresponding RTSP link ::</p>\n\n"""
    )
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Generating {path}")
    path.write_text(html)



def load_paths(urls_path)-> list[str]:
    with open(urls_path, "r") as f:
        return [url.strip() for url in f.readlines()[2::]]

def create_folder(path: Path):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Creating {path}")
    path.mkdir(parents=True)


def create_file(path: Path):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Creating {path}")
    path.touch()


def append_result(pic_file: Path, rtsp_url: str):
    # Append to .txt result file
    with RESULT_FILE.open("a") as f:
        f.write(f"{rtsp_url}\n")

    # Insert to .html gallery file
    if pic_file.exists():
        with HTML_FILE.open("a") as f:
            f.write(
                (
                    '<div class="responsive"><div class="gallery">\n'
                    f'<img src="{pic_file.parent.name}/{pic_file.name}" alt="{rtsp_url}" '
                    'width="600" height="400" onclick="f(this)"></div></div>\n\n'
                )
            )

def escape_chars(s: str):
    # Escape every character that's not a letter,
    # '_', '-', '.' or space with an '_'.
    return re.sub(r"[^\w\-_. ]", "_", s)
