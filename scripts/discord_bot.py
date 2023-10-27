import requests
import json
import os

def post_to_discord(webhook_url, content):
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "content": content,
    }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
    return response.status_code

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

if __name__ == '__main__':
    stats = requests.get(f"https://dct.openempathic.ai/stats/?key={os.environ.get('DCT_API_KEY', 0)}").json()

    top_users = format_leaderboard(stats)
    emotion_stats = format_emotions(stats)

    combined_message = top_users + "\n\n" + emotion_stats

    # post_to_discord(f"https://discord.com/api/webhooks/{os.environ.get('DISCORD_WEBHOOK', 'changeme')}", combined_message)
    post_to_discord(f"https://discord.com/api/webhooks/{os.environ.get('TEST_DISCORD_WEBHOOK', 'changeme')}", combined_message)
