# Historical prompt catalog

Exact messages are retained in workload-inventory.json and hashed payload snapshots. Representative excerpts below are quoted as historical data, including identifiers.


## E026-code

18 payloads; saved token lengths [28400, 28510, 126716, 126826]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/4b2d90f4dde801b150dc9aece7d35ac077e6a90259d768160e8cb3e66ec6f11d.json).

Actual instruction:

```text
 Review the supplied repository as an offline engineer. Develop a complete transactional storage audit: identify invariants, reason through crash/retry/concurrency cases, then propose concrete Python/SQLite reference changes and tests. Produce a substantial engineering document with at least 30 numbered failure scenarios, worked SQL transactions, pseudocode, and an implementation plan. Use the provided source evidence and distinguish confirmed findings from hypotheses. No tools are available.
```

Representative source/prefix:

```text
Independent pool validation. Document family code. Nonce p0-32k-1.


===== SOURCE /home/user/DEV/heg/README.md =====
# Structural Graph Conjecture Lab

Structural Graph Conjecture Lab (`sglab`) is a Linux research system for
reproducible searches for finite counterexamples to structural graph
conjectures. Its implemented research target is the Erdős–Gyárfás conjecture:

> Every finite simple graph with minimum degree at least 3 contains a simple
> cycle whose length is a power of two.

The project is an engineering and experimentation system. It does not claim
that the conjecture has been resolved.

## What the system does

- runs bounded graph-search lanes with deterministic checkpoints;
- uses an AI Research Director to choose reviewed search actions;
- keeps the Director stateless and supplies a bounded scientific-memory
  snapshot on 
```


## E026-math

18 payloads; saved token lengths [28411, 28521, 126717, 126827]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/095ce981d0562483c686a7f6d90164dd035549e754af92248f6b60651a7ed016.json).

Actual instruction:

```text
 Develop a rigorous tutorial and reference implementation for exact rational polynomial interpolation and stable numerical evaluation, using the supplied numerical-library source as context. Derive Lagrange, Newton and barycentric formulations; prove correctness and uniqueness; analyze repeated nodes, degree reduction and conditioning. Work at least 20 nontrivial examples step by step with rational coefficients and explicit recurrence checks. Include complete Python reference implementations and property tests. Continue through the full derivations and examples, without a short summary or tool calls.
```

Representative source/prefix:

```text
Independent pool validation. Document family math. Nonce p0-32k-1.


===== SOURCE /usr/lib/python3.14/fractions.py =====
# Originally contributed by Sjoerd Mullender.
# Significantly modified by Jeffrey Yasskin <jyasskin at gmail.com>.

"""Fraction, infinite-precision, rational numbers."""

import functools
import math
import numbers
import operator
import re
import sys

__all__ = ['Fraction']


# Constants related to the hash implementation;  hash(x) is based
# on the reduction of x modulo the prime _PyHASH_MODULUS.
_PyHASH_MODULUS = sys.hash_info.modulus
# Value to be used for rationals that reduce to infinity modulo
# _PyHASH_MODULUS.
_PyHASH_INF = sys.hash_info.inf

@functools.lru_cache(maxsize = 1 << 14)
def _hash_algorithm(numerator, denominator):

    # To make sure that the hash of a Fraction agrees with the hash
    # of a numeri
```


## E026-prose

18 payloads; saved token lengths [28408, 28518, 126717, 126827]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/f70c1330b584463e72eec9828a1d59fea7d99c5a95a5b6614ab330ffba2359cd.json).

Actual instruction:

```text
 Write an extensive operational training handbook based on the supplied HTTP standards. Explain request semantics, retry safety, idempotency, conditional requests, cache invalidation and realistic proxy/client failure recovery in clear prose. Include at least 30 detailed incident narratives with cause, observation, decision, recovery and verification; provide a structured test catalog and worked messages. Distinguish normative requirements from application advice. Complete the document directly; no tools are available.
```

Representative source/prefix:

```text
Independent pool validation. Document family prose. Nonce p0-32k-1.


===== SOURCE /srv/ai/research/iq3s-residency-20261004T230051Z/sources/rfc9110.txt =====
﻿



Internet Engineering Task Force (IETF)                  R. Fielding, Ed.
Request for Comments: 9110                                         Adobe
STD: 97                                               M. Nottingham, Ed.
Obsoletes: 2818, 7230, 7231, 7232, 7233, 7235,                    Fastly
           7538, 7615, 7694                              J. Reschke, Ed.
Updates: 3864                                                 greenbytes
Category: Standards Track                                      June 2022
ISSN: 2070-1721


                             HTTP Semantics

Abstract

   The Hypertext Transfer Protocol (HTTP) is a stateless application-
   level protocol for distributed
```


