# Base Imports
import datetime
import os
import redis
from celery import Celery
import json
import plotly
from functools import reduce
import pandas as pd
port = int(os.environ.get('PORT', 6379))
import colorama
import requests
from bs4 import BeautifulSoup
# Custom Imports
from async_pull import date_to_today_list, date_to_today



# Run Heroku
ON_HEROKU = os.environ.get('ON_HEROKU')
os.environ.get('ON_HEROKU')

if ON_HEROKU:
    # get the heroku port
    port = int(os.environ.get('PORT', 17995))  # as per OP comments default is 17995


redis_url = os.getenv('REDIS_URL', f'redis://localhost:{port}')

celery_app = Celery("Celery App", broker=redis_url)

redis_instance = redis.StrictRedis.from_url(redis_url)

REDIS_HASH_NAME = os.environ.get("DASH_APP_NAME", "app-data")
REDIS_KEYS = {"DATASET": 'DATASET', "DATE_UPDATED": "DATE_UPDATED"}


@celery_app.on_after_configure.connect
def start_celery(**kwargs):
    c_listout_dataframe_to_date()
    c_dataframe_to_date()
    c_scrape_google_task()

"""Start / Management"""
@celery_app.task
def c_dataframe_to_date(date='2020-03-20'):
        df_list = date_to_today.main(date)

        redis_instance.set(
            'c_date_to_today',
            json.dumps(
                df_list.to_dict(),
                # This JSON Encoder will handle things like numpy arrays
                # and datetimes
                cls=plotly.utils.PlotlyJSONEncoder,
            ),
        )
        # Save the timestamp that the dataframe was updated
        redis_instance.hset(
        REDIS_HASH_NAME, REDIS_KEYS["DATASET"], f'{str(datetime.datetime.now())}')

@celery_app.on_after_configure.connect
def snapshot_table_task(sender, **kwargs):
    print("----> setup_periodic_tasks")
    sender.add_periodic_task(
        45,  # seconds
        # an alternative to the @app.task decorator:
        # wrap the function in the app.task function
        c_dataframe_to_date.s(),
        name="date_to_today",
    )




@celery_app.task
def c_dataframe(date='2020-03-20', ):
        df_list = date_to_today.main(date, )

        redis_instance.set(
            'table_data',
            json.dumps(
                df_list.to_dict(),
                # This JSON Encoder will handle things like numpy arrays
                # and datetimes
                cls=plotly.utils.PlotlyJSONEncoder,
            ),
        )
        # Save the timestamp that the dataframe was updated
        redis_instance.hset(
        REDIS_HASH_NAME, REDIS_KEYS["DATASET"], f'{str(datetime.datetime.now())}')


@celery_app.task
def c_listout_dataframe_to_date(usa_only=False, scale=1000, days=30):
    # We should connect the last expensive data querying steps needed to render the graphs with this data

    # Get Today's Date
    today = datetime.date.today()

    # Get the date 7 days ago
    days_ago = today - datetime.timedelta(days=days)

    # Create Variable = Async Data Fetch requesting date
    df_list = date_to_today_list.main(date=str(days_ago), value=scale, usa_only=usa_only)
    # returns a list [df1, df2, ... df7]


    # loop through the list
    for df in df_list:

        print(f'Building Redis Storage on: {df["lastUpdate"][0]}-dataframe')

        # Creates a redis instence to store data, turns df to dictionary & encodes in json
        redis_instance.set(
            f'{df["lastUpdate"][0]}-dataframe',
            json.dumps(
                df.to_dict(),
                # This JSON Encoder will handle things like numpy arrays
                # and datetimes
                cls=plotly.utils.PlotlyJSONEncoder,
            ),
        )

@celery_app.on_after_configure.connect
def dataframe_to_date_task(sender, **kwargs):
    print("----> setup_periodic_tasks")
    sender.add_periodic_task(
        45,  # seconds
        # an alternative to the @app.task decorator:
        # wrap the function in the app.task function
        c_listout_dataframe_to_date.s(),
        name="dataframe_to_date",
    )



@celery_app.task
def c_scrape_google_task():
    # We should connect the last expensive data querying steps needed to render the graphs with this data
    source = requests.get('https://developers.google.com/public-data/docs/canonical/countries_csv')
    soup = BeautifulSoup(source.text, 'html.parser')

    data = []
    for tr in soup.find_all('tr'):
        values = [td.text for td in tr.find_all('td')]
        data.append(values)

    countries = pd.DataFrame(data[1::])

    countries.rename(columns={0: 'country', 1: 'latitude', 2: 'longitude', 3: 'name'}, inplace=True)

    redis_instance.set(
        f'country-basic-geo-dataframe',
        json.dumps(
            countries.to_dict(),
            # This JSON Encoder will handle things like numpy arrays
            # and datetimes
            cls=plotly.utils.PlotlyJSONEncoder,
        ),
    )

@celery_app.on_after_configure.connect
def dataframe_scrape_google_task(sender, **kwargs):
    print("----> setup_periodic_tasks")
    sender.add_periodic_task(
        45,  # seconds
        # an alternative to the @app.task decorator:
        # wrap the function in the app.task function
        c_listout_dataframe_to_date.s(),
        name="country-basic-geo-dataframe",
    )


if __name__ == "__main__":
    def get_basic_country_geo():
        jsonified_df = redis_instance.get(
            'country-basic-geo-dataframe'
        ).decode("utf-8")
        df = pd.DataFrame(json.loads(jsonified_df))
        return df

    def get_dropdown_options():
        options = []
        df = get_basic_country_geo()
        df=df.to_dict()
        for x, y in zip(df['country'], df['name']):
            options.append({'country_code': df['country'][x], 'country': df['name'][y]})

        return options