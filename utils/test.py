from listennotes_api import search_podcast, get_episodes, get_audio_url

print("Searching podcasts for: web development")
podcasts = search_podcast("web development")
if podcasts:
    first_podcast = podcasts[0]
    print("🎙️ Found:", first_podcast["title_original"])
    episodes = get_episodes(first_podcast["id"])
    if episodes:
        print("🎧 First episode:", episodes[0]["title"])
        audio_url, title = get_audio_url(episodes[0]["id"])
        print("🔗 Audio URL:", audio_url)
