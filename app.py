from __future__ import annotations
from flask import Flask, render_template, request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

app = Flask(__name__)

# Map simple time codes to zoneinfo names (fixed offsets)
TIME_CODES = {
    "UTC-12": "Etc/GMT+12",
    "UTC-11": "Etc/GMT+11",
    "UTC-10": "Etc/GMT+10",
    "UTC-9": "Etc/GMT+9",
    "UTC-8": "Etc/GMT+8",
    "UTC-7": "Etc/GMT+7",
    "UTC-6": "Etc/GMT+6",
    "UTC-5": "Etc/GMT+5",
    "UTC-4": "Etc/GMT+4",
    "UTC-3": "Etc/GMT+3",
    "UTC-2": "Etc/GMT+2",
    "UTC-1": "Etc/GMT+1",
    "UTC": "UTC",
    "UTC+1": "Etc/GMT-1",
    "UTC+2": "Etc/GMT-2",
    "UTC+3": "Etc/GMT-3",
    "UTC+4": "Etc/GMT-4",
    "UTC+5": "Etc/GMT-5",
    "UTC+6": "Etc/GMT-6",
    "UTC+7": "Etc/GMT-7",
    "UTC+8": "Etc/GMT-8",
    "UTC+9": "Etc/GMT-9",
    "UTC+10": "Etc/GMT-10",
    "UTC+11": "Etc/GMT-11",
    "UTC+12": "Etc/GMT-12",
    "UTC+13": "Etc/GMT-13",
    "UTC+14": "Etc/GMT-14",
    "CET": "Etc/GMT-1",
    "CEST": "Etc/GMT-2",
}

ZONES = list(TIME_CODES.keys())


def now_utc():
    return datetime.now(tz=ZoneInfo("UTC"))


def fmt_offset(tz: ZoneInfo) -> str:
    # Returns a pretty UTC offset like "+02:00" or "-05:30"
    offset = datetime.now(tz).utcoffset() or timedelta()
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    return f"{sign}{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def current_time_in_zone(code: str, tz_name: str):
    tz = ZoneInfo(tz_name)
    dt = now_utc().astimezone(tz)
    return {
        "zone": code,
        "now": dt,
        "offset": fmt_offset(tz),
        "abbr": dt.tzname() or "",
    }


def difference(tz_a: str, tz_b: str, at: datetime | None = None):
    at = at or now_utc()
    a = at.astimezone(ZoneInfo(tz_a))
    b = at.astimezone(ZoneInfo(tz_b))
    # Compare the UTC offsets to determine the difference between zones
    offset_a = a.utcoffset() or timedelta()
    offset_b = b.utcoffset() or timedelta()
    delta = (offset_b - offset_a).total_seconds() / 3600.0  # hours (float)
    # Normalize to absolute hours/minutes for display, keep sign separately
    sign = 1 if delta > 0 else -1 if delta < 0 else 0
    h = int(abs(delta))
    m = int(round((abs(delta) - h) * 60))
    pretty_abs = f"{h}h {m:02d}m"
    direction = "ahead of" if sign > 0 else "behind" if sign < 0 else "the same time as"
    if sign == 0:
        description = f"{tz_b} is the same time as {tz_a}"
    else:
        description = f"{tz_b} is {pretty_abs} {direction} {tz_a}"
    return {
        "a": a,
        "b": b,
        "hours": sign * h,
        "minutes": sign * m,
        "pretty": f"{('+' if delta >= 0 else '-')}{h:01d}h {m:02d}m",
        "direction": direction,
        "pretty_abs": pretty_abs,
        "description": description,
    }


@app.route("/")
def index():
    # Optional query params: my_tz, other_tz (codes)
    my_code = request.args.get("my_tz") or "UTC"
    other_code = request.args.get("other_tz") or "UTC+1"
    my_tz = TIME_CODES.get(my_code, "UTC")
    other_tz = TIME_CODES.get(other_code, "UTC+1")

    # Build quick comparison and a small conversion table
    conv_base = now_utc()
    diff = difference(my_tz, other_tz, conv_base)
    diff["description"] = diff["description"].replace(other_tz, other_code).replace(my_tz, my_code)

    # common slots to visualize (local time for tz_a and corresponding tz_b)
    common_slots = [
        ("Now", conv_base),
        ("Today 09:00", conv_base.replace(hour=9, minute=0, second=0, microsecond=0)),
        ("Today 13:00", conv_base.replace(hour=13, minute=0, second=0, microsecond=0)),
        ("Today 18:00", conv_base.replace(hour=18, minute=0, second=0, microsecond=0)),
        ("Tomorrow 09:00", (conv_base + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)),
    ]

    conversion = []
    for label, base in common_slots:
        a = base.astimezone(ZoneInfo(my_tz))
        b = base.astimezone(ZoneInfo(other_tz))
        conversion.append({
            "label": label,
            "a": a,
            "b": b,
        })

    # Table of all zones with current time & offset (trimmed client‑side with search)
    all_rows = [current_time_in_zone(code, tz) for code, tz in TIME_CODES.items()]

    return render_template(
        "index.html",
        zones=ZONES,
        my_tz=my_code,
        other_tz=other_code,
        diff=diff,
        conversion=conversion,
        all_rows=all_rows,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
