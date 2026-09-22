from datetime import datetime
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


def ist_now() -> datetime:
    """
    Return current timestamp in IST.
    """
    return datetime.now(IST)