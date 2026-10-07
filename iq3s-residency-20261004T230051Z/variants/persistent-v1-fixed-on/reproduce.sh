#!/usr/bin/env bash
set -euo pipefail
"/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-fixed-on/benchmark-32k.sh" "$@"
"/srv/ai/research/iq3s-residency-20261004T230051Z/variants/persistent-v1-fixed-on/benchmark-128k.sh" "$@"
