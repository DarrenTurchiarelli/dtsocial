import praw
import openai

client_id      = 'your_client_id'
client_secret  = 'your_client_secret'
user_agent     = 'your_user_agent'
openai_api_key = 'your_openai_api_key'

reddit = praw.Reddit(client_id     = client_id,
                     client_secret = client_secret,
                     user_agent= user_agent)

openai.api_key = openai_api_key

def get_gpt_response(question):
    response = openai.Completion.create(
        engine='davinci',
        prompt=question,
        max_tokens=100
    )
    return response.choices[0].text.strip()

def search_reddit(query, subreddit):
    search_results = reddit.subreddit(subreddit).search(query)
    results = []
    count = 0
    for result in search_results:
        if count == 5: # limit the results to 5
            break
        results.append({
            'title': result.title,
            'text': result.selftext
        })
        count += 1
    return results

while True:
    user_input = input('Ask a question matey: ')
    reddit_results = search_reddit(user_input, 'Azure')
    gpt_response = get_gpt_response(user_input)
    print('Reddit results:')
    for result in reddit_results:
        print(result['title'])
        print(result['text'])
    print('ChatGPT response:')
    print(gpt_response)
