import os 
import requests
import json
from google import genai
from google.genai import types
from metadata_db import setup_db, get_video_metadata, cache_video_metadata

def get_video_id(youtube_link: str) -> str:
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
    return video_id

def fetch_video(video_id: str, yt_key: str) -> str:
    print("Fetching from YouTube API...")
    # Create post response for YOUTUBE_KEY
    url = 'https://www.googleapis.com/youtube/v3/videos'

    params = {
        'part': 'snippet',
        'id': video_id,
        'key': yt_key
    }

    # Create get requests for a Youtube video
    response = requests.get(url,params=params)
    return response

def gemini_response(yt_tag: str, my_api_key: str) -> str:
    
    genai.api_key = my_api_key
    client = genai.Client(
        api_key=my_api_key,
    )
    # Specify the model to use and the messages to send opposite tags
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
        system_instruction= "Pretend you are searching for a video on YouTube. You have to search for a video opposite to the most relevent tags given to you in only 3 words or less. Return those 3 words and those words only."#"Pretend you are a YouTube creator uploading a video. You are given tags opposite to the video you are creating. Generate 3 of the most relevant opposite tags, AND THE TAGS ONLY, that are the opposite of the tags given."
        ),
        contents=yt_tag, #The tags from the youtube api response
    )
    return response.text

def youtube_search(tags: str, yt_key: str) -> str:
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': tags,
        'key': yt_key,
        'type': "video"
    }
    response = requests.get(url, params = params)
    return response

def flatten_dict(data):
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
    return flattened_results

def print_searches(results):
    print("Printing the first five results that match the alternative tags...\n")
    for result in results:
        title = result['title']
        desc = result['description']
        channel = result['channelTitle']
        yt_id = result['id_value']

        print(f"Link: https://www.youtube.com/watch?v={yt_id}")
        print("Title: ", title)
        print("Description: ", desc)
        print("Channel Name: ", channel, '\n')

def main():


    my_api_key = os.getenv('GENAI_KEY')
    my_yt_key = os.getenv('YOUTUBE_KEY')

    # Create an genAI client using the key from our environment variable

    print("Welcome to the YouTube Video Explorer!")
    print("This tool helps you discover YouTube videos that are 'opposite' to a video you provide.")
    print("Here's how it works:")
    print("1. You'll provide a YouTube video link.")
    print("2. The program will extract details like its title, description, and tags from YouTube.")
    print("3. It then uses advanced AI (Gemini) to brainstorm search terms that represent the 'opposite' themes or content of the original video's tags.")
    print("4. Finally, it searches YouTube using these new, 'opposite' terms and displays a list of relevant videos.")
    print("This is perfect for finding new content, exploring different perspectives, or just having fun with AI-powered discovery!\n")

    # Ask user for input (must be a youtube link)
    # Gets the YouTube ID from the link
    video_id = ""
    while not video_id:
        youtube_link = input("Enter a YouTube Link (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ: ")
        video_id = get_video_id(youtube_link)
        if not video_id:
            print("Invalid YouTube link. Please enter a valid YouTube video URL.")

    video_id = get_video_id(youtube_link)
    setup_db()
    #check cache first 
    cached = get_video_metadata(video_id)

    #if video in cache load from cache, otherwise call API and store in cache
    if cached:
        print("Loading already stored tags from the database...")
        title = cached['title']
        description = cached['description']
        tags = cached['tags']

    else:
        fetched = fetch_video(video_id, my_yt_key)
        if fetched.status_code == 200:
            data = fetched.json()
            if 'items' in data and len(data['items']) > 0:
                snippet = data['items'][0]['snippet']
                title = snippet.get('title', '')
                description = snippet.get('description', '')
                tags = snippet.get('tags', [])

                cache_video_metadata(video_id,title,description,tags)
            else:
                print(f"No video details found for ID '{video_id}'. It might be private, deleted, or incorrect.")
                return # Exit if no video details
        else:
            print(f"Error fetching video details (HTTP Status: {response_video_fetch.status_code}): {response_video_fetch.text}")
            return
        
    for i in range(len(tags)):
        tags[i] = '#' + tags[i]

    new_tags = gemini_response(' '.join(tags), my_api_key)
    youtube_fetched = youtube_search(new_tags, my_yt_key)
    if youtube_fetched.status_code == 200:
        data = youtube_fetched.json()
        flattened_results = flatten_dict(data)
        print_searches(flattened_results)
    else:
        print(f"Error searching YouTube (HTTP Status: {response_Youtube.status_code}): {response_Youtube.text}")
        return

if __name__ == "__main__":
    main()
# Search for videos of the opposite tag and return a list (or playlist) of videos