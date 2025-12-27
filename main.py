import requests
import os
import logging
import sqlite3
import time
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(level=logging.DEBUG)

def init_db():
    conn = sqlite3.connect('cooley.db') 
    cursor = conn.cursor()  
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users_data (
        slack_id TEXT PRIMARY KEY,
        api_key TEXT
    )
''') 
    conn.commit()  
    conn.close()

init_db()

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')

app = App(token=SLACK_BOT_TOKEN)


@app.message("hi")
def hello(ack, body, say, logger):
    ack()
    logger.debug(body)
    say("hello im a rac! (rac means raccoon btw) (Ts a placeholder)")


@app.command("/config-api-key")
def set_api_key(logger, respond, ack, command, body):
    ack()
    slack_id = command["user_id"]
    api_key = command.get("text", "").strip()
    
    logger.debug(body)


    if not api_key:
        respond("please provide an api key! you can get an api key at https://mail.hackclub.com/my/api_keys")
        return
    
    try:
        response = requests.get(
            "https://mail.hackclub.com/api/public/v1/me",
            headers={'Authorization': f'Bearer {api_key}'}
        )

        if response.status_code != 200:
            respond("mail request failed due to auth error! are you sure you are using the right key?")
            return

    except Exception as e:
        respond("unable to make a request to the mail service!")
        return
    try:
        conn = sqlite3.connect('cooley.db')
        cursor = conn.cursor()
        cursor.execute('REPLACE INTO users_data (slack_id, api_key) VALUES (?, ?)', (slack_id, api_key))
        conn.commit()
        conn.close()

        respond("i have sucessfully configured your api key! you can do the rest of the commands.")
    except Exception as e:
        respond(f"i verified your key but i cannot save it to my DB! please try again soon.")


















if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()