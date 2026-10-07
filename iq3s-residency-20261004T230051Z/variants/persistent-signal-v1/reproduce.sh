#!/usr/bin/env bash
set -euo pipefail
"/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-signal-v1/benchmark-32k.sh" "$@"
"/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-signal-v1/benchmark-128k.sh" "$@"
