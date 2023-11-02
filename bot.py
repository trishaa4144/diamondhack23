import discord
import feedparser
import os
import asyncio
import json
import yaml 
from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
article_history_file = 'article_history.yml'
article_history = set()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def load_article_history():
    try:
        with open(article_history_file, 'r') as file:
            return set(yaml.safe_load(file))
    except (FileNotFoundError, yaml.YAMLError):
        return set()

def save_article_history():
    with open(article_history_file, 'w') as file:
        yaml.dump(list(article_history), file)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    first_channel = client.guilds[0].text_channels[0]

    # Every minute, check for new articles. If a new article has been posted, send the
    # link to the article to the first text channel in the Discord server
    while True:
        print("fetching rss feed ...")

        feed = feedparser.parse('https://dbknews.com/feed/')

        for entry in feed.entries:
            add_flag = False
            for item in entry['tags']:
                if item['term'] == "Campus" or item['term'] == "Campus Life":
                    add_flag = True

            if add_flag == True and (entry.link not in article_history):
                print(f"\"{entry.title}\" has not been seen yet, notifying.")
                # contents
                contents = entry['content'][0]['value']
                await first_channel.send(f"New article from The Diamondback:\n**{entry.title}**\n{entry.link}\n")

                article_history.add(entry.link)
        
        save_article_history()

        await asyncio.sleep(60 * 5)  # Sleep for 60 seconds


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$ask'):
        await message.channel.send("searching database...")
        await message.channel.send(query(message.content[4:]))

def query(question: str):
    storage_context = StorageContext.from_defaults(persist_dir='./storage')
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    response = query_engine.query(question)   
    return response 


if __name__ == '__main__':
    article_history = load_article_history()
    try:
        client.run(BOT_TOKEN)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        save_article_history()