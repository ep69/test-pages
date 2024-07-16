import csv
import datetime
from pprint import pprint
from googleapiclient.discovery import build
from jinja2 import Environment, FileSystemLoader
import os

api_key = os.environ['GAPI_KEY']
calendar_id = "2bc0ae0d9e4d0d8567858f3d78b8d7e2d87d2dcc41cb430f07a0c1efbe65efc9@group.calendar.google.com"
now = datetime.datetime.now().astimezone().isoformat()
maxResults = 10

service = build("calendar", "v3", developerKey=api_key)
events_result = service.events().list(calendarId=calendar_id, timeMin=now, maxResults=maxResults, timeZone="Europe/Prague").execute()
#pprint(events_result)

events = []
for e in events_result.get("items", []):
    event = {}
    event["summary"] = e.get("summary")
    start = e.get("start", {})
    end = e.get("end", {})
    if "date" in start:
        start_s = start.get("date")
        end_s = end.get("date", None)
        if end_s is not None and end_s != start_s:
            when_s = f"{start_s} - {end_s}"
        else:
            when_s = start_s
    elif "dateTime" in start:
        start_dt = start.get("dateTime")
        assert("T" in start_dt)
        start_date, start_time = start_dt.split("T", 2)
        if "+" in start_time:
            start_time, _ = start_time.split("+", 2)
        if "Z" in start_time:
            start_time, _ = start_time.split("Z", 2)
        h, m, _ = start_time.split(":")
        start_time = f"{h}:{m}"
        start_s = f"{start_date} {start_time}"
        end_dt = end.get("dateTime", None)
        if end_dt is None:
            when_s = start_s
        else:
            assert("T" in end_dt)
            end_date, end_time = end_dt.split("T", 2)
            if "+" in end_time:
                end_time, _ = end_time.split("+", 2)
            if "Z" in end_time:
                end_time, _ = end_time.split("Z", 2)
            h, m, _ = end_time.split(":")
            end_time = f"{h}:{m}"
            if end_date == start_date:
                end_s = end_time
            else:
                end_s = f"{end_date} {end_time}"
            when_s = f"{start_s} - {end_s}"

    else:
        print("Weird date")
        assert(False)

    event["when"] = when_s

    events.append(event)
events = sorted(events, key=lambda x: x["when"])
#pprint(events)

environment = Environment(loader=FileSystemLoader("./"))
page_template = environment.get_template("template.html")
page_filename = "index.html"
context = {
    "events": events,
    "date": now,
    }
with open(page_filename, mode="w", encoding="utf-8") as page:
    page.write(page_template.render(context))
#print(page_template.render(context))
