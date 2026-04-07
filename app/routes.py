import os
import uuid
import glob
import subprocess
import re
from flask import request, render_template, send_file, abort
from app import app, UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------- Sanitizers ----------------------
def sanitize_int(val, min_val=None, max_val=None):
    """Convert to int and clamp to optional bounds. Return None if invalid."""
    try:
        v = int(val)
        if min_val is not None and v < min_val:
            return None
        if max_val is not None and v > max_val:
            return None
        return v
    except (TypeError, ValueError):
        return None

def sanitize_color(val):
    """Allow only valid hex colors: RRGGBB or #RRGGBB"""
    if not val:
        return None
    val = val.strip()
    if re.fullmatch(r"#?[0-9a-fA-F]{6}", val):
        return val if val.startswith("#") else f"#{val}"
    return None

def sanitize_bool(val):
    """Convert checkbox input to boolean"""
    return bool(val)

# ---------------------- Helpers ----------------------
def generate_file_paths(filename):
    file_id = str(uuid.uuid4())
    return {
        "input": os.path.join(UPLOAD_FOLDER, f"{file_id}_{filename}"),
        "output": os.path.join(UPLOAD_FOLDER, f"{file_id}_optimized.gif"),
        "temp_frames": os.path.join(UPLOAD_FOLDER, f"{file_id}_frames")
    }

def save_uploaded_file(uploaded_file, path):
    uploaded_file.save(path)

def get_media_dimensions(input_path):
    """Get width and height of a video or GIF using ffprobe."""
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        input_path
    ], capture_output=True, text=True, check=True)

    parts = result.stdout.strip().split(",")
    if len(parts) == 2:
        return int(parts[0]), int(parts[1])
    raise RuntimeError("Could not determine media dimensions.")

def extract_frames(input_path, temp_frames_dir):
    """Extract frames from video using ffmpeg"""
    os.makedirs(temp_frames_dir, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-i", input_path, "-vsync", "0",
        os.path.join(temp_frames_dir, "%05d.png")
    ], check=True)
    frames = sorted(glob.glob(os.path.join(temp_frames_dir, "*.png")))
    if not frames:
        raise RuntimeError("No frames extracted from video.")
    return frames

def optimize_gif(
    frame_files, output_path, quality=90, fps=None,
    width=None, height=None, fast=False, extra=False,
    motion_quality=None, lossy_quality=None, repeat=None,
    fixed_color=None, matte=None, no_sort=False
):
    """Run gifski with all sanitized options"""
    frame_files = [os.path.abspath(f) for f in frame_files]
    output_path = os.path.abspath(output_path)

    cmd = ["gifski", "--output", output_path, "--quality", str(quality)]

    if fps: cmd += ["--fps", str(fps)]
    if width: cmd += ["--width", str(width)]
    if height: cmd += ["--height", str(height)]
    if fast: cmd += ["--fast"]
    if extra: cmd += ["--extra"]
    if motion_quality: cmd += ["--motion-quality", str(motion_quality)]
    if lossy_quality: cmd += ["--lossy-quality", str(lossy_quality)]
    if repeat is not None: cmd += ["--repeat", str(repeat)]
    if fixed_color: cmd += ["--fixed-color", fixed_color]
    if matte: cmd += ["--matte", matte]
    if no_sort: cmd += ["--no-sort"]

    cmd += frame_files

    print("Running command:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def cleanup_temp_frames(temp_frames_dir):
    if os.path.isdir(temp_frames_dir):
        for f in os.listdir(temp_frames_dir):
            os.remove(os.path.join(temp_frames_dir, f))
        os.rmdir(temp_frames_dir)

def calculate_size_reduction(orig_path, output_path):
    orig_size_kb = os.path.getsize(orig_path) / 1024
    new_size_kb = os.path.getsize(output_path) / 1024
    reduction = round((orig_size_kb - new_size_kb) / orig_size_kb * 100, 2)
    return {"orig_size": round(orig_size_kb, 2), "new_size": round(new_size_kb, 2), "reduction": reduction}

def human_readable_size(filepath):
    """Return human-readable file size with 2 decimal points."""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

# ---------------------- Routes ----------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files['file']
    paths = generate_file_paths(uploaded_file.filename)
    save_uploaded_file(uploaded_file, paths["input"])

    # ---------------------- Sanitize inputs ----------------------
    quality = sanitize_int(request.form.get("quality"), 1, 100) or 90
    fps = sanitize_int(request.form.get("fps"), 1)
    width = sanitize_int(request.form.get("width"), 1)
    height = sanitize_int(request.form.get("height"), 1)
    fast = sanitize_bool(request.form.get("fast"))
    extra = sanitize_bool(request.form.get("extra"))
    motion_quality = sanitize_int(request.form.get("motion_quality"), 1, 100)
    lossy_quality = sanitize_int(request.form.get("lossy_quality"), 1, 100)
    repeat = sanitize_int(request.form.get("repeat"))
    fixed_color = sanitize_color(request.form.get("fixed_color"))
    matte = sanitize_color(request.form.get("matte"))
    no_sort = sanitize_bool(request.form.get("no_sort"))

    # ---------------------- Dimension fallback ----------------------
    if not width and not height:
        # Neither specified — use original dimensions to prevent gifski's default downscale
        orig_w, orig_h = get_media_dimensions(paths["input"])
        width = orig_w
        height = orig_h
    # If only one is specified, leave the other as None so gifski scales proportionally

    try:
        is_gif = uploaded_file.filename.lower().endswith(".gif")
        frame_files = [paths["input"]] if is_gif else extract_frames(paths["input"], paths["temp_frames"])

        optimize_gif(
            frame_files,
            paths["output"],
            quality=quality,
            fps=fps,
            width=width,
            height=height,
            fast=fast,
            extra=extra,
            motion_quality=motion_quality,
            lossy_quality=lossy_quality,
            repeat=repeat,
            fixed_color=fixed_color,
            matte=matte,
            no_sort=no_sort
        )

    finally:
        cleanup_temp_frames(paths["temp_frames"])

    # ---------------------- File sizes ----------------------
    orig_size = human_readable_size(paths["input"])
    new_size = human_readable_size(paths["output"])
    sizes = calculate_size_reduction(paths["input"], paths["output"])
    gif_url = f"/uploads/{os.path.basename(paths['output'])}"

    return render_template(
        "result.html",
        orig_size=orig_size,
        new_size=new_size,
        reduction=sizes["reduction"],
        gif_url=gif_url
    )

@app.route("/uploads/<filename>")
def serve_file(filename):
    safe_path = os.path.join(UPLOAD_FOLDER, os.path.basename(filename))
    if not os.path.exists(safe_path):
        abort(404)
    return send_file(safe_path)
