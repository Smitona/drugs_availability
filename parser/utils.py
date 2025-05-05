
async def parse_schedule(schedule_string):
    schedule_dict = {}
    parts = schedule_string.split()

    for i in range(0, len(parts), 2):
        if i + 1 < len(parts):
            day = parts[i].strip(':')
            time_range = parts[i + 1]
            schedule_dict[day] = time_range

    return schedule_dict
