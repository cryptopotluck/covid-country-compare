import plotly.graph_objects as go
from async_pull import date_to_today_list, breakdown_usa_data
import colorama
import datetime
import plotly.express as px
import pandas as pd

def request_candlestick(redis_data, country):
    df_list = redis_data


    print(colorama.Fore.BLUE + f'type of country: {type(country)}')

    redis_data=breakdown_usa_data.main(df_list)

    # df = pd.concat(df_list)
    #
    # print(colorama.Fore.BLUE + f'you are working with: {df}')
    # states = df['provinceState'].to_list()
    # unique_states = list(set(states))
    #
    # finished_dataframes = []
    # for s in unique_states:
    #     print(s)
    #     print('work with:')
    #     print(df['provinceState'])
    #     usa_only = df['provinceState'].str.contains(s)
    #
    #
    #     df2 = df[usa_only]
    #     finished_dataframes.append(df2)
    #
    # data = []
    # for x in finished_dataframes:
    #
    #     print('final strech')
    #     print(x)
    #
    #     texts = []
    #     for index, row in x.iterrows():
    #         texts.append(f"{row['provinceState']}-{row['deaths']}")
    print(redis_data)


    data=[]
    deaths_list =[]
    confirmed_list=[]
    recovered_list=[]
    c_r_dif = []
    location=[]
    for x in redis_data:

        print('bad ass?')
        loc=pd.DataFrame(x['provinceState'])
        print(type(loc))
        print(loc.iloc[0][0])
        loc = loc.iloc[0]
        location.append(loc['provinceState'])


        deaths = 0
        confirmed = 0
        recovered = 0

        for d in x['deaths']:
            deaths = deaths + int(d)

        for c in x['confirmed']:
            confirmed = confirmed + int(c)

        for r in x['recovered']:
            recovered = recovered + int(r)

        c_r_d = confirmed - recovered



        deaths_list.append(deaths)
        confirmed_list.append(confirmed)
        recovered_list.append(recovered)
        c_r_dif.append(c_r_d)

    try:
        print('locations')
        print(location)
        data.append(go.Scatter3d(
                x=c_r_dif,
                y=deaths_list,
                z=recovered_list,
                mode='markers',
                customdata=location,
                hovertemplate=
                "<b>confirmed: %{x}</b><br><br>" +
                "<b>Deaths: %{y}</b><br><br>" +
                "Location: %{customdata}<br>" +
                "<extra></extra>",
                marker=dict(
                    size=12,
                    color=deaths_list,  # set color to an array/list of desired values
                    colorscale='Viridis',  # choose a colorscale
                    opacity=0.8
                )
        ))

    except:
        pass






        # frames.append(go.Line(name=f' Deaths',
        #                                         text=c_d_rate,
        #                                         hovertemplate=
        #                                         "Death Rate: %{text}<br>" +
        #                                         "<extra></extra>",
        #                                         x=dates,
        #                                         y=deaths,
        #                                         marker=dict(
        #                                             size=deaths,
        #                                             color='salmon',
        #                                         ),
        #                                         ))
        # frames.append(go.Line(name=f' Recovered',
        #                                         text=recovered,
        #                                         hovertemplate=
        #                                         "Recovered: %{text}<br>" +
        #                                         "<extra></extra>",
        #                                         x=dates,
        #                                         y=recovered,
        #                                         marker=dict(
        #                                             size=recovered,
        #                                             color='green',
        #                                         ),
        #                                         ))


    # else:
    #     data = []
    #     for df in df_list:
    #
    #         close = []
    #         for c, d in zip(df['confirmed'], df['deaths']):
    #             close.append(float(c[0])/float(d[0]))
    #
    #         data.append(go.Line(name='Confirmed',
    #                             text=df['confirmed'],
    #                             hovertemplate=
    #                             "Confirmed #: %{text}<br>" +
    #                             "<extra></extra>",
    #                             x=df['lastUpdate'],
    #                             y=df['confirmed'],
    #                             marker=dict(
    #                                 size=df['confirmed_size'][0],
    #                                 color='yellow',
    #                             ),
    #                             ))
    #         data.append(go.Line(name='Deaths',
    #                             text=close,
    #                             hovertemplate=
    #                             "Death Rate: %{text}<br>" +
    #                             "<extra></extra>",
    #                             x=df['lastUpdate'],
    #                             y=df['deaths'],
    #                             marker=dict(
    #                                 size=df['death_size'][0],
    #                                 color='salmon',
    #                             ),
    #                             ))
    #         data.append(go.Line(name='Recovered',
    #                             text=df['recovered'],
    #                             hovertemplate=
    #                             "Recovered: %{text}<br>" +
    #                             "<extra></extra>",
    #                             x=df['lastUpdate'],
    #                             y=df['recovered'],
    #                             marker=dict(
    #                                 size=df['recovered_size'][0],
    #                                 color='green',
    #                             ),
    #                             ))

    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        )
    )

    fig = go.Figure(data=data, layout=layout)

    return fig


if __name__ == '__main__':

    def get_home_map_animation(country):
        df_list = date_to_today_list.main(date='2020-08-24', usa_only=True)

        finished_redis_fetch = []
        for df in df_list:
            if country == 'United States':
                country = 'US'
                df2 = df['countryRegion'].str.contains(country)
                print('fuckhead')
                print(df[df2])
                finished_redis_fetch.append(df[df2])
            else:
                df2 = df['countryRegion'].str.contains(country)
                finished_redis_fetch.append(df[df2])

        print('This is the DF to Focus on')
        print(finished_redis_fetch)

        return finished_redis_fetch

    request_candlestick(get_home_map_animation('US'), country='US').show()

    print('finished?')

