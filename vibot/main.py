# for concurrent uploads
import asyncio

# importing uploader file
import uploader

# importing downloader file
import downloader

# for progress bar
from tqdm import tqdm


# Main function
# ----------------------------------
async def main(links):
    # Download videos
    for url in tqdm(links, desc="Downloading Videos", unit="video", leave=False):
        downloader.download_video_by_url(url)

    # Monitor directory for uploads
    await uploader.monitor_directory()


# ----------------------------------

# Store links the way you wanted
# Sample links
links = [
    "https://www.instagram.com/reels/C_Lahgkt2sh/",
    "https://www.instagram.com/reels/DBJpTjko4eI/",
    "https://www.instagram.com/reels/DBRo1Mooo6E/"
]

if __name__ == "__main__":
    asyncio.run(main(links))