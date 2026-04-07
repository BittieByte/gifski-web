import os
import uuid
import glob
import subprocess
from flask import request, render_template, send_file
from app import app, UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------- Helpers ----------------------
def generate_file_paths(filename):
    """Generate unique paths for input, output, and temp frames"""
    file_id = str(uuid.uuid4())
    return {
        "input": os.path.join(UPLOAD_FOLDER, f"{file_id}_{filename}"),
        "output": os.path.join(UPLOAD_FOLDER, f"{file_id}_optimized.gif"),
        "temp_frames": os.path.join(UPLOAD_FOLDER, f"{file_id}_frames")
    }


def save_uploaded_file(uploaded_file, path):
    uploaded_file.save(path)


def extract_frames(input_path, temp_frames_dir):
    """Extract frames from video"""
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
    """Run gifski with all relevant options"""
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

    # Append all frames last
    cmd += frame_files

    print("Running command:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def cleanup_temp_frames(temp_frames_dir):
    if os.path.isdir(temp_frames_dir):
        for f in os.listdir(temp_frames_dir):
            os.remove(os.path.join(temp_frames_dir, f))
        os.rmdir(temp_frames_dir)


def calculate_size_reduction(orig_path, output_path):
    orig_size = os.path.getsize(orig_path) / 1024
    new_size = os.path.getsize(output_path) / 1024
    reduction = round((orig_size - new_size) / orig_size * 100, 2)
    return {"orig_size": round(orig_size, 2), "new_size": round(new_size, 2), "reduction": reduction}


def sanitize_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


# ---------------------- Routes ----------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files['file']
    paths = generate_file_paths(uploaded_file.filename)
    save_uploaded_file(uploaded_file, paths["input"])

    # Collect all Gifski options from form
    quality = sanitize_int(request.form.get("quality")) or 90
    fps = sanitize_int(request.form.get("fps"))
    width = sanitize_int(request.form.get("width"))
    height = sanitize_int(request.form.get("height"))
    fast = bool(request.form.get("fast"))
    extra = bool(request.form.get("extra"))
    motion_quality = sanitize_int(request.form.get("motion_quality"))
    lossy_quality = sanitize_int(request.form.get("lossy_quality"))
    repeat = sanitize_int(request.form.get("repeat"))
    fixed_color = request.form.get("fixed_color") or None
    matte = request.form.get("matte") or None
    no_sort = bool(request.form.get("no_sort"))

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

    sizes = calculate_size_reduction(paths["input"], paths["output"])
    gif_url = f"/uploads/{os.path.basename(paths['output'])}"

    return render_template(
        "result.html",
        orig_size=sizes["orig_size"],
        new_size=sizes["new_size"],
        reduction=sizes["reduction"],
        gif_url=gif_url
    )


@app.route("/uploads/<filename>")
def serve_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))
