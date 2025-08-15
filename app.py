from __future__ import annotations
from flask import Flask, render_template, request
from datetime import datetime, timedelta, timezone

# Mapping of short time zone codes to fixed UTC offsets
CODE_TO_TZ: dict[str, timezone] = {}


def _build_code_map() -> None:
    """Populate CODE_TO_TZ with common offset-based codes."""
    for h in range(-12, 15):  # UTC-12 .. UTC+14
        if h == 0:
            continue
        name = f"UTC{h:+03d}:00"
        CODE_TO_TZ[name] = timezone(timedelta(hours=h), name)
    # Common aliases
    CODE_TO_TZ["UTC"] = timezone.utc
    CODE_TO_TZ["GMT"] = timezone.utc
    CODE_TO_TZ["CET"] = timezone(timedelta(hours=1), "CET")
    CODE_TO_TZ["CEST"] = timezone(timedelta(hours=2), "CEST")
    CODE_TO_TZ["EST"] = timezone(timedelta(hours=-5), "EST")
    CODE_TO_TZ["EDT"] = timezone(timedelta(hours=-4), "EDT")
    CODE_TO_TZ["CST"] = timezone(timedelta(hours=-6), "CST")
    CODE_TO_TZ["CDT"] = timezone(timedelta(hours=-5), "CDT")
    CODE_TO_TZ["MST"] = timezone(timedelta(hours=-7), "MST")
    CODE_TO_TZ["MDT"] = timezone(timedelta(hours=-6), "MDT")
    CODE_TO_TZ["PST"] = timezone(timedelta(hours=-8), "PST")
    CODE_TO_TZ["PDT"] = timezone(timedelta(hours=-7), "PDT")
    CODE_TO_TZ["BST"] = timezone(timedelta(hours=1), "BST")
    CODE_TO_TZ["IST"] = timezone(timedelta(hours=5, minutes=30), "IST")


_build_code_map()

ZONES = sorted(CODE_TO_TZ.keys())

app = Flask(__name__)

def now_utc():
    return datetime.now(tz=timezone.utc)


def fmt_offset(tz: timezone) -> str:
    # Returns a pretty UTC offset like "+02:00" or "-05:30"
    offset = datetime.now(tz).utcoffset() or timedelta()
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    return f"{sign}{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def current_time_in_zone(tz_name: str):
    tz = CODE_TO_TZ[tz_name]
    dt = now_utc().astimezone(tz)
    return {
        "zone": tz_name,
        "now": dt,
        "offset": fmt_offset(tz),
        "abbr": dt.tzname() or "",
    }


def difference(tz_a: str, tz_b: str, at: datetime | None = None):
    at = at or now_utc()
    a = at.astimezone(CODE_TO_TZ[tz_a])
    b = at.astimezone(CODE_TO_TZ[tz_b])
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
    # Optional query params: my_tz, other_tz
    my_tz = request.args.get("my_tz") or "UTC"
    other_tz = request.args.get("other_tz") or "UTC+01:00"

    # Build quick comparison and a small conversion table
    conv_base = now_utc()
    diff = difference(my_tz, other_tz, conv_base)

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
        a = base.astimezone(CODE_TO_TZ[my_tz])
        b = base.astimezone(CODE_TO_TZ[other_tz])
        conversion.append({
            "label": label,
            "a": a,
            "b": b,
        })

    # Table of all zones with current time & offset (trimmed client‑side with search)
    all_rows = [current_time_in_zone(z) for z in ZONES]

    return render_template(
        "index.html",
        zones=ZONES,
        my_tz=my_tz,
        other_tz=other_tz,
        diff=diff,
        conversion=conversion,
        all_rows=all_rows,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
