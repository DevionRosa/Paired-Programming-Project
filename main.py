import os 
import requests
import json
from google import genai
from google.genai import types
from metadata_db import setup_db, get_video_metadata, cache_video_metadata

my_api_key = os.getenv('GENAI_KEY')
my_yt_key = os.getenv('YOUTUBE_KEY')

genai.api_key = my_api_key

# Create an genAI client using the key from our environment variable
client = genai.Client(
    api_key=my_api_key,
)

#Setup DB and makes sure the table is ready
setup_db()

# Ask user for input (must be a youtube link)
# Gets the YouTube ID from the link
youtube_link = input("Enter a YouTube Link: ")
video_id = ""
start = False
counter = 0
for char in youtube_link:
    # https://www.youtube.com/watch?v=vm4H-GDUrWk&ab_channel=ForgeLabs
    if char == '=':
        start = True
        continue
    if char == '&':
        break
    if start:
        video_id = video_id + char


#check cache first 
cached = get_video_metadata(video_id)

#if video in cache load from cache, otherwise call API and store in cache
if cached:
    print("Loading from cache...")
    title = cached['title']
    description = cached['description']
    tags = cached['tags']

else:
    print("Fetching from YouTube API...")
    # Create post response for YOUTUBE_KEY
    url = 'https://www.googleapis.com/youtube/v3/videos'

    params = {
        'part': 'snippet',
        'id': video_id,
        'key': my_yt_key
    }

    # Create get requests for a Youtube video
    response = requests.get(url,params=params)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        snippet = data['items'][0]['snippet']
        title = snippet.get('title', '')
        description = snippet.get('description', '')
        tags = snippet.get('tags', [])

        cache_video_metadata(video_id,title,description,tags)
        
print("Title:", title)
print("Description:", description)
print("Tags:", tags)

for i in range(len(tags)):
    tags[i] = '#' + tags[i]

# Specify the model to use and the messages to send opposite tags
response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
      system_instruction="Pretend you are a YouTube creator uploading a video. You are given tags opposite to the video you are creating. Generate 3 of the most relevant opposite tags, AND THE TAGS ONLY, that are the opposite of the tags given."
    ),
    contents=" ".join(tags), #The tags from the youtube api response
)

# Removes the '#' in each tag so we can run it through the YouTube API
new_tags = response.text.replace('#', '')
print(new_tags)

url = 'https://www.googleapis.com/youtube/v3/search'
params = {
    'part': 'snippet',
    'q': new_tags,
    'key': my_yt_key
}

response = requests.get(url, params = params)
data = response.json()

flattened_results = []
for item in data['items']:
    entry = {}
    entry['kind'] = item['kind']
    
    # Extract ID based on the 'kind'
    if item['id']['kind'] == 'youtube#video':
        entry['id_type'] = 'video'
        entry['id_value'] = item['id']['videoId']
    elif item['id']['kind'] == 'youtube#playlist':
        entry['id_type'] = 'playlist'
        entry['id_value'] = item['id']['playlistId']
    # Add other types as needed (e.g., 'youtube#channel')
    else:
        entry['id_type'] = item['id']['kind']
        entry['id_value'] = None # Or handle accordingly

    entry['title'] = item['snippet']['title']
    entry['description'] = item['snippet']['description']
    entry['channelTitle'] = item['snippet']['channelTitle']

    flattened_results.append(entry)

for result in flattened_results:
    print(result)
# Search for videos of the opposite tag and return a lsit (or playlist) of videos