import asyncio
import datetime
from asyncio import AbstractEventLoop
import aiohttp
import colorama
import pandas as pd
import ssl
import certifi
import plotly.graph_objects as go

date=str(datetime.date.today()-datetime.timedelta(days=1))

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


def main(data):
    # Create the asyncio Loop
    loop: AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    t0 = datetime.datetime.now()
    print(colorama.Fore.LIGHTGREEN_EX + 'Start Async Timer', flush=True)
    result = loop.run_until_complete(get_covid_data(loop, data))
    dt = datetime.datetime.now() - t0
    print(colorama.Fore.LIGHTGREEN_EX + '----------------------------------------------------------------------------------------------------------')

    print(colorama.Fore.LIGHTGREEN_EX + "fetch_country.py - Finished Async Execution, total time: {:,.2f} sec.".format(dt.total_seconds()), flush=True)
    print('----------------------------------------------------------------------------------------------------------')
    return result


async def get_covid_data(loop: AbstractEventLoop, data):
    tasks = []

    df = pd.concat(data)

    print(colorama.Fore.BLUE + f'you are working with: {df}')
    states = df['provinceState'].to_list()
    unique_states = list(set(states))


    # Created a loop & Appended a loop_task that returns the value of get_api()
    for s in unique_states:
        tasks.append((loop.create_task(clean_data(data=df, state=s))))

    print(f'tasks = {tasks}')
    finished = []
    for task in tasks:
        data = await task
        final_fetch = await final_task(data)
        finished.append(final_fetch)

    print(colorama.Fore.WHITE + f"Task Finished: {finished[0]}", flush=True)
    return finished


async def final_task(finished_dataframes):

    dfs = pd.concat(finished_dataframes)


    print('focus focus')
    print(dfs)
    #
    #
    #     for index, row in x.iterrows():
    #         texts.append(f"{row['provinceState']}-{row['deaths']}")
    #
    # finished_dataframes['text'] = texts




    return dfs


async def clean_data(data, state):


    print('----|----')
    finished_dataframes = []
    for s in data:
        print(s)
        print('work with:')
        print(data['provinceState'])
        usa_only = data['provinceState'].str.contains(state)

        df = data[usa_only]
        finished_dataframes.append(df)





    # if country == 'USA':
    #     usa_only = data['countryRegion'].str.contains('US')
    #     data = data[usa_only]


    # data['confirmed_size'] = data.loc[:, 'confirmed'].apply(lambda x: int(x) / scale)
    # data['death_size'] = data.loc[:, 'deaths'].apply(lambda x: int(x) / scale)
    # data['recovered_size'] = data.loc[:, 'recovered'].apply(lambda x: int(x) / scale)

    return finished_dataframes


if __name__ == '__main__':
    start_script = main()
    print(colorama.Fore.CYAN + f"Returns: {start_script}", flush=True)





