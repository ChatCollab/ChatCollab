
from source.source import run_slack_source
import time

print("Starting Slack Source...")

# Wait 3 seconds to allow timeline to come online. TODO: In future, should build in a check for timeline status.
time.sleep(3)


def print_to_logs_slack_source(message):
    print("[SLACK SOURCE] " + message, flush=True)

# Start async function of run_slack_source without threading
run_slack_source(print_to_output=print_to_logs_slack_source)