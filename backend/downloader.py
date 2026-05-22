import yt_dlp
import os
import uuid


def get_video_info(url):
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get("formats", [])
        video_options = []
        seen_qualities = set()

        for f in formats:
            height = f.get("height")
            ext = f.get("ext")
            filesize = f.get("filesize") or f.get("filesize_approx") or 0
            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")

            if height and ext == "mp4" and vcodec != "none" and acodec != "none":
                quality_label = f"{height}p"
                if quality_label not in seen_qualities:
                    seen_qualities.add(quality_label)
                    size_mb = round(filesize / (1024 * 1024), 2) if filesize else 0
                    video_options.append({
                        "format": "MP4",
                        "quality": quality_label,
                        "size_mb": size_mb,
                        "format_id": f.get("format_id")
                    })

        video_options.sort(key=lambda x: int(x["quality"].replace("p", "")))

        audio_options = []
        for f in formats:
            ext = f.get("ext")
            acodec = f.get("acodec", "none")
            vcodec = f.get("vcodec", "none")
            filesize = f.get("filesize") or f.get("filesize_approx") or 0

            if ext == "m4a" and acodec != "none" and vcodec == "none":
                abr = f.get("abr", 0)
                size_mb = round(filesize / (1024 * 1024), 2) if filesize else 0
                if abr and abr >= 128:
                    audio_options.append({
                        "format": "MP3",
                        "quality": "Classic MP3",
                        "size_mb": size_mb,
                        "format_id": f.get("format_id")
                    })
                else:
                    audio_options.append({
                        "format": "MP3",
                        "quality": "Fast",
                        "size_mb": size_mb,
                        "format_id": f.get("format_id")
                    })

        audio_options = audio_options[:2]

        return {
            "title": info.get("title", "Video"),
            "thumbnail": info.get("thumbnail", ""),
            "platform": info.get("extractor_key", "Unknown"),
            "duration": info.get("duration", 0),
            "video_formats": video_options,
            "audio_formats": audio_options
        }

    except Exception as e:
        return {"error": str(e)}


def download_video(url, format_type, quality, download_folder):
    try:
        unique_id = str(uuid.uuid4())[:8]

        if format_type == "mp3":
            output_template = os.path.join(download_folder, f"{unique_id}.%(ext)s")
            ydl_opts = {
                'cookiefile': 'cookies.txt',
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "quiet": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
            expected_ext = "mp3"
        else:
            quality_map = {
                "480": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
                "720": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
                "1080": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
            }
            fmt = quality_map.get(quality, quality_map["720"])
            output_template = os.path.join(download_folder, f"{unique_id}.%(ext)s")
            ydl_opts = {
                "format": fmt,
                "outtmpl": output_template,
                "quiet": True,
                "merge_output_format": "mp4",
            }
            expected_ext = "mp4"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "video")

        safe_title = "".join(c for c in title if c.isalnum() or c in " -_")[:50]
        filename = f"{safe_title}.{expected_ext}"
        downloaded_file = os.path.join(download_folder, f"{unique_id}.{expected_ext}")

        if not os.path.exists(downloaded_file):
            for f in os.listdir(download_folder):
                if f.startswith(unique_id):
                    downloaded_file = os.path.join(download_folder, f)
                    break

        return {
            "filepath": downloaded_file,
            "filename": filename
        }

    except Exception as e:
        return {"error": str(e)}