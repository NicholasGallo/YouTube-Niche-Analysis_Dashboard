import requests
import pandas as pd
import time
import isodate 

API_KEY = ''#INSERT API KEY

# List of YouTube handles to analyze
handles = ['@nexpo','@scaretheater','@chillingscares','@abyssaldetective','@scaretheater','@nickcrowley','@mrnightmare','@virtualcarbon','@something_sinister','@realhorrortok','@lazyMasquerade','@shaiivalley','@blameitonjorge','@mooncrime','@tuv','@thevoid','@saganHawkes','@mrballen','@sirius','@feartales','@top5s','@sirspooks']


all_videos = []

def get_channel_id(handle):
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={handle}&key={API_KEY}"
    response = requests.get(search_url).json()
    if not response.get('items'):
        print(f"Channel not found for handle: {handle}")
        return None
    return response['items'][0]['snippet']['channelId'], response['items'][0]['snippet']['title']

def get_uploads_playlist(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={API_KEY}"
    response = requests.get(url).json()
    return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def get_videos_from_playlist(playlist_id):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={playlist_id}&key={API_KEY}"
    return requests.get(url).json()['items']

def get_video_details(video_ids):
    ids = ','.join(video_ids)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={ids}&key={API_KEY}"
    return requests.get(url).json()['items']

def parse_duration(iso_duration):
    try:
        return isodate.parse_duration(iso_duration).total_seconds()
    except:
        return None

for handle in handles:
    result = get_channel_id(handle)
    if not result:
        continue
    channel_id, channel_title = result
    print(f"🔍 Fetching videos from: {channel_title}")
    
    playlist_id = get_uploads_playlist(channel_id)
    videos = get_videos_from_playlist(playlist_id)
    video_ids = [v['snippet']['resourceId']['videoId'] for v in videos]

    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        details = get_video_details(batch_ids)
        
        for video in details:
            snippet = video['snippet']
            stats = video['statistics']
            duration_iso = video['contentDetails']['duration']
            duration_sec = parse_duration(duration_iso)

            all_videos.append({
                'channel_handle': handle,
                'channel_title': channel_title,
                'video_id': video['id'],
                'title': snippet.get('title'),
                'publish_date': snippet.get('publishedAt'),
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'comment_count': int(stats.get('commentCount', 0)),
                'duration_seconds': duration_sec,
                'duration_iso': duration_iso
            })

        time.sleep(1)

# Export to CSV
df = pd.DataFrame(all_videos)
df.to_csv('youtube_horror_video_stats_with_duration.csv', index=False)
print("Saved video data with duration to 'youtube_horror_video_stats_with_duration.csv'")
