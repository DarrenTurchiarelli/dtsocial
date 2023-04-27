from flask import Flask, request, render_template
import praw
import openai

app = Flask(__name__)

# Define the API keys
client_id      = 'your_client_id'
client_secret  = 'your_client_secret'
user_agent     = 'your_user_agent'
openai_api_key = 'your_openai_api_key'

# Initialize the Reddit and OpenAI APIs
reddit = praw.Reddit(client_id     = client_id,
                     client_secret = client_secret,
                     user_agent    = user_agent)

openai.api_key = openai_api_key

# Define a function to search Reddit and return the results
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

# Define a function to generate a response using the OpenAI API
def get_gpt_response(question):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=question,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Define the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Define a route to handle the form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Get the user's question from the form
    question = request.form['question']
    
    # Search Reddit for relevant results
    reddit_results = search_reddit(question, 'azure')
    
    # Generate a response using the OpenAI API
    gpt_response = get_gpt_response(question)
    
    # Render the results template with the Reddit and GPT results
    return render_template('results.html', reddit_results=reddit_results, gpt_response=gpt_response)

if __name__ == '__main__':
    app.run(debug=True)
