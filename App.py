from flask import Flask, request, render_template
import praw
import openai
import os
import json

app = Flask(__name__)

# Load config values
with open(r'AzureOpenAIconfig.json') as config_file:
    config_details = json.load(config_file)

# Setting up the deployment name
chatgpt_model_name = config_details['CHATGPT_MODEL_NAME']

# This is set to "azure"
openai.api_type = "azure"

# The API key for your Azure OpenAI resource.
openai.api_key = config_details['OPENAI_API_KEY']

# The base URL for your Azure OpenAI resource. e.g. "https://<your resource name>.openai.azure.com"
openai.api_base = config_details['OPENAI_API_BASE']

# Currently Chat Completion API have the following versions available: 2023-03-15-preview
openai.api_version = config_details['OPENAI_API_VERSION']

openai.gpt_type = config_details['OPENAI_GPT_TYPE']
# Initialize the Reddit APIs
reddit = praw.Reddit(client_id     = config_details['REDDIT_CLIENT_ID'],
                     client_secret = config_details['REDDIT_CLIENT_SECRET'],
                     user_agent    = config_details['REDDIT_USER_AGENT'])

#chatgpt_api_key   = (config_details['CHATGPT_API_KEY'])
#openai.api_key    = chatgpt_api_key 

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

# Define the function to communicate with Azure OpenAI ChatGPT  
def generate_response(question):  
    model_engine = chatgpt_model_name  
    response = openai.Completion.create(  
        engine= model_engine,  
        prompt= question, 
        temperature= 0.0, 
        max_tokens= 100,
        top_p= 0.0,  
        frequency_penalty= 0,
        presence_penalty= 0,
        stop= None           
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
    user_question = request.form['question']
    
    # Search Reddit for relevant results
    reddit_results = search_reddit(user_question, 'azure')
    
    # Generate a response using the OpenAI API
    generated_response = generate_response(user_question)
    
    # Render the results template with the Reddit and GPT results
    return render_template('results.html', reddit_results=reddit_results, response=generated_response)

if __name__ == '__main__':
    app.run(debug=True)
