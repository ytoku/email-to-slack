#!/bin/sh
LOGFILE=/var/log/email-to-slack/notify.log
cd $(dirname $0)
date -Iseconds >>$LOGFILE
# Suppress any output to prevent error mail storm
exec python3 notify.py >>$LOGFILE 2>&1
