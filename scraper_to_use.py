# import requests
# import sys
# import time
# import os
# import argparse
# import isodate
# from datetime import timedelta

# # List of snippet features to collect
# snippet_features = ["title", "publishedAt", "channelTitle"]

# # Column headers for the CSV (only the properties you requested)
# header = ["title", "publishedAt", "channelTitle", "category", "tags", "duration", 
#           "live_content", "view_count", "likes", "comment_count", 
#           "subscriber_count", "engagement_rate", "total_view_count", "channel_country"]

# # Category mapping
# category_mapping = {
#     "1": "Film & Animation",
#     "2": "Autos & Vehicles",
#     "10": "Music",
#     "15": "Pets & Animals",
#     "17": "Sports",
#     "18": "Short Movies",
#     "19": "Travel & Events",
#     "20": "Gaming",
#     "21": "Videoblogging",
#     "22": "People & Blogs",
#     "23": "Comedy",
#     "24": "Entertainment",
#     "25": "News & Politics",
#     "26": "Howto & Style",
#     "27": "Education",
#     "28": "Science & Technology",
#     "29": "Nonprofits & Activism",
#     "30": "Movies",
#     "31": "Anime/Animation",
#     "32": "Action/Adventure",
#     "33": "Classics",
#     "34": "Comedy",
#     "35": "Documentary",
#     "36": "Drama",
#     "37": "Family",
#     "38": "Foreign",
#     "39": "Horror",
#     "40": "Sci-Fi/Fantasy",
#     "41": "Thriller",
#     "42": "Shorts",
#     "43": "Shows",
#     "44": "Trailers"
# }

# def setup(api_path, code_path):
#     with open(api_path, 'r') as file:
#         api_key = file.readline().strip()

#     with open(code_path) as file:
#         country_codes = [x.strip() for x in file]

#     return api_key, country_codes

# def prepare_feature(feature):
#     feature = str(feature).replace('"', '""')  # Escape quotes for CSV
#     return f'"{feature}"'

# def api_request(api_key, page_token, country_code):
#     request_url = (
#         f"https://www.googleapis.com/youtube/v3/videos"
#         f"?part=snippet,statistics,contentDetails&chart=mostPopular"
#         f"&regionCode={country_code}&maxResults=50"
#         f"&key={api_key}"
#     )
#     if page_token:
#         request_url += f"&pageToken={page_token}"
    
#     request = requests.get(request_url)

#     if request.status_code == 429:
#         print("Temp-banned due to excess requests, please wait and continue later")
#         sys.exit()
#     elif request.status_code != 200:
#         print(f"Error: {request.status_code} - {request.text}")
#         return {}

#     return request.json()

# def get_tags(tags_list):
#     return prepare_feature("|".join(tags_list))

# def get_channel_stats(api_key, channel_id):
#     """
#     Fetch channel statistics: subscriber count, total view count, and country.
#     """
#     url = (
#         f"https://www.googleapis.com/youtube/v3/channels"
#         f"?part=snippet,statistics&id={channel_id}&key={api_key}"
#     )
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         stats = data['items'][0]['statistics']
#         snippet = data['items'][0]['snippet']
        
#         # Get subscriber count and total view count
#         subscriber_count = stats.get('subscriberCount', 0)
#         total_view_count = stats.get('viewCount', 0)
        
#         # Get the country (if available)
#         channel_country = snippet.get('country', 'Unknown')

#         return int(subscriber_count), int(total_view_count), channel_country
#     else:
#         print(f"Error fetching channel stats: {response.status_code}")
#         return 0, 0, 'Unknown'

# def parse_duration(duration_str):
#     """Convert ISO 8601 duration to decimal minutes."""
#     if not duration_str:
#         return 0.0  # Default to 0 minutes if the duration is missing
#     try:
#         # Parse the ISO 8601 duration string to a timedelta object
#         duration = isodate.parse_duration(duration_str)
#         if isinstance(duration, timedelta):
#             # Convert the duration to total minutes
#             total_minutes = duration.total_seconds() / 60
#             return round(total_minutes, 2)  # Round to 2 decimal places for clarity
#         else:
#             return 0.0  # In case the parsing fails, return 0 minutes
#     except isodate.ISO8601Error:
#         return 0.0  # Return 0 if parsing the duration fails

# def get_videos(api_key, items):
#     lines = []
#     for video in items:
#         if "statistics" not in video or "contentDetails" not in video:
#             continue

#         snippet = video['snippet']
#         statistics = video['statistics']
#         content_details = video['contentDetails']

