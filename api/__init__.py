# LOCAL
from api.starter import *

# API
import aiofiles
from typing import Optional, Annotated
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# OTHER
import base64
import multipart
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
