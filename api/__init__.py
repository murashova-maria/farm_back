# LOCAL
from loader import *
from api.starter import Starter

# API
import aiofiles
from typing import Optional, Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, File, UploadFile, Form

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
