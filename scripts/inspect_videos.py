import cv2
import os
import glob
import json

video_dir = os.path.join(os.getcwd(), "sample videos")
videos = glob.glob(os.path.join(video_dir, "*.mp4"))

print(f"Found {len(videos)} videos in {video_dir}:\n", flush=True)

out_dir = os.path.join(os.getcwd(), "backend", "app", "static", "thumbnails")
os.makedirs(out_dir, exist_ok=True)

video_info = []

for v_path in videos:
    cap = cv2.VideoCapture(v_path)
    if not cap.isOpened():
        print(f"Could not open {v_path}", flush=True)
        continue

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = frame_count / fps if fps > 0 else 0

    base_name = os.path.splitext(os.path.basename(v_path))[0]
    
    # Save a frame from 25%, 50%, 75%
    saved_frames = []
    for pct in [0.25, 0.50, 0.75]:
        target_frame = int(frame_count * pct)
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        if ret:
            frame_filename = f"{base_name}_frame_{int(pct*100)}.jpg"
            save_path = os.path.join(out_dir, frame_filename)
            # Resize thumbnail if 4K to prevent huge images
            thumb = cv2.resize(frame, (1280, 720)) if width > 1920 else frame
            cv2.imwrite(save_path, thumb)
            saved_frames.append(frame_filename)

    cap.release()

    info = {
        "filename": os.path.basename(v_path),
        "resolution": f"{width}x{height}",
        "fps": round(fps, 1),
        "frame_count": frame_count,
        "duration_sec": round(duration_sec, 1),
        "thumbnails": saved_frames
    }
    video_info.append(info)
    print(f"File: {info['filename']}")
    print(f"  Resolution: {info['resolution']} @ {info['fps']} fps")
    print(f"  Frames: {info['frame_count']} ({info['duration_sec']}s)")
    print(f"  Thumbnails saved: {saved_frames}\n", flush=True)

with open("scratch/video_inspection.json", "w") as f:
    json.dump(video_info, f, indent=2)