#         # Collecting required snippet features
#         features = [prepare_feature(snippet.get(feature, "")) for feature in snippet_features]

#         # Map category
#         category_id = snippet.get("categoryId", "")
#         category = category_mapping.get(category_id, "Unknown")

#         # Collect tags
#         tags = get_tags(snippet.get("tags", ["[none]"]))

#         # Duration in minutes (decimal format)
#         duration_iso = content_details.get('duration', 'PT0S')  # Default to PT0S if missing
#         duration = parse_duration(duration_iso)

#         # Other fields
#         live_content = content_details.get('liveBroadcastContent', 'none')

#         # Statistics
#         view_count = int(statistics.get("viewCount", 0))
#         likes = int(statistics.get('likeCount', 0))
#         comment_count = int(statistics.get('commentCount', 0))

#         # Channel stats (subscriber count, total view count, and country)
#         channel_id = snippet.get("channelId", "")
#         subscriber_count, total_view_count, channel_country = get_channel_stats(api_key, channel_id)

#         # Engagement rate
#         engagement_rate = (likes + comment_count) / view_count if view_count else 0

#         # Prepare the CSV line
#         line = features + [prepare_feature(category)] + [prepare_feature(x) for x in [
#             tags, duration, live_content, view_count, likes, comment_count, 
#             subscriber_count, engagement_rate, total_view_count, channel_country
#         ]]
#         lines.append(",".join(line))
#     return lines

# def get_pages(api_key, country_code):
#     country_data = []
#     next_page_token = ""

#     while next_page_token is not None:
#         video_data_page = api_request(api_key, next_page_token, country_code)
#         next_page_token = video_data_page.get("nextPageToken", None)

#         items = video_data_page.get('items', [])
#         country_data += get_videos(api_key, items)

#     return country_data

# def write_to_file(output_dir, country_code, country_data):
#     print(f"Writing {country_code} data to file...")

#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     file_path = os.path.join(output_dir, f"{time.strftime('%y.%d.%m')}_{country_code}_videos.csv")
#     with open(file_path, "w+", encoding='utf-8') as file:
#         for row in country_data:
#             file.write(f"{row}\n")

# def get_data(api_key, country_codes, output_dir):
#     for country_code in country_codes:
#         country_data = [",".join(header)] + get_pages(api_key, country_code)
#         write_to_file(output_dir, country_code, country_data)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--key_path', help='Path to the file containing the api key', default='api_key.txt')
#     parser.add_argument('--country_code_path', help='Path to the file containing the list of country codes', default='country_codes.txt')
#     parser.add_argument('--output_dir', help='Path to save the outputted files', default='output/')

#     args = parser.parse_args()

#     api_key, country_codes = setup(args.key_path, args.country_code_path)
#     get_data(api_key, country_codes, args.output_dir)

import requests
import sys
import time
import os
import argparse
import isodate
from datetime import timedelta

# List of snippet features to collect (now including "description")
snippet_features = ["title", "publishedAt", "channelTitle", "description"]

# Column headers for the CSV (only the properties you requested)
header = ["title", "publishedAt", "channelTitle", "description", "category", "tags", "duration", 
          "live_content", "view_count", "likes", "comment_count", 
          "subscriber_count", "engagement_rate", "total_view_count", "channel_country"]

# Category mapping
category_mapping = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "18": "Short Movies",
    "19": "Travel & Events",
    "20": "Gaming",
    "21": "Videoblogging",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism",
    "30": "Movies",
    "31": "Anime/Animation",
    "32": "Action/Adventure",
    "33": "Classics",
    "34": "Comedy",
    "35": "Documentary",
    "36": "Drama",
    "37": "Family",
    "38": "Foreign",
    "39": "Horror",
    "40": "Sci-Fi/Fantasy",
    "41": "Thriller",
    "42": "Shorts",
    "43": "Shows",
    "44": "Trailers"
}

def setup(api_path, code_path):
    with open(api_path, 'r') as file:
        api_key = file.readline().strip()

    with open(code_path) as file:
        country_codes = [x.strip() for x in file]

    return api_key, country_codes

def prepare_feature(feature):
    feature = str(feature).replace('"', '""')  # Escape quotes for CSV
    return f'"{feature}"'

def api_request(api_key, page_token, country_code):
    request_url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet,statistics,contentDetails&chart=mostPopular"
        f"&regionCode={country_code}&maxResults=50"
        f"&key={api_key}"
    )
    if page_token:
        request_url += f"&pageToken={page_token}"
    
    request = requests.get(request_url)

    if request.status_code == 429:
        print("Temp-banned due to excess requests, please wait and continue later")
        sys.exit()
    elif request.status_code != 200:
        print(f"Error: {request.status_code} - {request.text}")
        return {}

    return request.json()

