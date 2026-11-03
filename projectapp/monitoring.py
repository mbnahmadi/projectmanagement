import os
import json
import logging
import urllib.request
import urllib.parse

from datetime import datetime, timedelta
import pytz



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

    logging.info("Push sent successfully: %s", status)
