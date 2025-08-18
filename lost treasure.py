import streamlit as st
import requests
from datetime import datetime, timedelta
import isodate  # 👈 duration parse karne ke liye zaroori hai

# -------------------------
# YouTube API Settings
# -------------------------
API_KEY = "AIzaSyAvFafNFyNd9qIJLkuhnykHU_TbK0Tm-mk"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# -------------------------
# Streamlit UI
# -------------------------
st.title("YouTube Viral Topics Tool (5+ min Videos Only)")

days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

keywords = [
     "Knights Templar",
        "Templar treasure",
        "lost treasure",
        "holy grail",
        "Templar secrets",
        "crusades history",
        "medieval mysteries",
        "hidden gold",
        "Oak Island treasure",
        "Templar artifacts",
        "ancient relics",
        "mystery of 1307",
        "Templar banking wealth",
        "lost relics of Jerusalem",
        "buried Templar treasure",
        "forbidden Templar knowledge",
        "maps to treasure",
        "Templar conspiracy theories",
        "secret societies Templar",
        "Templar treasure legends"
]

# -------------------------
# Helper Function
# -------------------------
def parse_duration(duration_str):
    """Convert ISO8601 duration string to seconds"""
    try:
        return int(isodate.parse_duration(duration_str).total_seconds())
    except:
        return 0

# -------------------------
# Fetch Data
# -------------------------
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"🔎 Searching for keyword: **{keyword}**")

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
            video_ids = [v["id"]["videoId"] for v in videos if "id" in v and "videoId" in v["id"]]
            channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v and "channelId" in v["snippet"]]

            if not video_ids or not channel_ids:
                continue

            # Video Stats + Duration
            stats_params = {"part": "statistics,contentDetails", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                continue

            # Channel Stats
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                continue

            # Collect Results
            for video, stat, channel in zip(videos, stats_data["items"], channel_data["items"]):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                duration_seconds = parse_duration(stat["contentDetails"]["duration"])

                # ✅ Only 5+ minutes videos + small channels
                if subs < 3000 and duration_seconds >= 300:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs,
                        "Duration (min)": round(duration_seconds / 60, 2)
                    })

        # -------------------------
        # Show Results
        # -------------------------
        if all_results:
            st.success(f"✅ Found {len(all_results)} results across all keywords!")
            for result in all_results:
                st.markdown(
                    f"**🎬 Title:** {result['Title']}  \n"
                    f"**📝 Description:** {result['Description']}  \n"
                    f"**🔗 URL:** [Watch Video]({result['URL']})  \n"
                    f"**👀 Views:** {result['Views']}  \n"
                    f"**📊 Subscribers:** {result['Subscribers']}  \n"
                    f"**⏱ Duration:** {result['Duration (min)']} minutes"
                )
                st.write("---")
        else:
            st.warning("No 5+ minute videos found with <3000 subs in this range.")

    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

