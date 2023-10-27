import os
import requests
import discord
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.members = False
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Store the ID of the messages (starts as None)
LEADERBOARD_MESSAGE_ID = EMOTION_MESSAGE_ID = None

BOT_TOKEN = os.environ.get("BOT_TOKEN", 0)
CHANNEL_ID = int(os.environ.get("LEADERBOARD_CHANNEL_ID", 0))

def format_leaderboard(myjson):
    # Define emojis for the ranks - extend the list as needed
    emojis = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    if len(myjson["top_users"]) > len(emojis):
        emojis.extend([":medal:"] * (len(myjson["top_users"]) - len(emojis)))

    message = "# 🏆 **Top 10 Users** 🏆\n\n"

    for index, user in enumerate(myjson["top_users"]):
        # Remove email from username if it is not already removed
        # username = re.sub(r'@.*$', '', user["author__username"])
        username = user["author__username"]
        message += f"{emojis[index]} **{username}**: {user['submission_count']} annotations\n"
    
    return message

def format_emotions(myjson):
    emojis = {  "Curious And Fascinated":"🤩",
                "Pensive And Reflective":"🤔",
                "Fearful And Anxious":"😰",
                "Happy And Energetic":"😄",
                "Calm And Composed":"😌",
                "Focused And Attentive":"🤓",
                "Surprised And Confused":"😲",
                "Sad And Despondent":"😢",
                "Romantic And Passionate":"😍",
                "Seductive And Enticing":"😘",
                "Angry And Irritated":"😠",
                "Persistent And Determined":"💪",
                "Discomposed And Unsettled":"😓",
                "Grumpy And Cranky":"😡",
                "Disgusted":"🤢"}

    sorted_emotions = sorted(myjson["emotion_counts"].items(), key=lambda x: x[1], reverse=True)

    message = "# 🎭 **Emotion Counts** 🎭\n\n"
    for emotion, count in sorted_emotions:
        formatted_emotion = emotion.replace('_', ' ').title()
        emoji = emojis.get(formatted_emotion, "")  # Get the emoji, default to an empty string if not found
        message += f"{emoji} **{formatted_emotion}**: {count} samples\n"
    return message


@bot.event
async def on_ready():
    auto_update_leaderboard.start()
    auto_update_emotions.start()

@tasks.loop(minutes=5)
async def auto_update_leaderboard():
    global LEADERBOARD_MESSAGE_ID

    # Initialize leaderboard if not already
    if not LEADERBOARD_MESSAGE_ID:
        channel = bot.get_channel(CHANNEL_ID)
        msg = await channel.send("# 🏆 **Top 10 Users** 🏆")
        LEADERBOARD_MESSAGE_ID = msg.id

    # Update the leaderboard
    stats = requests.get(f"https://dct.openempathic.ai/stats/?key={os.environ.get('DCT_API_KEY', 0)}").json()
    channel = bot.get_channel(CHANNEL_ID)
    msg = await channel.fetch_message(LEADERBOARD_MESSAGE_ID)
    await msg.edit(content=f"{format_leaderboard(stats)}")

@tasks.loop(minutes=5)
async def auto_update_emotions():
    global EMOTION_MESSAGE_ID

    # Initialize emotion if not already
    if not EMOTION_MESSAGE_ID:
        channel = bot.get_channel(CHANNEL_ID)
        msg = await channel.send("# 🎭 **Emotion Counts** 🎭")
        EMOTION_MESSAGE_ID = msg.id

    # Update the emotion
    stats = requests.get(f"https://dct.openempathic.ai/stats/?key={os.environ.get('DCT_API_KEY', 0)}").json()
    channel = bot.get_channel(CHANNEL_ID)
    msg = await channel.fetch_message(EMOTION_MESSAGE_ID)
    await msg.edit(content=f"{format_emotions(stats)}")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"An error occurred: {error}")

# Run the bot
bot.run(BOT_TOKEN)