#!/usr/bin/env bash
set -euo pipefail
"/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-pool-default/benchmark-32k.sh" "$@"
"/srv/ai/research/iq3s-residency-20261004T230051Z/variants/p1-pool-default/benchmark-128k.sh" "$@"
