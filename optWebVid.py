import subprocess
import os
from tkinter import filedialog, Tk, messagebox, simpledialog

def get_input_file():
    """Open a file dialog to let user select input video file."""
    root = Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select video file to compress",
        filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv *.flv *.wmv"), ("All files", "*.*")]
    )
    return file_path

def get_resolution_choice():
    """Let user choose between 720p or 1080p resolution."""
    root = Tk()
    root.withdraw()
    choice = simpledialog.askinteger(
        "Resolution Selection",
        "Choose output resolution:\n1 for 720p (1280x720)\n2 for 1080p (1920x1080)",
        minvalue=1,
        maxvalue=2,
        initialvalue=1
    )
    
    if choice == 1:
        return '1280:720', '720p'
    elif choice == 2:
        return '1920:1080', '1080p'
    else:
        return '1280:720', '720p'  # Default fallback

def compress_with_ffmpeg(input_path, output_path=None, crf=28, preset='medium', resolution='1280:720'):
    """
    Compress video using FFmpeg with resolution choice.
    
    Parameters:
    - input_path: Path to input video file
    - output_path: Path for output file
    - crf: Constant Rate Factor (18-28 for good balance)
    - preset: Encoding speed to compression ratio
    - resolution: Output resolution (either '1280:720' or '1920:1080')
    """
    
    # Set default output path if none provided
    if output_path is None:
        input_dir, input_filename = os.path.split(input_path)
        name, ext = os.path.splitext(input_filename)
        output_filename = f"{name}_compressed{ext}"
        output_path = os.path.join(input_dir, output_filename)
    
    # Use scale filter that maintains aspect ratio
    scale_filter = f"scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2"
    
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-c:v', 'libx264',
        '-crf', str(crf),
        '-preset', preset,
        '-vf', scale_filter,
        '-c:a', 'aac',
        '-b:a', '128k',
        output_path
    ]
    
    print(f"Compressing video to {resolution}...\nInput: {input_path}\nOutput: {output_path}")
    subprocess.run(cmd, check=True)
    
    # Print size comparison
    original_size = os.path.getsize(input_path) / (1024 * 1024)
    compressed_size = os.path.getsize(output_path) / (1024 * 1024)
    
    print(f"\nCompression complete!\nOriginal: {original_size:.2f}MB\nCompressed: {compressed_size:.2f}MB")
    print(f"Reduction: {original_size - compressed_size:.2f}MB ({((original_size - compressed_size)/original_size)*100:.1f}%)")

def main():
    print("Video Compression Tool")
    
    # Get input file
    input_path = get_input_file()
    if not input_path:  # User cancelled
        print("No file selected. Exiting.")
        return
    
    # Get resolution choice
    resolution, resolution_name = get_resolution_choice()
    print(f"Selected resolution: {resolution_name}")
    
    # Ask for output location
    root = Tk()
    root.withdraw()
    initial_dir, initial_file = os.path.split(input_path)
    name, ext = os.path.splitext(initial_file)
    default_output = os.path.join(initial_dir, f"{name}_{resolution_name}{ext}")
    
    output_path = filedialog.asksaveasfilename(
        title="Save compressed video as...",
        initialdir=initial_dir,
        initialfile=f"{name}_{resolution_name}{ext}",
        defaultextension=ext,
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    
    # If user cancels save dialog, use default location
    if not output_path:
        output_path = default_output
        print(f"No output location selected. Using default: {output_path}")
    
    # Compress the video
    compress_with_ffmpeg(input_path, output_path, resolution=resolution)

if __name__ == "__main__":
    main()