## cpython-asyncio-queues

2 payloads; saved token lengths [2499]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/61c4afd609cf690c98dba3682ea5d1fd8191d6c3d9005bc93f5b32dd5e9c30b5.json).

Actual instruction:

```text

Design a bounded asynchronous log ingestion service around this queue implementation. Explain cancellation, backpressure, shutdown, retries, and ordering; provide a concrete Python implementation and adversarial tests.
```

Representative source/prefix:

```text
Source document:
__all__ = (
    'Queue',
    'PriorityQueue',
    'LifoQueue',
    'QueueFull',
    'QueueEmpty',
    'QueueShutDown',
)

import collections
import heapq
from types import GenericAlias

from . import locks
from . import mixins


class QueueEmpty(Exception):
    """Raised when Queue.get_nowait() is called on an empty Queue."""
    pass


class QueueFull(Exception):
    """Raised when the Queue.put_nowait() method is called on a full Queue."""
    pass


class QueueShutDown(Exception):
    """Raised when putting on to or getting from a shut-down Queue."""
    pass


class Queue(mixins._LoopBoundMixin):
    """A queue, useful for coordinating producer and consumer coroutines.

    If maxsize is less than or equal to zero, the queue size is infinite. If it
    is an integer greater than 0, then "await put()" will block when t
```


## cpython-logging-handlers

1 payloads; saved token lengths [6376]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/c9b7817d2dbcad28e21a1278aeaf65316c3310aa2f6d5848fa09c990c7e3b0c6.json).

Actual instruction:

```text

Design reliable rotating audit logs for a multiprocess local application based on this implementation. Compare queue-based logging and direct file writes; describe failure handling, ownership and executable test scenarios.
```

Representative source/prefix:

```text
Source document:
# Copyright 2001-2021 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Vinay Sajip
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, 
```


## cpython-thread-executor

1 payloads; saved token lengths [2220]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/84685d5f2694ae4127851f22682c816fec00b099166b5b5e234657dcadd778fc.json).

Actual instruction:

```text

Review this executor implementation for a service that submits dependent blocking jobs. Explain deadlocks, cancellation, shutdown and failure propagation; design an application wrapper with tests without modifying this library.
```

Representative source/prefix:

```text
Source document:
# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Implements ThreadPoolExecutor."""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

from concurrent.futures import _base
import itertools
import queue
import threading
import types
import weakref
import os


_threads_queues = weakref.WeakKeyDictionary()
_shutdown = False
# Lock that ensures that new workers are not created while the interpreter is
# shutting down. Must be held while mutating _threads_queues and _shutdown.
_global_shutdown_lock = threading.Lock()

def _python_exit():
    global _shutdown
    with _global_shutdown_lock:
        _shutdown = True
    items = list(_threads_queues.items())
    for t, q in items:
        q.put(None)
    for t, q in items:
        t.join()

# Register for `_python_exit()` t
```


## cpython-zipfile

1 payloads; saved token lengths [6991]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/521f4e333a693a0a8d326822ee03da62e7f21a9fb83dc88af48a142545843239.json).

Actual instruction:

```text

Implement a safe offline archive importer using this implementation as reference. Discuss path normalization, links, size limits, streaming, atomic publication and interrupted extraction. Include Python code and tests.
```

Representative source/prefix:

```text
Source document:
"""
Read and write ZIP files.

XXX references to utf-8 need further investigation.
"""
import binascii
import importlib.util
import io
import os
import shutil
import stat
import struct
import sys
import threading
import time

try:
    import zlib # We may need its compression method
    crc32 = zlib.crc32
except ImportError:
    zlib = None
    crc32 = binascii.crc32

try:
    import bz2 # We may need its compression method
except ImportError:
    bz2 = None

try:
    import lzma # We may need its compression method
except ImportError:
    lzma = None

try:
    from compression import zstd # We may need its compression method
except ImportError:
    zstd = None

__all__ = ["BadZipFile", "BadZipfile", "error",
           "ZIP_STORED", "ZIP_DEFLATED", "ZIP_BZIP2", "ZIP_LZMA",
           "ZIP_ZSTANDARD", "is_zipfile", "ZipIn
```


