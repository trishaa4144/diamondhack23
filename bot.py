import discord
import feedparser
import os
import asyncio
import json

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
article_history_file = 'article_history.json'


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def load_article_history():
    """
    Load article history from article_history_file
    """
    try:
        with open(article_history_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_article_history(article_history):
    """
    Save history to article_history_file
    """
    with open(article_history_file, 'w') as file:
        json.dump(article_history, file)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    first_channel = client.guilds[0].text_channels[0]

    # Every minute, check for new articles. If a new article has been posted, send the
    # link to the article to the first text channel in the Discord server
    while True:
        await first_channel.send("fetching rss feed ...")

        article_history = load_article_history()

        feed = feedparser.parse('https://dbknews.com/feed/')

        for entry in feed.entries:
            if entry.link not in article_history:
                await first_channel.send(f"new article just dropped: {entry.title}\n{entry.link}")
                article_history.append(entry.link)
        
        save_article_history(article_history)

        await asyncio.sleep(60)  # Sleep for 60 seconds


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$search'):
        await message.channel.send('searching')

client.run(BOT_TOKEN)