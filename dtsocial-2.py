import praw
import openai

openai.api_key = 'your_api_key'

reddit = praw.Reddit(client_id='your_client_id',
                     client_secret='your_client_secret',
                     user_agent='Integrate Reddit API and ChatGPT API by u/dturchiarelli')

def get_gpt_response(question):
    response = openai.Completion.create(
        engine='davinci',
        prompt=question,
        max_tokens=2000
    )
    return response.choices[0].text.strip()

def search_reddit(query, subreddit):
    search_results = reddit.subreddit(subreddit).search(query)
    results = []
    for result in search_results:
        results.append({
            'title': result.title,
            'text': result.selftext
        })
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
