"""Smoke tests verifying overall system imports, exports, and core functionality."""

from __future__ import annotations

import matplotlib
import numpy as np
import pandas as pd
import scipy
import statsmodels

import experimentguard


def test_package_smoke():
    assert experimentguard.__version__ == "0.1.0"
    assert pd.__version__ is not None
    assert np.__version__ is not None
    assert scipy.__version__ is not None
    assert statsmodels.__version__ is not None
    assert matplotlib.__version__ is not None
