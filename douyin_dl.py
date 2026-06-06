#!/usr/bin/env python3
"""
Douyin / TikTok Watermark-Free Video Downloader
Usage: python douyin_dl.py <share_url>
"""

import re
import sys
import json
import os
import requests
from urllib.parse import unquote


def extract_video_id(share_url):
    """Extract video ID from various Douyin share URL formats."""
    patterns = [
        r'video/(\d+)',
        r'/(\d{17,})',
        r'(?:https?://)?(?:www\.)?douyin\.com/\S+/(\d+)',
        r'(?:https?://)?(?:www\.)?iesdouyin\.com/share/video/(\d+)',
    ]
    for p in patterns:
        m = re.search(p, share_url)
        if m:
            return m.group(1)
    return None


def download_video(video_id, output_dir="downloads"):
    """Download watermark-free video using public APIs."""
    os.makedirs(output_dir, exist_ok=True)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.douyin.com/",
    }
    
    # Try API endpoint
    api_urls = [
        f"https://www.iesdouyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}",
    ]
    
    for api_url in api_urls:
        try:
            resp = requests.get(api_url, headers=headers, timeout=10)
            data = resp.json()
            
            if "aweme_detail" in data:
                detail = data["aweme_detail"]
                # Get watermark-free video URL
                video_url = (
                    detail.get("video", {})
                    .get("play_addr", {})
                    .get("url_list", [None])[0]
                )
                if not video_url:
                    video_url = (
                        detail.get("video", {})
                        .get("bit_rate", [{}])[0]
                        .get("play_addr", {})
                        .get("url_list", [None])[0]
                    )
                
                if video_url:
                    # Remove watermark param
                    video_url = re.sub(r'[?&]watermark=[01]', '', video_url)
                    
                    print(f"[+] Downloading video {video_id}...")
                    video_resp = requests.get(video_url, headers=headers, timeout=30)
                    
                    filename = f"{output_dir}/douyin_{video_id}.mp4"
                    with open(filename, "wb") as f:
                        f.write(video_resp.content)
                    
                    print(f"[✓] Saved to: {filename}")
                    print(f"[✓] Size: {len(video_resp.content) / 1024:.1f} KB")
                    return filename
            
            elif "status_code" in data and data["status_code"] == 0:
                # Alternative response format
                pass
                
        except Exception as e:
            print(f"[-] API error: {e}")
            continue
    
    print("[-] Failed to download. Try another URL or check your share link.")
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    share_url = sys.argv[1].strip()
    print(f"[*] Processing: {share_url}")
    
    video_id = extract_video_id(share_url)
    if not video_id:
        print("[-] Could not extract video ID from URL")
        return
    
    print(f"[+] Video ID: {video_id}")
    download_video(video_id)


if __name__ == "__main__":
    main()