## strata-repository-maintenance

30 payloads; saved token lengths [4096, 28378, 28379, 28381, 126715, 126716, 126719, 257781, 257783]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/378642860ea23174775b3de861e4692a665796b4674d63fa62996d12fea6aafb.json).

Actual instruction:

```text
 This is an offline review of the complete repository excerpts already supplied above. No tools are available. Produce the answer directly; do not announce exploration, request tools, or output tool-call markup. Produce a detailed repository maintenance plan in 40 numbered sections. For each section, identify a distinct component from the supplied code, explain its responsibilities, propose a concrete change with a full unified diff and at least two verification cases. Continue until all 40 sections are complete; include enough detail for another engineer to implement them. Do not summarize early.
```

Representative source/prefix:

```text
Repository files and coding-agent history:

### CMakeLists.txt
```
﻿# Strata Engine - top-level build (P1.S1).
#
# Targets (phase-1 Ă‚Â§P1.S1): `strata_artifact` (no CUDA dependency), `tests`.  `strata_plan` and the C++
# `strata-pack` are added when their sources exist - a target with no sources would make the build graph
# claim something the tree does not have, which is worse than an absent target.
#
# CUDA targets arrive in Phase 2.  The kernels need sm_80 or newer (tf32 mma, bf16 math) and the guard
# below refuses anything older: silently building for a pre-Ampere arch would produce a binary that runs
# and is wrong about its own performance, which is the worst of both outcomes.
cmake_minimum_required(VERSION 3.24)
project(strata VERSION 0.1.31 LANGUAGES CXX)
add_compile_definitions(STRATA_VERSION="${PROJECT_VERSION}")
# issue #31: 
```


## task-cal-prose

5 payloads; saved token lengths [64]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/bab8f23d3fe851c1c13d7c26e7c2e5fa7c5c450d70d63776f55a4b55d6f79c74.json).

Actual instruction:

```text
Write a detailed engineering handbook for incident response in a fictional water-treatment control service. Include communication, failure analysis, recovery and worked incident narratives.
```

Representative source/prefix:

```text
Write a detailed engineering handbook for incident response in a fictional water-treatment control service. Include communication, failure analysis, recovery and worked incident narratives.
```


## task-dev-code

3 payloads; saved token lengths [67]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/b752faef31f65031c77b803a54a3f5c3ac436dcfa493cab369b7c281b36ba4d4.json).

Actual instruction:

```text
Implement a Python dependency graph with topological sorting, cycle reporting, incremental edge updates and tests. Explain the full design and write the implementation and many edge cases.
```

Representative source/prefix:

```text
Implement a Python dependency graph with topological sorting, cycle reporting, incremental edge updates and tests. Explain the full design and write the implementation and many edge cases.
```


## task-dev-math

3 payloads; saved token lengths [66]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/96163ea4a9b280004772e9732541feed473b6630dfca4d70591e01f7357ee719.json).

Actual instruction:

```text
Develop an elementary derivation of finite-state Markov hitting times, then solve six different examples step by step, verifying each with recurrence equations and Python simulation code.
```

Representative source/prefix:

```text
Develop an elementary derivation of finite-state Markov hitting times, then solve six different examples step by step, verifying each with recurrence equations and Python simulation code.
```


## task-hold-code

5 payloads; saved token lengths [72]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/7b0e7f104a286f726299ecb3dfce1cd4765ae9564b3954ce128b074e837f7bd9.json).

Actual instruction:

```text
Design a transactional inventory ledger in SQLite and Python. Specify schema, idempotency, concurrent updates, audit invariants, migration, rollback, and a complete tested reference implementation.
```

Representative source/prefix:

```text
Design a transactional inventory ledger in SQLite and Python. Specify schema, idempotency, concurrent updates, audit invariants, migration, rollback, and a complete tested reference implementation.
```


## task-hold-math

5 payloads; saved token lengths [59]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/7111b72f53902b7761c405f2a6e81372a7d23c400caf171c0f83de7bd73e305c.json).

Actual instruction:

```text
Give a detailed derivation and reference Python implementation for exact rational polynomial interpolation, including error cases, independent examples and property tests.
```

Representative source/prefix:

```text
Give a detailed derivation and reference Python implementation for exact rational polynomial interpolation, including error cases, independent examples and property tests.
```


## task-hold-structured

5 payloads; saved token lengths [69]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/d9cacc1395ac2fb95e020e870786fe2751566d256530da37fc282bb89db3cdcd.json).

Actual instruction:

```text
Produce a structured test catalog as valid JSON with 80 cases for a datetime parser. Each case needs input, expected interpretation, boundary rationale and a test stub.
```

Representative source/prefix:

```text
Produce a structured test catalog as valid JSON with 80 cases for a datetime parser. Each case needs input, expected interpretation, boundary rationale and a test stub.
```


## task-math-1

2 payloads; saved token lengths [162]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/acdbc5a83f92f037b063ef4d38ede9a2f1ce0fecfb7a46f35d15217bf7922653.json).

Actual instruction:

```text

