import google.generativeai as genai
import requests
from googleapiclient.discovery import build

YOUTUBE_API_KEY = "AIzaSyBaGDKbkgXSOTePejGzvD30-jrR8OWMAFc"

GEMINI_API_KEY = "AIzaSyAaIteyMqjHH78E-1hoyy7nsVTPL27c1xI"

genai.configure(api_key=GEMINI_API_KEY)

def search_youtube(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=10,  
        videoDuration="medium", 
        publishedAfter="2024-03-17T00:00:00Z"  
    ).execute()

    results = []
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        results.append({"title": title, "url": url})

    return results

def analyze_titles(video_titles):
    """Use Gemini AI to find the best video based on title relevance."""
    prompt = f"Find the most relevant video title from this list for a user query:\n{video_titles}"
    
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    
    return response.text.strip() if response else "No recommendation found."

query = input("Enter your search query: ")
videos = search_youtube(query)

print("\n🔹 Top 10 YouTube Videos:")
for i, video in enumerate(videos, start=1):
    print(f"{i}. {video['title']} - {video['url']}")

titles = [video["title"] for video in videos]
best_video = analyze_titles(titles)

print("\n✅ Best Video Recommendation:", best_video)
