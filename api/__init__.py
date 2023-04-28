# LOCAL
from loader import *
from api.starter import Starter

# API
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# OTHER
from threading import Thread
from datetime import datetime
from typing import Dict, Any, List

app = FastAPI()
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
