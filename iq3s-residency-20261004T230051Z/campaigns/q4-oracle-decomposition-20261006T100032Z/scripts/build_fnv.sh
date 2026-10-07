#!/usr/bin/env bash
set -euo pipefail
campaign=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
timeout 60s g++ -O3 -shared -fPIC "$campaign/scripts/fnv64.cpp" -o "$campaign/analysis/libfnv64.so"
sha256sum "$campaign/analysis/libfnv64.so"
