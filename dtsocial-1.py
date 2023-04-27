import praw

reddit = praw.Reddit(client_id='your_client_id',
                     client_secret='your_client_secret',
                     user_agent='Integrate Reddit API and ChatGPT API by u/dturchiarelli')

search_results = reddit.subreddit('Azure').search('compute')

for result in search_results:
    print(result.title)
    print(result.selftext)
