from flask import Flask, request, render_template
import praw
import openai

app = Flask(__name__)

# Initialize the Reddit and OpenAI APIs
reddit = praw.Reddit(client_id='your_client_id',
                     client_secret='your_client_secret',
                     user_agent='Integrate Reddit API and ChatGPT API by u/dturchiarelli')

openai.api_key = 'your_api_key'

# Define a function to search Reddit and return the results
def search_reddit(query, subreddit):
    search_results = reddit.subreddit(subreddit).search(query)
    results = []
    for result in search_results:
        results.append({
            'title': result.title,
            'text': result.selftext
        })
    return results

# Define a function to generate a response using the OpenAI API
def get_gpt_response(question):
    response = openai.Completion.create(
        engine='davinci',
        prompt=question,
        max_tokens=2000
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
