import os
import sys
from pathlib import Path

def split_zip_file(input_zip_path, output_dir, max_part_size=1024*1024*1024):  # 1GB in bytes
    """
    Split a ZIP file into smaller parts that can be reassembled later.
    
    Args:
        input_zip_path (Path): Path to the input ZIP file
        output_dir (Path): Directory where split files will be saved
        max_part_size (int): Maximum size of each part in bytes (default 1GB)
    """
    try:
        # Verify input file exists and is accessible
        if not input_zip_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_zip_path}")
        if not os.access(input_zip_path, os.R_OK):
            raise PermissionError(f"No read permission for file: {input_zip_path}")

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify output directory is writable
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"No write permission for directory: {output_dir}")

        # Base name for split files (without extension)
        base_name = output_dir / input_zip_path.stem
        
        print(f"\nSplitting {input_zip_path} into {max_part_size/(1024*1024):.0f}MB parts...")

        # Read the input file in binary mode
        with open(input_zip_path, 'rb') as f:
            part_num = 1
            while True:
                # Read up to max_part_size bytes
                chunk = f.read(max_part_size)
                if not chunk:
                    break  # End of file
                
                # Write the chunk to a new part file
                part_filename = f"{base_name}.zip.{part_num:03d}"
                with open(part_filename, 'wb') as part_file:
                    part_file.write(chunk)
                
                print(f"Created part {part_num}: {part_filename}")
                part_num += 1
        
        print(f"\nSuccessfully split {input_zip_path} into {part_num-1} parts.")
        print("To reassemble later, use one of these commands:")
        print(f'Windows: copy /B "{base_name}.zip.*" "{base_name}.zip"')
        print(f'Linux/macOS: cat "{base_name}.zip."* > "{base_name}.zip"')
        return True

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return False

def get_valid_input(prompt, is_file=False, expected_extension=None):
    """Helper function to get valid user input with error handling."""
    while True:
        try:
            user_input = input(prompt).strip()
            
            # Remove surrounding quotes if present
            user_input = user_input.strip('"').strip("'")
            
            if not user_input:
                raise ValueError("Path cannot be empty")
            
            path = Path(user_input).expanduser().absolute()
            
            if is_file:
                if not path.exists():
                    raise FileNotFoundError(f"Path does not exist: {path}")
                if expected_extension and path.suffix.lower() != expected_extension:
                    raise ValueError(f"File must have {expected_extension} extension")
                if not os.access(path, os.R_OK):
                    raise PermissionError(f"No read permission for file: {path}")
            else:  # Directory
                if not path.exists():
                    # Ask if user wants to create the directory
                    create = input(f"Directory {path} doesn't exist. Create it? [y/n]: ").lower()
                    if create == 'y':
                        path.mkdir(parents=True, exist_ok=True)
                    else:
                        continue
                if not os.access(path, os.W_OK):
                    raise PermissionError(f"No write permission for directory: {path}")
            
            return path
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            print("Please try again.\n")

def main():
    print("ZIP File Splitter - Split large ZIP files for FAT32 compatibility")
    print("---------------------------------------------------------------\n")
    
    # Ask for input file path
    input_path = get_valid_input(
        "Enter path to the ZIP file you want to split (drag & drop OK): ",
        is_file=True,
        expected_extension='.zip'
    )
    
    # Ask for output directory
    output_path = get_valid_input(
        "Enter output directory for split files (drag & drop OK): ",
        is_file=False
    )
    
    # Ask for split size (optional)
    while True:
        size_input = input("Enter maximum part size in GB (default=1): ").strip()
        if not size_input:
            max_size = 1024*1024*1024  # Default 1GB
            break
        try:
            max_size = float(size_input) * 1024*1024*1024
            if max_size <= 0:
                raise ValueError("Size must be positive")
            break
        except ValueError as e:
            print(f"Invalid size: {e}. Please enter a number like 1 or 1.5")
    
    # Split the file
    split_zip_file(input_path, output_path, max_size)

if __name__ == "__main__":
    main()

"""
To reassemble later, use one of these commands:
Windows: copy /B "/Users/prenticelathon/Downloads/Radiophobia-3-Ver.-1.18.zip.*" "/Users/prenticelathon/Downloads/Radiophobia-3-Ver.-1.18.zip"
Linux/macOS: cat "/Users/prenticelathon/Downloads/Radiophobia-3-Ver.-1.18.zip."* > "/Users/prenticelathon/Downloads/Radiophobia-3-Ver.-1.18.zip"
"""