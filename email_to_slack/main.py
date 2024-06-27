import email.header
import email.message
import email.parser
import email.policy
import sys
from typing import Any, Optional, Tuple

import requests

from email_to_slack.config import INCOMING_WEBHOOK_URL

EX_TEMPFAIL = 75

SLACK_MAX_LINES = 56


def decode_header_part(r: Tuple[Any, Optional[Any]]) -> str:
    if isinstance(r[0], str):
        return r[0]
    if isinstance(r[0], bytes) and isinstance(r[1], str):
        return r[0].decode(r[1], "replace")
    raise ValueError


def send_message(message: str) -> None:
    try:
        response = requests.post(
            INCOMING_WEBHOOK_URL,
            json={
                "text": message.rstrip(),
            },
            timeout=5,
        )
    except requests.exceptions.Timeout:
        sys.exit(EX_TEMPFAIL)  # retry
    if response.status_code == 500:
        sys.exit(EX_TEMPFAIL)  # retry


def main() -> None:
    message = sys.stdin.read()
    msgobj = email.parser.Parser(policy=email.policy.default).parsestr(message)
    if not isinstance(msgobj, email.message.EmailMessage):
        return  # error

    subject = "".join(
        decode_header_part(r)
        for r in email.header.decode_header(msgobj["Subject"])
    )

    bodyobj = msgobj.get_body(preferencelist=("plain",))
    if not isinstance(bodyobj, email.message.MIMEPart):
        return  # error
    body = bodyobj.get_content()
    if not isinstance(body, str):
        return  # error

    parts = list[str]()
    part = f"Subject: `{subject}`\n```\n"
    part_nlines = 2
    for line in body.split("\n"):
        part += line + "\n"
        part_nlines += 1
        if part_nlines >= SLACK_MAX_LINES - 1:
            parts.append(part.rstrip() + "\n```")
            part = "```\n"
            part_nlines = 1
    if part != "":
        parts.append(part.rstrip() + "\n```")

    if len(parts) > 3:
        parts = parts[:3]
        parts[-1] += "\n(snip)"

    for part in parts:
        send_message(part)