Solve this complete applied problem with derivations, implementation detail and verification.
```

Representative source/prefix:

```text
Source document:
A backup service has n=5 independent drives, each exponential failure rate lambda=.02/day. It tolerates at most2 simultaneous failed drives; one repair worker repairs at rate mu=.5/day. Derive the continuous-time Markov chain, stationary distribution, probability of data-loss state, expected time to first data loss starting healthy, and sensitivity to doubling repair rate. Explain every boundary and distinguish first passage from stationary risk. Give a reproducible numerical algorithm and check limiting cases.

Task:
Solve this complete applied problem with derivations, implementation detail and verification.
```


## task-math-2

1 payloads; saved token lengths [166]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/c509233ea8c3d77afd0739ef37b3a61f4b0db1954124afd6bfe4b47922b0f555.json).

Actual instruction:

```text

Solve this complete applied problem with derivations, implementation detail and verification.
```

Representative source/prefix:

```text
Source document:
A warehouse replenishes one item every seven days. Daily demand is independent Poisson with mean18, supplier lead time is three days, fixed order cost120 and unit holding cost.04/day. Derive a periodic-review base-stock policy at99% cycle-service probability, distinguish cycle service from fill rate, estimate shortage expectation without normal-tail shortcuts, and compare with a continuous-review policy. Show numerical calculations, exact sums and assumptions; discuss how correlated demand invalidates the result.

Task:
Solve this complete applied problem with derivations, implementation detail and verification.
```


## task-math-3

1 payloads; saved token lengths [180]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/e199c408b4836249d6ef9a629263e36349c02d4be1af422d1aeb80bf2f630b4a.json).

Actual instruction:

```text

Solve this complete applied problem with derivations, implementation detail and verification.
```

Representative source/prefix:

```text
Source document:
A sensor reports y(t)=a exp(-bt)+c with Gaussian noise sigma=.03 at t=0,1,2,4,8. Observations are1.08,.86,.66,.45,.24. Derive nonlinear least-squares gradients and Hessian, perform an explicit damped Gauss-Newton calculation, give a convergent algorithm, estimate uncertainty and discuss identifiability/parameter correlation. Compare fitting log-transformed data with fitting original measurements, including the role of unknown c. Provide pseudocode and consistency checks.

Task:
Solve this complete applied problem with derivations, implementation detail and verification.
```


## task-math-4

1 payloads; saved token lengths [171]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/55b1e378a21bb092fc4e418a3ba84eb51d71cacd1907080eb0716ec6d0bf11c1.json).

Actual instruction:

```text

Solve this complete applied problem with derivations, implementation detail and verification.
```

Representative source/prefix:

```text
Source document:
Two queues share a server of capacity12 jobs/s. StreamA arrival4/s earns value3/job, streamB arrival6/s earns1/job. Service times exponential; a completed job is useful only if sojourn is under.5s. Compare FCFS, nonpreemptive priority and a capacity partition. Derive what can be established analytically and formulate a simulation with reproducible confidence estimates for the rest. Include stability, tail probabilities, conservation checks and a clear distinction between exact formulas and approximations.

Task:
Solve this complete applied problem with derivations, implementation detail and verification.
```


## task-structured-1

1 payloads; saved token lengths [201]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/4ce4e3eb2ba6445fc4e475429521af1ec667854ec9a51131b84b6080ebccdaa7.json).

Actual instruction:

```text

