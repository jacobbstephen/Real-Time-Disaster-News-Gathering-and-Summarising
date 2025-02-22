# Real-Time-Disaster-News-Gathering-and-Summarising

The project uses NewsAPi, Google Maps APi and Open AI to gather relevant news for a particular location and summarize it.
Steps
1. Install all the required packages
2. Load API keys from .env file
3. Intialize Google Maps API Client
4. Reverse geocode the latitude and longititude and extract the state and country from the result of reverse geoencoding.
5. Implement the function to get the disaster news for the state and country seperately and summarise the news using LLM.


Function get disaster news [ get_disaster_news ()]
1. Declare the keywords for disaster
2. for each keywords send a API request to find news corresponding to it and append it.
3. for all the news, filter only disaster news for the current location
4. return the filtered news

Function to summarize the news [ summarize_news()]
1. Create an AI Chat Model (LLM) using OpenAi  gpt-3.5-turbo
2. Define a Prompt Template
3. Create a Prompt Template Object
4. Chain the prompt template with LLM
5. Invoke the model to generate the summay of the news articles
6. Return the final summary
