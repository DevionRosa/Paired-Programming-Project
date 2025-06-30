import os 
from google import genai
from google.genai import types

my_api_key = os.getenv('GENAI_KEY')
my_yt_key = os.getenv('YOUTUBE_KEY')

genai.api_key = my_api_key

# Create an genAI client using the key from our environment variable
client = genai.Client(
    api_key=my_api_key,
)

# Create get response for YOUTUBE_KEY

#Store the tags of the Youtube Video

# Specify the model to use and the messages to send opposite tags
response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
      system_instruction="Pretend you are a YouTube creator uploading a video. You are given tags opposite to the video you are creating. Generate tags that are the opposite of the tags given."
    ),
    contents="What are the advantages of pair programming?", #The tags from the youtube api response
)

# Search for videos of the opposite tag and return a lsit (or playlist) of videos