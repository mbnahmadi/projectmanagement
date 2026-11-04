import os
import json
import logging
import urllib.request
import urllib.parse

from datetime import datetime
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)

TEHRAN_TZ = ZoneInfo("Asia/Tehran")

STATE_FILE = (
    "/home/mobin/control-project/monitoring/task_state.json"
)


# -------------------------
# State Management
# -------------------------

def load_task_state():
    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(STATE_FILE, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        logger.exception("Could not read task state file")
        return {}


def save_task_state(state):
    temp_file = STATE_FILE + ".tmp"

    with open(temp_file, "w") as file:
        json.dump(state, file, indent=4)

    os.replace(temp_file, STATE_FILE)


def record_task_success(monitor_type, completed_at):

    if monitor_type not in ("morning", "evening"):
        raise ValueError("Invalid monitor type")

    state = load_task_state()

    state[monitor_type] = completed_at

    save_task_state(state)

    logger.info(
        "Task success recorded: %s at %s",
        monitor_type,
        completed_at
    )


# -------------------------
# Uptime Kuma Push
# -------------------------

def send_push(push_url, status, message):

    if not push_url:
        raise ValueError("Push URL is not configured")

    parts = urllib.parse.urlsplit(push_url)

    query_params = urllib.parse.parse_qsl(
        parts.query,
        keep_blank_values=True
    )

    query_params = [
        (key, value)
        for key, value in query_params
        if key not in ("status", "msg")
    ]

    query_params.extend([
        ("status", status),
        ("msg", message[:200])
    ])

    query_string = urllib.parse.urlencode(query_params)

    url = urllib.parse.urlunsplit((
        parts.scheme,
        parts.netloc,
        parts.path,
        query_string,
        parts.fragment
    ))

    request = urllib.request.Request(url)

    with urllib.request.urlopen(request, timeout=15) as response:

        response_body = response.read().decode("utf-8")

        if response.getcode() != 200:
            raise RuntimeError(
                "Uptime Kuma returned HTTP {}".format(
                    response.getcode()
                )
            )

        result = json.loads(response_body)

        if not result.get("ok"):
            raise RuntimeError(
                "Uptime Kuma rejected heartbeat: {}".format(
                    response_body
                )
            )

    logger.info("Uptime Kuma push sent successfully: %s", status)


# -------------------------
# Monitor Status
# -------------------------

def check_monitor_status(monitor_type, state, now=None):

    if now is None:
        now = datetime.now(TEHRAN_TZ)

    if monitor_type == "morning":
        deadline_hour = 6

    elif monitor_type == "evening":
        deadline_hour = 18

    else:
        raise ValueError("Invalid monitor type")

    if now.hour < deadline_hour:
        return {
            "status": "pending",
            "message": "{} task is not due yet".format(
                monitor_type
            )
        }

    last_success = state.get(monitor_type)

    if last_success:
        try:
            completed_at = datetime.fromisoformat(last_success)

            # Convert to Tehran time before comparing dates
            if completed_at.tzinfo is not None:
                completed_at = completed_at.astimezone(TEHRAN_TZ)

        except (ValueError, TypeError):
            completed_at = None
    else:
        completed_at = None

    if completed_at and completed_at.date() == now.date():
        return {
            "status": "up",
            "message": "{} task completed successfully".format(
                monitor_type
            )
        }

    return {
        "status": "down",
        "message": "{} task was not completed for {}".format(
            monitor_type,
            now.date()
        )
    }


# -------------------------
# Watchdog
# -------------------------

def get_monitor_url(monitor_type):

    if monitor_type == "morning":
        return os.getenv("PM_MORNING_PUSH_URL")

    elif monitor_type == "evening":
        return os.getenv("PM_EVENING_PUSH_URL")

    raise ValueError("Invalid monitor type")


def run_watchdog():

    state = load_task_state()

    now = datetime.now(TEHRAN_TZ)

    for monitor_type in ("morning", "evening"):

        result = check_monitor_status(
            monitor_type,
            state,
            now
        )

        current_status = result["status"]

        # Before the deadline, do nothing
        if current_status == "pending":
            continue

        last_reported_status = state.get(
            "{}_status".format(monitor_type)
        )

        # No status change: no need to send another Push
        if current_status == last_reported_status:
            continue

        monitor_url = get_monitor_url(monitor_type)

        try:
            send_push(
                monitor_url,
                current_status,
                result["message"]
            )

            # Save status only after successful Push
            state["{}_status".format(monitor_type)] = current_status

            save_task_state(state)

            logger.info(
                "Monitor status changed: %s -> %s",
                monitor_type,
                current_status
            )

        except Exception:
            logger.exception(
                "Watchdog failed for monitor: %s",
                monitor_type
            )