Write an exhibit plan and a structured catalog schema. Include visitor-facing prose, evidence uncertainty, permissions workflow, budget, staffing, milestones and examples of completed catalog records.
```

Representative source/prefix:

```text
Source document:
A municipal museum received360 oral-history interviews from1900–1970. Consent permits public excerpts for240, research-only use for85, and no further use for35. Fifteen interviews concern a flood; residents disagree on chronology. The exhibit lasts12weeks, has six panels and a listening station. Staff: curator.5FTE, archivist.2FTE, two volunteers. Budget18000. Accessibility requires transcripts, captions and plain-language summaries. No living person should be identified without recorded permission.

Task:
Write an exhibit plan and a structured catalog schema. Include visitor-facing prose, evidence uncertainty, permissions workflow, budget, staffing, milestones and examples of completed catalog records.
```


## task-structured-2

1 payloads; saved token lengths [199]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/630b8b9a3128139df737fb04f7cca8fc89f6de6c6297269f88a330cafed4b589.json).

Actual instruction:

```text

Produce a factual public update, detailed internal postmortem and JSON action register. Separate facts, hypotheses and unknowns; preserve chronology and avoid unsupported assurances. Include accountable actions and verification criteria.
```

Representative source/prefix:

```text
Source document:
At07:10 a pump tripped. Pressure alarms appeared07:17. Operator restart07:22 failed; a bypass opened07:38 and restored part of town08:05. Full pressure returned10:40 after replacing a contactor. Residents reported brown water until14:00. Last inspection was24days earlier; logs show two unexplained trips. No contamination test result is yet available. Three schools opened late. Dispatch messages incorrectly stated a burst pipe.

Task:
Produce a factual public update, detailed internal postmortem and JSON action register. Separate facts, hypotheses and unknowns; preserve chronology and avoid unsupported assurances. Include accountable actions and verification criteria.
```


## task-structured-3

1 payloads; saved token lengths [191]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/8dfa60ad9f9a829eb135b1c9da42d53ff5990195875834e9c51df06938414303.json).

Actual instruction:

```text

Develop a realistic prioritization and delivery plan, explain tradeoffs, calculate capacity, design a metadata template and write a grant-progress narrative. Include explicit uncertainties and a machine-readable staged backlog.
```

Representative source/prefix:

```text
Source document:
Library has12000 newspaper pages,900 photographs and300 handwritten letters. OCR sample error rates: newspapers4%, letters18%. Photos include unidentified people. Two scanners process90pages/hour and150photos/hour. Available operator time240hours. Metadata review averages2minutes/item; rights review required on20% of objects. Grant deadline10weeks, budget12000, user priority local newspapers. Originals cannot leave the building.

Task:
Develop a realistic prioritization and delivery plan, explain tradeoffs, calculate capacity, design a metadata template and write a grant-progress narrative. Include explicit uncertainties and a machine-readable staged backlog.
```


## task-structured-4

1 payloads; saved token lengths [172]. Full [payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/provenance/historical-payloads/43e214045e1507086345463fe410eea599251c2d994153d2462637706b9c5721.json).

Actual instruction:

```text

Draft an inclusive operating agreement, a balanced budget proposal, conflict-resolution process and structured registration form. Provide concrete clauses and worked examples, including accessibility alternatives and fair waitlist handling.
```

Representative source/prefix:

```text
Source document:
Forty households share30plots; ten households are waitlisted. Irrigation costs900/year, tool insurance250/year, compost500/year. Plot fee currently35/year. Six volunteers maintain common paths. Some residents cannot perform physical work. Complaints concern shade, unattended produce and chemical sprays. Lease renews annually and bans permanent structures. The council asks for transparent allocation and accessible volunteering.

Task:
Draft an inclusive operating agreement, a balanced budget proposal, conflict-resolution process and structured registration form. Provide concrete clauses and worked examples, including accessibility alternatives and fair waitlist handling.
```

# Frozen Phase 0 core prompts

All are offline single requests, with no tool execution. The exact source/excerpt and full payload are linked; short inputs remain short.

## code-heg

code/agent / repository review; source group heg-storage; split development; configured limit 131072, actual input 22883 tokens.

Actual instruction:

```text
Review the supplied storage design and implementation. Identify transactional invariants, cancellation/retry and crash risks. Prioritize concrete corrections with small code examples and tests. Ground each finding in the supplied files and distinguish hypotheses.
```

Representative source:

```text

===== SOURCE code-000-README.md =====
# Structural Graph Conjecture Lab

