import asyncio
from twikit import Client, TooManyRequests
from datetime import datetime
from random import randint
import csv
from configparser import ConfigParser

MINIMUM_TWEETS = 10
QUERY = 'Amino'

#* Initialize client and login
async def login_and_save_cookies():
    # Load config
    config = ConfigParser()
    config.read('config.ini')

    username = config['X']['username']
    email = config['X']['email']
    password = config['X']['password']

    # Initialize client
    client = Client(language='en-US')

    # Login
    await client.login(
        auth_info_1=username,
        auth_info_2=email,
        password=password
    )

    # Save cookies
    client.save_cookies('cookies.json')
    print("✅ Logged in and saved cookies!")

# Run the async function
asyncio.run(login_and_save_cookies())


async def get_tweets(tweets):
    client = Client(language='en-US')
    #client.load_cookies('cookies.json')  # Use saved cookies
    if tweets is None:
        print(f'{datetime.now()} - Getting tweets...')
        tweets = await client.search_tweet(QUERY, product='Top')
    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
        await asyncio.sleep(wait_time)
        tweets = await tweets.next()

    return tweets


async def main():
    tweet_count = 0
    tweets = None

    # Create CSV file and write header
    with open('tweets.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes'])

    while tweet_count < MINIMUM_TWEETS:
        try:
            tweets = await get_tweets(tweets)  # ✅ Await the coroutine
        except TooManyRequests as e:
            rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
            print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
            wait_time = (rate_limit_reset - datetime.now()).total_seconds()
            await asyncio.sleep(wait_time)  # ✅ Async sleep
            continue
        except Exception as e:
            print(f'{datetime.now()} - Error: {e}')
            break

        if not tweets:
            print(f'{datetime.now()} - No more tweets found')
            break

        for tweet in tweets:
            tweet_count += 1
            tweet_data = [
                tweet_count,
                tweet.user.name,
                tweet.text,
                tweet.created_at,
                tweet.retweet_count,
                tweet.favorite_count
            ]

            with open('tweets.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(tweet_data)

            print(f'{datetime.now()} - Got {tweet_count} tweets')

            if tweet_count >= MINIMUM_TWEETS:
                break

    print(f'{datetime.now()} - Done! Got {tweet_count} tweets')


# Run the async main function
asyncio.run(main())