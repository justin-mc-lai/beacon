#!/usr/bin/env python3
"""Beacon CLI - Entry point for ptk compatibility"""
import sys
import os

# Add beacon to path
beacon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, beacon_path)

from beacon.main import app

if __name__ == "__main__":
    app()
