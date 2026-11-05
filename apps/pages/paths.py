"""One way to write an address, so an old link matches its redirect however it is typed."""

import posixpath
from urllib.parse import unquote, urlsplit


def normalize_path(value: str) -> str:
    """'/About-Us', 'about-us/', 'https://distinctive.co.zw/about-us/?x=1' → '/about-us/'.

    Lower case (WordPress addresses are), no host, query or fragment, a leading slash, and a
    trailing slash unless the last part looks like a file (/feed.xml, /index.php).
    """
    value = (value or "").strip()
    if "://" in value:  # a full address: keep only its path
        value = urlsplit(value).path
    path = unquote(value.split("?")[0].split("#")[0] or "/").lower()
    if not path.startswith("/"):
        path = "/" + path
    while "//" in path:
        path = path.replace("//", "/")
    last = path.rsplit("/", 1)[-1]
    if not path.endswith("/") and not posixpath.splitext(last)[1]:
        path += "/"
    return path
