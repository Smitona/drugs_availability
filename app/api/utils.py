from datetime import datetime as dt
import re


async def parse_schedule(schedule_string):
    schedule_dict = {}
    parts = schedule_string.split()

    for i in range(0, len(parts), 2):
        if i + 1 < len(parts):
            day = parts[i].strip(':')
            time_range = parts[i + 1]
            schedule_dict[day] = time_range

    return schedule_dict


async def prepare_drug_data(item: dict):
    full_name = item['drugName']

    match = re.search(r'^(\w+)[®, ]', full_name)

    if match:
        drug_name = match.group(1)
    else:
        drug_name = full_name.split()[0] if full_name else ""

    pharmacy_name = item['storeName']
    actuality_dt = dt.strptime(item['actualDate'], "%Y-%m-%dT%H:%M:%S")

    return drug_name, pharmacy_name, actuality_dt