def get_tags(tags_list):
    return prepare_feature("|".join(tags_list))

def get_channel_stats(api_key, channel_id):
    """
    Fetch channel statistics: subscriber count, total view count, and country.
    """
    url = (
        f"https://www.googleapis.com/youtube/v3/channels"
        f"?part=snippet,statistics&id={channel_id}&key={api_key}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        stats = data['items'][0]['statistics']
        snippet = data['items'][0]['snippet']
        
        # Get subscriber count and total view count
        subscriber_count = stats.get('subscriberCount', 0)
        total_view_count = stats.get('viewCount', 0)
        
        # Get the country (if available)
        channel_country = snippet.get('country', 'Unknown')

        return int(subscriber_count), int(total_view_count), channel_country
    else:
        print(f"Error fetching channel stats: {response.status_code}")
        return 0, 0, 'Unknown'

def parse_duration(duration_str):
    """Convert ISO 8601 duration to decimal minutes."""
    if not duration_str:
        return 0.0  # Default to 0 minutes if the duration is missing
    try:
        # Parse the ISO 8601 duration string to a timedelta object
        duration = isodate.parse_duration(duration_str)
        if isinstance(duration, timedelta):
            # Convert the duration to total minutes
            total_minutes = duration.total_seconds() / 60
            return round(total_minutes, 2)  # Round to 2 decimal places for clarity
        else:
            return 0.0  # In case the parsing fails, return 0 minutes
    except isodate.ISO8601Error:
        return 0.0  # Return 0 if parsing the duration fails

def get_videos(api_key, items):
    lines = []
    for video in items:
        if "statistics" not in video or "contentDetails" not in video:
            continue

        snippet = video['snippet']
        statistics = video['statistics']
        content_details = video['contentDetails']

        # Collecting required snippet features
        features = [prepare_feature(snippet.get(feature, "")) for feature in snippet_features]

        # Map category
        category_id = snippet.get("categoryId", "")
        category = category_mapping.get(category_id, "Unknown")

        # Collect tags
        tags = get_tags(snippet.get("tags", ["[none]"]))

        # Duration in minutes (decimal format)
        duration_iso = content_details.get('duration', 'PT0S')  # Default to PT0S if missing
        duration = parse_duration(duration_iso)

        # Other fields
        live_content = content_details.get('liveBroadcastContent', 'none')

        # Statistics
        view_count = int(statistics.get("viewCount", 0))
        likes = int(statistics.get('likeCount', 0))
        comment_count = int(statistics.get('commentCount', 0))

        # Channel stats (subscriber count, total view count, and country)
        channel_id = snippet.get("channelId", "")
        subscriber_count, total_view_count, channel_country = get_channel_stats(api_key, channel_id)

        # Engagement rate
        engagement_rate = (likes + comment_count) / view_count if view_count else 0

        # Prepare the CSV line
        line = features + [prepare_feature(category)] + [prepare_feature(x) for x in [
            tags, duration, live_content, view_count, likes, comment_count, 
            subscriber_count, engagement_rate, total_view_count, channel_country
        ]]
        lines.append(",".join(line))
    return lines

def get_pages(api_key, country_code):
    country_data = []
    next_page_token = ""

    while next_page_token is not None:
        video_data_page = api_request(api_key, next_page_token, country_code)
        next_page_token = video_data_page.get("nextPageToken", None)

        items = video_data_page.get('items', [])
        country_data += get_videos(api_key, items)

    return country_data

def write_to_file(output_dir, country_code, country_data):
    print(f"Writing {country_code} data to file...")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = os.path.join(output_dir, f"{time.strftime('%y.%d.%m')}_{country_code}_videos.csv")
    with open(file_path, "w+", encoding='utf-8') as file:
        for row in country_data:
            file.write(f"{row}\n")

def get_data(api_key, country_codes, output_dir):
    for country_code in country_codes:
        country_data = [",".join(header)] + get_pages(api_key, country_code)
        write_to_file(output_dir, country_code, country_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--key_path', help='Path to the file containing the api key', default='api_key.txt')
    parser.add_argument('--country_code_path', help='Path to the file containing the list of country codes', default='country_codes.txt')
    parser.add_argument('--output_dir', help='Path to save the outputted files', default='output/')

    args = parser.parse_args()

    api_key, country_codes = setup(args.key_path, args.country_code_path)
    get_data(api_key, country_codes, args.output_dir)