import praw

client_id     = 'your_client_id'
client_secret = 'your_client_secret'
user_agent    = 'your_user_agent'

reddit = praw.Reddit(client_id     = client_id,
                     client_secret = client_secret,
                     user_agent    = user_agent)

for result in search_results:
    print(result.title)
    print(result.selftext)
