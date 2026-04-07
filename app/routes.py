import os, uuid, glob, subprocess
from flask import request, render_template, send_file
from app import app, UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_file_paths(filename): file_id=str(uuid.uuid4()); return {"input": os.path.join(UPLOAD_FOLDER,f"{file_id}_{filename}"), "output": os.path.join(UPLOAD_FOLDER,f"{file_id}_optimized.gif"), "temp_frames": os.path.join(UPLOAD_FOLDER,f"{file_id}_frames")}
def save_uploaded_file(uploaded_file,path): uploaded_file.save(path)
def extract_frames(input_path,temp_frames_dir): os.makedirs(temp_frames_dir,exist_ok=True); subprocess.run(["ffmpeg","-i",input_path,"-vsync","0",os.path.join(temp_frames_dir,"%05d.png")],check=True); frames=sorted(glob.glob(os.path.join(temp_frames_dir,"*.png"))); return frames if frames else RuntimeError("No frames extracted from video.")
def optimize_gif(frame_files,output_path,quality,fps=None,width=None,height=None): frame_files=[os.path.abspath(f) for f in frame_files]; output_path=os.path.abspath(output_path); cmd=["gifski","--output",output_path,"--quality",str(quality)];
 if fps: cmd+=["--fps",str(fps)]; if width: cmd+=["--width",str(width)]; if height: cmd+=["--height",str(height)]; cmd+=frame_files; subprocess.run(cmd,check=True)
def cleanup_temp_frames(temp_frames_dir): 
    if os.path.isdir(temp_frames_dir): 
        for f in os.listdir(temp_frames_dir): os.remove(os.path.join(temp_frames_dir,f)); os.rmdir(temp_frames_dir)
def calculate_size_reduction(orig_path,output_path):
    orig_size=os.path.getsize(orig_path)/1024; new_size=os.path.getsize(output_path)/1024; reduction=round((orig_size-new_size)/orig_size*100,2); return {"orig_size":round(orig_size,2),"new_size":round(new_size,2),"reduction":reduction}

@app.route("/",methods=["GET"])
def index(): return render_template("index.html")

@app.route("/upload",methods=["POST"])
def upload():
    uploaded_file=request.files['file']
    def sanitize_int(val): 
        try: return int(val)
        except: return None
    quality=sanitize_int(request.form.get("quality")) or 80
    fps=sanitize_int(request.form.get("fps"))
    width=sanitize_int(request.form.get("width"))
    height=sanitize_int(request.form.get("height"))
    paths=generate_file_paths(uploaded_file.filename)
    save_uploaded_file(uploaded_file,paths["input"])
    try:
        is_gif=uploaded_file.filename.lower().endswith(".gif")
        frame_files=[paths["input"]] if is_gif else extract_frames(paths["input"],paths["temp_frames"])
        optimize_gif(frame_files,paths["output"],quality,fps,width,height)
    finally: cleanup_temp_frames(paths["temp_frames"])
    sizes=calculate_size_reduction(paths["input"],paths["output"])
    gif_url=f"/uploads/{os.path.basename(paths['output'])}"
    return render_template("result.html",orig_size=sizes["orig_size"],new_size=sizes["new_size"],reduction=sizes["reduction"],gif_url=gif_url)

@app.route("/uploads/<filename>")
def serve_file(filename): return send_file(os.path.join(UPLOAD_FOLDER,filename))
