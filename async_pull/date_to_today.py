import asyncio
import datetime
from asyncio import AbstractEventLoop
import aiohttp
import colorama
import socket
import requests

from pandas import DataFrame as df
import pandas as pd
import dash_bootstrap_components as dbc
import dash_html_components as html
import urllib.request
import platform
import os
import ssl
import certifi
import time

date=str(datetime.date.today()-datetime.timedelta(days=1))

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

print(f'holly date {date}')

def main(selected_date, country_filter=None):
    # Create the asyncio Loop
    loop: AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    t0 = datetime.datetime.now()
    print(colorama.Fore.LIGHTGREEN_EX + 'App started', flush=True)
    result = loop.run_until_complete(get_covid_data(loop, dates=[date, selected_date], country_filter=country_filter))
    dt = datetime.datetime.now() - t0
    print(colorama.Fore.LIGHTGREEN_EX + "App exiting, total time: {:,.2f} sec.".format(dt.total_seconds()), flush=True)
    return result


async def get_covid_data(loop: AbstractEventLoop, dates: list, country_filter):
    tasks = []

    for d in dates:
        tasks.append((loop.create_task(get_api(date=d))))

    print(f'tasks = {tasks}')
    finished = []
    for task in tasks:
        api = await task

        data = pd.DataFrame(api)
        finished_fetch = await clean_data(data, country_filter)
        finished.append(finished_fetch)

    return finished[0]

async def get_api(date: str) -> str:

    url = f'https://covid19.mathdro.id/api/daily/{date}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=ssl_context) as resp:
            resp.raise_for_status()

            api = await resp.json()
            return api

async def clean_data(c_data, country_filter):
    if country_filter == 'United States':
        return c_data['countryRegion'].str.contains('US')
    else:
        try:
            df2 = c_data['countryRegion'].str.contains(country_filter)
            return c_data[df2]
        except:
            return c_data




if __name__ == '__main__':
    choices = []
    for x in main(selected_date='2020-03-20').head():
       choices.append(x)
    print(colorama.Fore.CYAN + f'You can filter df by {choices}')
    print()
    print(main(selected_date='2020-03-20')['countryRegion'])