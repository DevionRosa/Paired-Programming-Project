# YouTube Opposite Video Recommender

This project calls the YouTube API to extract metadata from a video using its URL, and generates antonyms using 
Google Gemini's API, and then searches YouTube using these new tags to come up with "anti-recommendations".
## Features
- Extracts metadata (title, description, tags) using YouTube Data API
- Checks SQL database to see if metadata is already stored, reducing API calls
- Uses Gemini to generate opposite tags for a video
- Searches YouTube for videos based on opposite tags
- Displays top 5 relevant search results
## Project Structure
|- main.py - Entry point for program \
|- metadata_db.py - SQLite database for caching metadata \ 
|- testing.py - Contains unit tests for functions \
|- youtube_antirec.db - Database that is created upon first running the program \ 
|- README.md \

## Usage
Run the following command in the terminal: python3 main.py \ 
Enter a link upon being prompted \
To run unit tests use: python3 -m unittest testing.py 
