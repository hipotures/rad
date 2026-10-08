#!/usr/bin/env python3
"""Freeze public interval, joint-frame and parameter-refinement source pins.

Credits: Avi Eisenberg (#62), eumemic (#57), Alejandro Zarzuelo Urdiales
(#61), and every predecessor in the fetched NOTICE/licensing records.
Acquisition only; this helper does not certify the mathematical claims.
"""
import fetch_public_baselines as acquisition

acquisition.PINS = {
    62: 'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
    57: 'cd350f76c9bc01489ec83568bded532cb69be938',
    61: 'afb7cb67d1858641315cfbf4ac768ee64a8eff3a',
}

if __name__ == '__main__':
    acquisition.main()
