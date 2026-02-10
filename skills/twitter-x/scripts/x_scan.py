#!/usr/bin/env python3
"""Scan an X/Twitter profile and tweets using twikit.
Usage: python3 x_scan.py <screen_name> [tweet_id]
Requires: pip install twikit
Cookies cached at /home/openclaw/.secrets/x_twikit_cookies.json
"""
import asyncio, sys, json, os
from twikit import Client

COOKIES_PATH = '/home/openclaw/.secrets/x_twikit_cookies.json'
CREDS = json.load(open('/home/openclaw/.secrets/twitter.json'))

async def main():
    screen_name = sys.argv[1] if len(sys.argv) > 1 else None
    tweet_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    client = Client('en-US')
    
    # Try loading cookies first
    if os.path.exists(COOKIES_PATH):
        try:
            client.load_cookies(COOKIES_PATH)
            print("Loaded cached cookies")
        except:
            await client.login(
                auth_info_1=CREDS['email'],
                auth_info_2=CREDS['username'],
                password=CREDS['password']
            )
            client.save_cookies(COOKIES_PATH)
    else:
        await client.login(
            auth_info_1=CREDS['email'],
            auth_info_2=CREDS['username'],
            password=CREDS['password']
        )
        client.save_cookies(COOKIES_PATH)
    
    if tweet_id:
        tweet = await client.get_tweet_by_id(tweet_id)
        print(f"\n=== TWEET ===")
        print(f"Author: {tweet.user.name} (@{tweet.user.screen_name})")
        print(f"Text: {tweet.full_text}")
        print(f"Date: {tweet.created_at}")
        print(f"Likes: {tweet.favorite_count} | RTs: {tweet.retweet_count} | Views: {tweet.view_count}")
    
    if screen_name:
        user = await client.get_user_by_screen_name(screen_name)
        print(f"\n=== PROFILE: @{user.screen_name} ===")
        print(f"Name: {user.name}")
        print(f"Bio: {user.description}")
        print(f"Location: {user.location}")
        print(f"Followers: {user.followers_count}")
        print(f"Following: {user.following_count}")
        print(f"Tweets: {user.statuses_count}")
        print(f"Joined: {user.created_at}")
        
        tweets = await user.get_tweets('Tweets', count=10)
        print(f"\n=== RECENT TWEETS ===")
        for i, t in enumerate(tweets):
            print(f"\n--- {i+1}. ({t.created_at}) ---")
            print(f"{t.full_text[:500]}")
            print(f"❤ {t.favorite_count} | 🔁 {t.retweet_count} | 👁 {t.view_count}")

asyncio.run(main())
