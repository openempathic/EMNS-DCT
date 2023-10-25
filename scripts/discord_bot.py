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

if __name__ == '__main__':
    message = requests.get(f"https://dct.openempathic.ai/stats/?key={os.environ.get('DCT_API_KEY', 0)}").json()
    message = format_leaderboard(message)
    post_to_discord(f"https://discord.com/api/webhooks/{os.environ.get('DISCORD_WEBHOOK', 'changeme')}", message)
    # post_to_discord(f"https://discord.com/api/webhooks/{os.environ.get('TEST_DISCORD_WEBHOOK', 'changeme')}", message)
