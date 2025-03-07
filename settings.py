from datetime import *
import os
import pandas as pd
import sys
from pathlib import Path
import numpy as np

from arch import arch_model
from scipy.stats import norm
import math
import holidays
from colorama import Fore, Style, init

from dataclasses import dataclass
from pretty_html_table import build_table
import win32com.client
from matplotlib import pyplot as plt
from pandas.tseries.offsets import *
import re
import logging

VAR_LIMIT = 1250000
BASE_PATH = Path(__file__).resolve().parent.parent
PATH_MODELS = BASE_PATH.parent
PATH_BRKNL = PATH_MODELS.parent

DT_INI = '28/02/2025' #base date for exercise
DT_INI_DTIME = pd.to_datetime(DT_INI, dayfirst=True)
DT_STR = pd.to_datetime(DT_INI, dayfirst=True).strftime("%Y-%m-%d")
DT_ARQ = DT_INI_DTIME.strftime("%Y%m%d")