Structural Graph Conjecture Lab (`sglab`) is a Linux research system for
reproducible searches for finite counterexamples to structural graph
conjectures. Its implemented research target is the Erdős–Gyárfás conjecture:

> Every finite simple graph with minimum degree at least 3 contains a simple
> cycle whose length is a power of two.

The project is an engineering and experimentation system. It does not claim
that the conjecture has been resolved.

## What the system does

- runs bounded graph-search lanes with deterministic checkpoints;
- uses an AI Research Director to choose reviewed search actions;
- keeps the Director stateless and supplies a bounded scientific
```

Length method: Natural full selected document/source set; no padding or repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/code-heg.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/code-heg-source.txt).

## math-rational

math/research / exact arithmetic; source group E026-numerical; split development; configured limit 32768, actual input 10943 tokens.

Actual instruction:

```text
Using the supplied exact rational implementation, derive and implement polynomial interpolation for points (0,1),(1,3),(2,7),(3,13). Verify exact coefficients in two independent formulations. Explain repeated-node failures, conditioning and property tests.
```

Representative source:

```text
# Originally contributed by Sjoerd Mullender.
# Significantly modified by Jeffrey Yasskin <jyasskin at gmail.com>.

"""Fraction, infinite-precision, rational numbers."""

import functools
import math
import numbers
import operator
import re
import sys

__all__ = ['Fraction']


# Constants related to the hash implementation;  hash(x) is based
# on the reduction of x modulo the prime _PyHASH_MODULUS.
_PyHASH_MODULUS = sys.hash_info.modulus
# Value to be used for rationals that reduce to infinity modulo
# _PyHASH_MODULUS.
_PyHASH_INF = sys.hash_info.inf

@functools.lru_cache(maxsize = 1 << 14)
def _hash_algorithm(numerator, denominator):

    # To make sure that the hash of a Fraction agrees with the hash
    # of a numerically equal integer, 
```

Length method: Natural full selected document/source set; no padding or repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/math-rational.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/math-rational-source.txt).

## text-http

text/translation / document summarization; source group E026-HTTP-standards; split development; configured limit 32768, actual input 20938 tokens.

Actual instruction:

```text
Summarize this HTTP caching standard for an engineer designing a caching proxy. Explain freshness, validation, invalidation and authenticated requests, and distinguish normative requirements from implementation advice. Use concrete message examples.
```

Representative source:

```text
﻿



Internet Engineering Task Force (IETF)                  R. Fielding, Ed.
Request for Comments: 9111                                         Adobe
STD: 98                                               M. Nottingham, Ed.
Obsoletes: 7234                                                   Fastly
Category: Standards Track                                J. Reschke, Ed.
ISSN: 2070-1721                                               greenbytes
                                                               June 2022


                              HTTP Caching

Abstract

   The Hypertext Transfer Protocol (HTTP) is a stateless application-
   level protocol for distributed, collaborative, hypertext information
   systems.  This document defines H
```

Length method: Natural full selected document/source set; no padding or repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/text-http.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/text-http-source.txt).

## mixed-build

structured/mixed / real build log analysis; source group strata-release-build-log; split development; configured limit 32768, actual input 10934 tokens.

Actual instruction:

```text
Analyze this actual CUDA/C++ build log. Produce a concise diagnosis, then a JSON inventory of targets, warnings, compilation units and completion evidence. Separate observed facts from unverified causes. Do not invent failed commands.
```

Representative source:

```text

