import requests
from twilio.rest import Client
import html
import os

TIME_SERIES_DAILY_ADJUSTED = "TIME_SERIES_DAILY_ADJUSTED"
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
INTERVAL = "24hour, 24hour"

STOCK_API_KEY = os.environ.get("stock_api_key")
NEWS_API_KEY = os.environ.get("news_api_key")
TWILIO_SID = os.environ.get("twilio_sid")
AUTH_TOKEN = os.environ.get("auth_token")
FROM_NUM = os.environ.get("from_num")
TO_NUM = os.environ.get("to_num")

INTRADAY = "https://www.alphavantage.co/query"
DAILY_ADJUSTED = "https://www.alphavantage.co/query"

stock_parameters = {
    "function": TIME_SERIES_DAILY_ADJUSTED,
    "symbol": STOCK,
    "interval": INTERVAL,
    "apikey": STOCK_API_KEY,
}

""" Getting values of thee stock and extracting closing data of yesterday and day before yesterday """
response = requests.get(url=INTRADAY, params=stock_parameters)
response.raise_for_status()
stock_data_json = response.json()

yesterday_day_before_yesterday = (list(stock_data_json["Time Series (Daily)"]))[0:2]
yesterday_data = float((stock_data_json["Time Series (Daily)"][yesterday_day_before_yesterday[0]]["4. close"]))
day_b_y_data = float((stock_data_json["Time Series (Daily)"][yesterday_day_before_yesterday[1]]["4. close"]))

""" Calculating difference between the yesterday closing and day before yesterday """
difference = yesterday_data - day_b_y_data

""" Change in percentage """
change_percentage = round((difference / yesterday_data) * 100, 2)

percentage_values = "🔺", "🔻"
percentage: str
message_send = False

if difference > 0:
    message_send = True
    percentage = percentage_values[0]

elif difference < 0:
    message_send = True
    percentage = percentage_values[1]

""" Getting news of the company """

if message_send:
    news_parameter = {
        "q": COMPANY_NAME,
        "language": "en",
        "apiKey": NEWS_API_KEY,
    }
    news_response = requests.get(url="https://newsapi.org/v2/everything", params=news_parameter)
    news_response.raise_for_status()
    new_data = (news_response.json())

    top_3_news = ((new_data["articles"])[0:3])
    news: str

    news_for_stock = ""
    title_for_stock = ""
    """ Sending message to the client """
    for i in range(3):
        news = f'{top_3_news[i]["description"]}\n'
        news_for_stock += news

        news = f'{top_3_news[i]["title"]}\n'
        title_for_stock += news

    news_list = (news_for_stock.split("\n"))
    title_list = (title_for_stock.split("\n"))

    for i in range(3):
        client = Client(TWILIO_SID, AUTH_TOKEN)
        message = client.messages.create(
            from_=FROM_NUM,
            body=f'{STOCK}:{percentage}{change_percentage}%\nContent: {html.unescape(title_list[i])}'
                 f'\nDescription: {html.unescape(news_list[i])}',
            to=TO_NUM,
        )
        print(message.sid)


