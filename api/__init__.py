# LOCAL
from loader import *
from api.starter import Starter

# API
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# OTHER
from typing import Dict, Any
from threading import Thread
from datetime import datetime

app = FastAPI()
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
