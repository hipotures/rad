#!/usr/bin/env bash
set -euo pipefail
cd /srv/ai/research/iq3s-residency-20261004T230051Z
"/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-frequency-v5/benchmark-32k.sh" "$@"
"/srv/ai/research/iq3s-residency-20261004T230051Z/variants/diagnostic-frequency-v5/benchmark-128k.sh" "$@"
