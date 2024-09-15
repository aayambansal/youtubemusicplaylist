import os
import re
from googleapiclient.discovery import build
from datetime import timedelta

def get_api_key():
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        api_key = input("Please enter your YouTube API Key: ").strip()
    return api_key

def get_youtube_service(api_key):
    return build('youtube', 'v3', developerKey=api_key)

def get_playlist_duration(youtube, playlist_url):
    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        return "Invalid YouTube playlist URL"
    
    total_seconds = 0
    next_page_token = None
    
    while True:
        playlist_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()
        
        video_ids = [item['contentDetails']['videoId'] for item in playlist_response['items']]
        
        video_request = youtube.videos().list(
            part='contentDetails',
            id=','.join(video_ids)
        )
        video_response = video_request.execute()
        
        for item in video_response['items']:
            duration = item['contentDetails']['duration']
            total_seconds += parse_duration(duration)
        
        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break
    
    return str(timedelta(seconds=total_seconds))

def parse_duration(duration):
    regex = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(regex, duration)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds
    return 0

def extract_playlist_id(url):
    patterns = [
        r'(?<=list=)[^&\n]+',
        r'(?<=youtube.com/playlist\?list=)[^&\n]+',
        r'(?<=youtu.be/)[^&\n]+'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(0)
    return None

def main():
    print("YouTube Playlist Duration Calculator")
    print("====================================")
    
    api_key = get_api_key()
    youtube = get_youtube_service(api_key)
    
    while True:
        playlist_url = input("Please enter a YouTube playlist URL (or 'q' to quit): ").strip()
        
        if playlist_url.lower() == 'q':
            print("Thank you for using the YouTube Playlist Duration Calculator. Goodbye!")
            break
        
        try:
            total_duration = get_playlist_duration(youtube, playlist_url)
            print(f"Total playlist duration: {total_duration}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        print("\n")

if __name__ == "__main__":
    main()
