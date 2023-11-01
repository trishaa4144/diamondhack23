import discord
import feedparser
import os
import asyncio
import yaml

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
            if entry.link not in article_history:
                print(f"\"{entry.title}\" has not been seen yet, notifying.")
                await first_channel.send(f"New article from The Diamondback!:\n**{entry.title}**\n{entry.link}")
                # We can use GPT to summarize the article contents (key: entry[content][value]) here
                article_history.add(entry.link)
        
        save_article_history()

        await asyncio.sleep(60 * 5)  # Sleep for 60 seconds


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$search'):
        await message.channel.send('searching')

if __name__ == '__main__':
    article_history = load_article_history()
    try:
        client.run(BOT_TOKEN)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        save_article_history()