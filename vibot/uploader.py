# for file handeling
import os

# for progress bar
from tqdm import tqdm

# for concurrent uploads
import aiohttp
import asyncio

# for importing config
import json

# Access constants from config file
# ----------------------------------
with open('config.json', 'r') as file:
    config_data = json.load(file)

TOKEN = config_data.get('TOKEN')
UPLOAD_URL_ENDPOINT = config_data.get('UPLOAD_URL_ENDPOINT')
CREATE_POST_ENDPOINT = config_data.get('CREATE_POST_ENDPOINT')
VIDEO_DIR = config_data.get('VIDEO_DIR')  # Directory to monitor
PROCESSED_FILES = set()  # Keep track of already processed files
CATEGORY_ID = config_data.get('CATEGORY_ID')
# ----------------------------------

# Set up Headers
# ----------------------------------
HEADERS = {
    "Flic-Token": TOKEN,
    "Content-Type": "application/json"
}


# ----------------------------------

# Handle video upload
# ----------------------------------
async def get_upload_url():
    """Fetch a pre-signed URL for video upload."""
    async with aiohttp.ClientSession() as session:
        async with session.get(UPLOAD_URL_ENDPOINT, headers=HEADERS) as response:
            if response.status == 200:
                data = await response.json()
                return data["url"], data["hash"]
            else:
                print(f"Failed to get upload URL: {response.status} - {await response.text()}")
                return None, None


async def upload_video(file_path, upload_url):
    """Upload the video file to the pre-signed URL."""
    async with aiohttp.ClientSession() as session:
        try:
            with open(file_path, "rb") as file:
                async with session.put(upload_url, data=file) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error uploading video: {e}")
            return False


async def create_post(title, video_hash, category_id):
    """Create a post using the hash from the upload."""
    payload = {
        "title": title,
        "hash": video_hash,
        "is_available_in_public_feed": False,
        "category_id": category_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(CREATE_POST_ENDPOINT, headers=HEADERS, json=payload) as response:
            if response.status == 200:
                return True
            else:
                print(f"Failed to create post: {response.status} - {await response.text()}")
                return False


# ----------------------------------

# Handle a new file discovered by monitor
# ----------------------------------
async def handle_new_file(file_path, title="test"):
    """Asynchronously handle a newly discovered file."""
    video_path = file_path
    video_title = title
    category_id = CATEGORY_ID  # Code 25 for super feed

    # Step 1: Fetch upload URL
    upload_url, video_hash = await get_upload_url()
    if not upload_url or not video_hash:
        print("Failed to fetch upload URL. Skipping.")
        return

    # Step 2: Upload the video
    if not await upload_video(video_path, upload_url):
        print("Failed to upload video. Skipping.")
        return

    # Step 3: Create the post
    if not await create_post(video_title, video_hash, category_id):
        print("Failed to create post. Skipping.")
        return

    os.remove(video_path)


# ----------------------------------

# Monitor the directory
# ----------------------------------
async def monitor_directory():
    """Monitor the /videos directory for new .mp4 files."""
    global PROCESSED_FILES

    while True:
        current_files = {file for file in os.listdir(VIDEO_DIR) if file.endswith('.mp4')}
        new_files = current_files - PROCESSED_FILES

        print(f"Monitoring {VIDEO_DIR} for new .mp4 files...")
        if new_files:

            # Create a progress bar for processing new files
            with tqdm(total=len(new_files), desc="Uploading files concurrently", unit="file") as pbar:
                tasks = []
                for file in new_files:
                    # Create a task for each file processing
                    task = asyncio.create_task(handle_new_file(os.path.join(VIDEO_DIR, file)))

                    # Add a callback to update the progress bar when the task is done
                    task.add_done_callback(lambda _: pbar.update(1))  # Update progress bar on task completion
                    tasks.append(task)

                # Wait for all tasks to complete
                await asyncio.gather(*tasks)

            PROCESSED_FILES = current_files

        await asyncio.sleep(5)  # Check every 5 seconds


# ----------------------------------

if __name__ == "__main__":
    asyncio.run(monitor_directory())