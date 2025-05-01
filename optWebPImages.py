import os
from PIL import Image
import sys

def clean_path(path):
    """Remove surrounding quotes and handle escaped spaces."""
    return path.strip().strip('"\'')

def resize_image(input_path, output_path, target_size_kb=50, output_format='webp'):
    """Resize image to be under target size (in KB)."""
    try:
        with Image.open(input_path) as img:
            if img.mode == 'RGBA' and output_format.lower() in ('jpg', 'jpeg'):
                img = img.convert('RGB')
            
            quality = 90
            min_quality = 10
            step = 5
            
            while quality >= min_quality:
                save_args = {
                    'quality': quality,
                    'method': 6 if output_format == 'webp' else 0
                }
                img.save(output_path, output_format.upper(), **save_args)
                
                file_size_kb = os.path.getsize(output_path) / 1024
                if file_size_kb <= target_size_kb:
                    print(f"✅ Success! Output: {output_path} ({file_size_kb:.1f} KB)")
                    return True
                quality -= step
            
            print(f"⚠️ Could not reduce under {target_size_kb} KB (minimum quality reached).")
            return False
    except Exception as e:
        print(f"❌ Processing Error: {str(e)}")
        return False

def main():
    print("=== Image Resizer (Under 50KB) ===")
    
    # Input handling with path cleaning
    raw_input = input("📂 Enter image path: ")
    input_path = clean_path(raw_input)
    
    if not os.path.exists(input_path):
        print(f"❌ File not found. Please check these possible issues:")
        print(f"1. Path with spaces: Try dragging the file into terminal instead of typing")
        print(f"2. Actual path: {os.path.abspath(input_path)}")
        print(f"3. File permissions: Try moving the file to your Desktop")
        sys.exit(1)
    
    # Format selection
    output_format = input("🔤 Choose format (W=WebP, A=AVIF): ").strip().lower()
    if output_format not in ('w', 'a'):
        print("❌ Invalid choice. Use 'W' or 'A'.")
        sys.exit(1)
    output_ext = 'webp' if output_format == 'w' else 'avif'
    
    # Output path handling
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    default_output = os.path.join(os.path.dirname(input_path), f"{base_name}_50kb.{output_ext}")
    user_output = clean_path(input(f"💾 Save as (default: {default_output}): "))
    output_path = user_output if user_output else default_output
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    # Process image
    if not resize_image(input_path, output_path, 50, output_ext):
        sys.exit(1)

if __name__ == "__main__":
    main()