/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/upstream-921-spin-validation-20261006T131023Z/source/src/kernels/cuda/verify_kernels.cu(1070): warning #177-D: function "strata::kernels::<unnamed>::resident_plan_par_kernel" was declared but never referenced
            void resident_plan_par_kernel(const int32_t* __restrict__ ids, int n, int k, const int32_t* __restrict__ res,
                 ^

[ 58%] Building CXX object CMakeFiles/strata_kernels.dir/src/kernels/ngram.cpp.o
/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/upstream-921-spin-validation-20261006T131023Z/source/src/kernels/cuda/iq_kernels.cu(2314): warning #20199-D: unrecognized #pragma in device code
  #pragma clang fp contract(off)
          ^

Remark: 
```

Length method: Natural full selected document/source set; no padding or repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/mixed-build.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/mixed-build-source.txt).

## code-queue

code/agent / implementation reasoning; source group cpython-asyncio-queues; split calibration; configured limit 32768, actual input 2498 tokens.

Actual instruction:

```text
Design a bounded asynchronous log ingestion service around this queue implementation. Explain cancellation, backpressure, shutdown, retries, and ordering; provide a concrete Python implementation and adversarial tests.
```

Representative source:

```text
__all__ = (
    'Queue',
    'PriorityQueue',
    'LifoQueue',
    'QueueFull',
    'QueueEmpty',
    'QueueShutDown',
)

import collections
import heapq
from types import GenericAlias

from . import locks
from . import mixins


class QueueEmpty(Exception):
    """Raised when Queue.get_nowait() is called on an empty Queue."""
    pass


class QueueFull(Exception):
    """Raised when the Queue.put_nowait() method is called on a full Queue."""
    pass


class QueueShutDown(Exception):
    """Raised when putting on to or getting from a shut-down Queue."""
    pass


class Queue(mixins._LoopBoundMixin):
    """A queue, useful for coordinating producer and consumer coroutines.

    If maxsize is less than or equal to zero, the queue size is inf
```

Length method: Natural full selected document/source set; no padding or repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/code-queue.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/code-queue-source.txt).

## math-sensor

math/research / numerical parameter fitting; source group authored-sensor-problem; split calibration; configured limit 131072, actual input 179 tokens.

Actual instruction:

```text
Solve this complete applied problem with derivations, implementation detail and verification.
```

Representative source:

```text
A sensor reports y(t)=a exp(-bt)+c with Gaussian noise sigma=.03 at t=0,1,2,4,8. Observations are1.08,.86,.66,.45,.24. Derive nonlinear least-squares gradients and Hessian, perform an explicit damped Gauss-Newton calculation, give a convergent algorithm, estimate uncertainty and discuss identifiability/parameter correlation. Compare fitting log-transformed data with fitting original measurements, including the role of unknown c. Provide pseudocode and consistency checks.
```

Length method: Natural full selected document/source set; no padding or repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/math-sensor.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/math-sensor-source.txt).

## text-tls

text/translation / English to Polish technical translation; source group rfc8446-TLS; split calibration; configured limit 131072, actual input 81722 tokens.

Actual instruction:

```text
Explain the TLS 1.3 handshake and its security boundaries using this standard. Translate the principal explanation into Polish while keeping protocol names and field names in English. Use a short glossary and distinguish what the excerpt specifies from assumptions.
```

Representative source:

```text






Internet Engineering Task Force (IETF)                       E. Rescorla
Request for Comments: 8446                                       Mozilla
Obsoletes: 5077, 5246, 6961                                  August 2018
Updates: 5705, 6066
Category: Standards Track
ISSN: 2070-1721


        The Transport Layer Security (TLS) Protocol Version 1.3

Abstract

   This document specifies version 1.3 of the Transport Layer Security
   (TLS) protocol.  TLS allows client/server applications to communicate
   over the Internet in a way that is designed to prevent eavesdropping,
   tampering, and message forgery.

   This document updates RFCs 5705 and 6066, and obsoletes RFCs 5077,
   5246, and 6961.  This document also specifies new requiremen
```

Length method: Natural full selected document/source set; no padding or repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/text-tls.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/text-tls-source.txt).

## mixed-fields

structured/mixed / grammar and schema extraction; source group rfc8941-structured-fields; split calibration; configured limit 131072, actual input 16346 tokens.

Actual instruction:

```text
Extract the structured-field data model and parser constraints from this standard. Provide a typed schema, parsing pseudocode and a compact JSON test catalog for dictionaries, lists, items and parameters, with examples drawn from the document. Distinguish illustrative tests from complete conformance coverage.
```

Representative source:

```text
﻿



Internet Engineering Task Force (IETF)                     M. Nottingham
Request for Comments: 8941                                        Fastly
Category: Standards Track                                      P-H. Kamp
ISSN: 2070-1721                                The Varnish Cache Project
                                                           February 2021


                    Structured Field Values for HTTP

Abstract

   This document describes a set of data types and associated algorithms
   that are intended to make it easier and safer to define and handle
   HTTP header and trailer fields, known as "Structured Fields",
   "Structured Headers", or "Structured Trailers".  It is intended for
   use by specifications of new HTT
```

Length method: Natural full selected document/source set; no padding or repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/mixed-fields.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/mixed-fields-source.txt).

## code-archive

code/agent / safe archive import; source group cpython-zipfile; split reserved_evaluation; configured limit 32768, actual input 6983 tokens.

Actual instruction:

```text
Implement a safe offline archive importer using this implementation as reference. Discuss path normalization, links, size limits, streaming, atomic publication and interrupted extraction. Include Python code and tests.
```

Representative source:

```text
"""
Read and write ZIP files.

XXX references to utf-8 need further investigation.
"""
import binascii
import importlib.util
import io
import os
import shutil
import stat
import struct
import sys
import threading
import time

try:
    import zlib # We may need its compression method
    crc32 = zlib.crc32
except ImportError:
    zlib = None
    crc32 = binascii.crc32

try:
    import bz2 # We may need its compression method
except ImportError:
    bz2 = None

try:
    import lzma # We may need its compression method
except ImportError:
    lzma = None

try:
    from compression import zstd # We may need its compression method
except ImportError:
    zstd = None

__all__ = ["BadZipFile", "BadZipfile", "error",
           "ZIP_STORED", "ZIP_D
```

Length method: Coherent complete-paragraph prefix of historical zipfile excerpt; original26000-character source ends mid-comment and remains preserved. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/code-archive.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/code-archive-source.txt).

## math-inventory

math/research / stochastic inventory; source group authored-warehouse-problem; split reserved_evaluation; configured limit 32768, actual input 165 tokens.

Actual instruction:

```text
Solve this complete applied problem with derivations, implementation detail and verification.
```

Representative source:

```text
A warehouse replenishes one item every seven days. Daily demand is independent Poisson with mean18, supplier lead time is three days, fixed order cost120 and unit holding cost.04/day. Derive a periodic-review base-stock policy at99% cycle-service probability, distinguish cycle service from fill rate, estimate shortage expectation without normal-tail shortcuts, and compare with a continuous-review policy. Show numerical calculations, exact sums and assumptions; discuss how correlated demand invalidates the result.
```

Length method: Natural full selected document/source set; no padding or repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/math-inventory.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/math-inventory-source.txt).

## text-websocket

text/translation / technical explanation; source group rfc6455-WebSocket; split reserved_evaluation; configured limit 32768, actual input 30383 tokens.

Actual instruction:

```text
Explain the WebSocket upgrade and framing protocol from the supplied coherent excerpt. Contrast HTTP request semantics with persistent full-duplex messaging; discuss validation, masking and failure handling. State when a detail is outside the supplied excerpt.
```

Representative source:

```text






Internet Engineering Task Force (IETF)                          I. Fette
Request for Comments: 6455                                  Google, Inc.
Category: Standards Track                                    A. Melnikov
ISSN: 2070-1721                                               Isode Ltd.
                                                           December 2011


                         The WebSocket Protocol

Abstract

   The WebSocket Protocol enables two-way communication between a client
   running untrusted code in a controlled environment to a remote host
   that has opted-in to communications from that code.  The security
   model used for this is the origin-based security model commonly used
   by web browsers.  The protocol
```

Length method: Coherent complete-paragraph prefix for admission; full original source preserved; no padding/repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/text-websocket.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/text-websocket-source.txt).

## mixed-chinook

structured/mixed / real SQL schema extraction; source group chinook-SQLite-DDL; split reserved_evaluation; configured limit 32768, actual input 1899 tokens.

Actual instruction:

```text
Extract an entity-relationship model from this real SQLite schema. Return a JSON catalog of tables, primary/foreign keys and constraints, then explain invoice and playlist joins, deletion risks and integrity checks. Do not assume facts from absent sample rows.
```

Representative source:

```text

/*******************************************************************************
   Chinook Database - Version 1.4.5
   Script: Chinook_Sqlite.sql
   Description: Creates and populates the Chinook database.
   DB Server: Sqlite
   Author: Luis Rocha
   License: https://github.com/lerocha/chinook-database/blob/master/LICENSE.md
********************************************************************************/

/*******************************************************************************
  WARNING: This file was generated by a tool and changes to this file
           will be lost when this file is regenerated.
********************************************************************************/

/***********************************************
```

Length method: Natural full selected document/source set; no padding or repetition. [Complete payload](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/mixed-chinook.json); [source snapshot](/srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/golden-swap-phase0-20261006T185015Z/corpus/mixed-chinook-source.txt).
