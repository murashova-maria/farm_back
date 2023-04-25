# LOCAL
from api import *


@app.post('/bots/{user_id}/schedules/')
async def bots_schedule(user_id: str, day: str, time_range: str, action: str):
    try:
        data = [user_id, action, day, time_range]
        main_queue.put(QueuedTask(ScheduleDB, 'create_schedule', data))
        return {'Status': "OK"}
    except Exception:
        raise HTTPException(status_code=400, detail=[])


@app.get('/bots/{user_id}/schedules/')
async def bots_schedule(user_id: str):
    try:
        schedules = ScheduleDB.filter_schedules(user_id=user_id)
        full_schedule = [["" for y in range(11)] for x in range(7)]
        for schedule in schedules:
            day = schedule['day']
            time_range = schedule['time_range']
            full_schedule[int(day)][int(time_range)] = schedule['action']
        return full_schedule
    except Exception:
        raise HTTPException(status_code=400, detail=[])
