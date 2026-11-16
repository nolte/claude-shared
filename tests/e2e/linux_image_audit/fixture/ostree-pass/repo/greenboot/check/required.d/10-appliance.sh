#!/bin/sh
# greenboot required health check: a non-zero exit marks this boot unhealthy;
# greenboot then reboots and, after the allowed attempts, rolls back.
set -eu
systemctl is-active --quiet appliance.service
