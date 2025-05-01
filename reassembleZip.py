import os
import glob
from pathlib import Path

def natural_sort_key(s):
    import re
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split('([0-9]+)', str(s))]

def reassemble_files():
    print("\nFiles in directory:")
    for f in Path().iterdir():
        print(f"  - {f.name}")
    
    # Find all numbered files automatically
    all_files = sorted(Path().glob("*.*[0-9][0-9][0-9]"), key=natural_sort_key)
    
    if not all_files:
        print("\nERROR: No split files found (looking for files ending in .001, .002 etc.)")
        return
        
    print("\nDetected possible split files:")
    for f in all_files[:5]:  # Show first 5 to avoid flooding
        print(f"  - {f.name}")
    if len(all_files) > 5:
        print(f"  (...and {len(all_files)-5} more)")
    
    base_name = input("\nEnter the COMMON PART before numbering (e.g., 'file.zip'): ").strip()
    output_file = input("Enter output filename (e.g., 'restored.zip'): ").strip()
    
    # Handle special characters in glob pattern
    parts = sorted([f for f in all_files if str(f).startswith(base_name)], key=natural_sort_key)
    
    if not parts:
        print(f"\nERROR: No files matched '{base_name}.*'")
        print("Try entering just the part BEFORE .001 (without the numbers)")
        return
    
    print(f"\nReassembling {len(parts)} files...")
    with open(output_file, 'wb') as out_file:
        for part in parts:
            print(f"Adding {part.name}...")
            with open(part, 'rb') as f:
                out_file.write(f.read())
    
    print(f"\nSUCCESS! Created {output_file}")
    print(f"Size: {os.path.getsize(output_file)/1024/1024:.2f} MB")

if __name__ == "__main__":
    print("=== SPECIAL CHARACTER-FRIENDLY REASSEMBLER ===")
    reassemble_files()