#!/bin/bash

# Script to find duplicate .txt files in data_text/ and delete duplicates
# along with their corresponding images in data_images/

set -e

TEXT_DIR="data_text"
IMAGE_DIR="data_images"

# Check if directories exist
if [ ! -d "$TEXT_DIR" ]; then
    echo "Error: Directory $TEXT_DIR does not exist"
    exit 1
fi

if [ ! -d "$IMAGE_DIR" ]; then
    echo "Warning: Directory $IMAGE_DIR does not exist"
    echo "Will only process text files"
fi

# Check if fdupes is installed
if ! command -v fdupes &> /dev/null; then
    echo "Error: fdupes is not installed"
    echo "Install it with: sudo apt-get install fdupes (Debian/Ubuntu)"
    echo "or: brew install fdupes (macOS)"
    exit 1
fi

echo "Finding duplicate .txt files in $TEXT_DIR..."
echo "============================================"

# Find duplicates, keeping first occurrence of each
# fdupes outputs groups of duplicates separated by blank lines
duplicates=$(fdupes -r "$TEXT_DIR" | grep "\.txt$")

if [ -z "$duplicates" ]; then
    echo "No duplicate .txt files found"
    exit 0
fi

# Process duplicate groups
current_group=()
while IFS= read -r line; do
    if [ -z "$line" ]; then
        # Empty line means end of duplicate group
        if [ ${#current_group[@]} -gt 1 ]; then
            echo ""
            echo "Duplicate group found (${#current_group[@]} files):"
            echo "  Keeping: ${current_group[0]}"
            
            # Delete all duplicates except the first one
            for ((i=1; i<${#current_group[@]}; i++)); do
                dup_file="${current_group[$i]}"
                echo "  Deleting: $dup_file"
                rm -f "$dup_file"
                
                # Extract filename without path and extension
                basename=$(basename "$dup_file" .txt)
                img_file="$IMAGE_DIR/${basename}.jpg"
                
                # Delete corresponding image if it exists
                if [ -f "$img_file" ]; then
                    echo "  Deleting: $img_file"
                    rm -f "$img_file"
                else
                    echo "  (No corresponding image: $img_file)"
                fi
            done
        fi
        current_group=()
    else
        current_group+=("$line")
    fi
done <<< "$duplicates"

# Process last group if exists
if [ ${#current_group[@]} -gt 1 ]; then
    echo ""
    echo "Duplicate group found (${#current_group[@]} files):"
    echo "  Keeping: ${current_group[0]}"
    
    for ((i=1; i<${#current_group[@]}; i++)); do
        dup_file="${current_group[$i]}"
        echo "  Deleting: $dup_file"
        rm -f "$dup_file"
        
        basename=$(basename "$dup_file" .txt)
        img_file="$IMAGE_DIR/${basename}.jpg"
        
        if [ -f "$img_file" ]; then
            echo "  Deleting: $img_file"
            rm -f "$img_file"
        else
            echo "  (No corresponding image: $img_file)"
        fi
    done
fi

echo ""
echo "============================================"
echo "Cleanup complete!"
