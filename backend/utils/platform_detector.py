import re


SUPPORTED_PLATFORMS = [
    "youtube.com", "youtu.be",
    "instagram.com",
    "facebook.com", "fb.watch",
    "twitter.com", "x.com",
    "tiktok.com",
    "dailymotion.com",
    "vimeo.com",
    "reddit.com",
    "pinterest.com"
]


def is_valid_url(url):
    pattern = re.compile(
        r'^(https?://)'
        r'([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}'
        r'(/[^\s]*)?$'
    )
    return bool(pattern.match(url.strip()))


def is_supported(url):
    url_lower = url.lower()
    for platform in SUPPORTED_PLATFORMS:
        if platform in url_lower:
            return True
    return False


def detect_platform(url):
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "instagram.com" in url_lower:
        return "instagram"
    elif "facebook.com" in url_lower or "fb.watch" in url_lower:
        return "facebook"
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return "twitter"
    elif "tiktok.com" in url_lower:
        return "tiktok"
    elif "dailymotion.com" in url_lower:
        return "dailymotion"
    elif "vimeo.com" in url_lower:
        return "vimeo"
    elif "reddit.com" in url_lower:
        return "reddit"
    elif "pinterest.com" in url_lower:
        return "pinterest"
    else:
        return "unknown"