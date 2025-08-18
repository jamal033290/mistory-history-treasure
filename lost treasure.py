import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyAvFafNFyNd9qIJLkuhnykHU_TbK0Tm-mk"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# ✅ List of broader keywords (fixed JSON block)
keywords = {
  "topic": "The Lost Treasure of the Knights Templar",
  "primary_keywords": [
    "Knights Templar",
    "Templar treasure",
    "lost treasure",
    "holy grail",
    "Templar secrets",
    "Templar history",
    "medieval mysteries",
    "crusades"
  ],
  "long_tail_keywords": [
    "where is the Knights Templar treasure",
    "evidence of Templar treasure locations",
    "Knights Templar and the Holy Grail myth",
    "Templar treasure in Scotland theories",
    "Oak Island Templar connections explained",
    "what happened to the Templars treasure 1307",
    "hidden symbols linked to Templar hoard",
    "Templar banking wealth and disappearance",
    "maps and clues to Templar treasure",
    "fact vs fiction Knights Templar gold"
  ],
  "search_intent_mix": {
    "informational": [
      "who were the Knights Templar",
      "what is the lost Templar treasure",
      "did the Templars protect the Holy Grail"
    ],
    "investigational": [
      "best documentaries on Knights Templar treasure",
      "archaeological finds linked to Templars",
      "historical sources for Templar wealth"
    ],
    "transactional": [
      "Knights Templar books for beginners",
      "Templar history documentaries to watch"
    ]
  }
}

# ✅ Merge all keywords into one flat list
all_keywords = (
    keywords["primary_keywords"]
    + keywords["long_tail_keywords"]
    + keywords["search_intent_mix"]["informational"]
    + keywords["search_intent_mix"]["investigational"]
    + keywords["search_intent_mix"]["transactional"]
)

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in all_keywords:
            st.write(f"Searching for keyword: {keyword}")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword: {keyword} due to missing video/channel data.")
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                st.warning(f"Failed to fetch video statistics for keyword: {keyword}")
                continue

            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                st.warning(f"Failed to fetch channel statistics for keyword: {keyword}")
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

