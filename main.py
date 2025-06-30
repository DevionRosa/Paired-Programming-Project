import os 
import requests
import json
from google import genai
from google.genai import types

my_api_key = os.getenv('GENAI_KEY')
my_yt_key = os.getenv('YOUTUBE_KEY')

genai.api_key = my_api_key

# Create an genAI client using the key from our environment variable
client = genai.Client(
    api_key=my_api_key,
)

# Create post response for YOUTUBE_KEY
url = 'https://www.googleapis.com/youtube/v3/videos'
video_id = 'vm4H-GDUrWk'

params = {
    'part': 'snippet',
    'id': video_id,
    'key': my_yt_key
}

response = requests.get(url,params=params)
data = response.json()

print("status code:", response.status_code)
print("JSON:", data)


if 'items' in data and len(data['items']) > 0:
    snippet = data['items'][0]['snippet']
    title = snippet.get('title', '')
    description = snippet.get('description', '')
    tags = snippet.get('tags', [])
    
    print("Title:", title)
    print("Description:", description)
    print("Tags:", tags)


# Ask user for input (must be a youtube link)

# Create get requests for a Youtube video

# Store the tags of the Youtube Video

# Specify the model to use and the messages to send opposite tags
response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
      system_instruction="Pretend you are a YouTube creator uploading a video. You are given tags opposite to the video you are creating. Generate tags that are the opposite of the tags given."
    ),
    contents="What are the advantages of pair programming?", #The tags from the youtube api response
)

# Search for videos of the opposite tag and return a lsit (or playlist) of videos