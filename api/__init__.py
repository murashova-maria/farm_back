# LOCAL
from loader import *
from api.starter import Starter

# API
from fastapi import FastAPI, HTTPException

# OTHER
from typing import Dict, Any
from threading import Thread
from datetime import datetime

app = FastAPI()
