import os
import googlemaps
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import requests

# Load API keys from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")

# Initialize Google Maps API Client
gmaps = googlemaps.Client(key=google_maps_api_key)

# 1️⃣ **Function to Extract District, State, Country**
def get_location_details(lat, lng):
    try:
        reverse_geocode_result = gmaps.reverse_geocode((lat, lng))
        if not reverse_geocode_result:
            return None, None  # No results found
        country, state = None, None
        for result in reverse_geocode_result:
            for component in result["address_components"]:      
                if "country" in component["types"]:
                    country = component["long_name"]
                if "administrative_area_level_1" in component["types"]:
                    state = component["long_name"]
    

        return state, country  # Return extracted values

    except Exception as e:
        print(f"⚠️ Error fetching location: {e}")
        return None, None, None

# 2️⃣ **Function to Fetch News Based on Location**

import requests

def get_disaster_news(location):
    disaster_keywords = [
        "earthquake", "flood", "explosion", "hurricane", "landslide",
        "wildfire", "cyclone", "tsunami", "pandemic", "crisis", "disaster", "calamity"
    ]

    all_articles = []

    for keyword in disaster_keywords:
        url = f"https://newsapi.org/v2/everything?q={location} {keyword}&language=en&apiKey={news_api_key}"
        response = requests.get(url)
        data = response.json()

        if data.get("status") == "ok" and "articles" in data:
            all_articles.extend(data["articles"])

    # **Filter only disaster-related news for the correct location**
    filtered_news = []
    for article in all_articles:
        title = article.get("title", "")
        description = article.get("description", "")
        source_name = article.get("source", {}).get("name", "")

        if title and description:
            title = title.lower()
            description = description.lower()

            # Check if the article is really about a disaster & the correct location
            if any(keyword in title or keyword in description for keyword in disaster_keywords) and location.lower() in (title + description + source_name).lower():
                filtered_news.append(f"{article['title']} - {article['description']}")

    if not filtered_news:
        print("⚠️ No disaster-related news found!")
        return []

    return filtered_news[:5]


# 3️⃣ **Function to Summarize News**
def summarize_news(news_articles, location_level):
    if not news_articles:
        return f"No disaster updates available for {location_level}."

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5, openai_api_key=openai_api_key)

    template = f"""
    Summarize the following disaster-related news into a short and clear update for users about {location_level}, Only give information about {location_level} that is if it is the state then give news about state only and not country, similarly with country also :
    {{news}}
    """
    prompt = PromptTemplate(input_variables=["news"], template=template)
    chain = prompt | llm  # Chain prompt with LLM model

    summary = chain.invoke({"news": "\n".join(news_articles)})  # Use .invoke()
    return summary.content.strip()

# 4️⃣ **Main Function: Fetch and Summarize News for District, State, and Country**
def disaster_alert(lat, lng):
    state, country = get_location_details(lat, lng)

    if  not state and not country:
        return "Could not determine your location."

    print(f"📍 Location Details:  State - {state}, Country - {country}\n")

    # Fetch and summarize news for each level
    news_summaries = []

    

    if state:
        state_news = get_disaster_news(state)
        news_summaries.append(f"**State ({state}) News:**\n{summarize_news(state_news, state)}")

    if country:
        country_news = get_disaster_news(country)
        news_summaries.append(f"**Country ({country}) News:**\n{summarize_news(country_news, country)}")

    return "\n\n".join(news_summaries)

# 5️⃣ **Example Usage**
latitude, longitude = 8.4697, 76.9818  # Example coordinates for Trivandrum, India
alert_message = disaster_alert(latitude, longitude)
print(alert_message)
