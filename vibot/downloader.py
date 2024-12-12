# for calling download api's and saving file
import requests, os

# For downloafing instagram reels
import instaloader

# For downloading TikTok reels
from tiktok_downloader import snaptik


# Download videos from instagram and tiktok with given url's
# ----------------------------------
def download_video(video_url, file_path):
    response = requests.get(video_url, stream=True)
    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)


def download_instagram_reel(url, save_dir="videos"):
    """
    Download an Instagram Reel with sound from the given URL.
    """
    L = instaloader.Instaloader()
    os.makedirs(save_dir, exist_ok=True)
    try:
        # Extract shortcode and fetch the post metadata
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Get the direct video URL
        video_url = post.video_url
        file_path = os.path.join(save_dir, f"{shortcode}.mp4")

        # Download the video with sound
        response = requests.get(video_url, stream=True)
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

        return file_path

    except Exception as e:
        print(f"Error downloading Instagram Reel: {e}")
        return None


def download_tiktok_video(url, save_dir="videos"):
    """
    Download an TikToks with sound from the given URL.
    """
    try:
        data = snaptik(url)
        video_url = data["download_links"][0]
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f"tiktok_{url.split('/')[-1]}.mp4")
        download_video(video_url, file_path)
        return file_path
    except:
        return None


def download_video_by_url(url):
    if "instagram.com" in url:
        return download_instagram_reel(url)
    elif "tiktok.com" in url:
        return download_tiktok_video(url)
    else:
        return None
# ----------------------------------