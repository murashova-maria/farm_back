from api import *


@app.post('/conversation/create/')
async def create_conversation():
    pass


@app.put('/conversation/{conversation_id}/')
async def add_user_to_conversation():
    pass


@app.put('/conversation/{conversation_id}/{user_id}/')
async def add_message_to_user():
    pass
