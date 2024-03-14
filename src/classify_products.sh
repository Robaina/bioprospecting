#!/bin/bash

# Initialize default values
input_dir="" # (outside Docker)
general_output_dir="" # (outside Docker)

# Function to display help
usage() {
    echo "Usage: $0 [-w work_directory] [-i input_directory] [-o output_directory]"
    exit 1
}

# Parse command-line options
while getopts 'w:i:o:' flag; do
    case "${flag}" in
        i) input_dir="${OPTARG}" ;;
        o) general_output_dir="${OPTARG}" ;;
        *) usage ;;
    esac
done

# Check if input and output directories are provided
if [[ -z "$input_dir" ]] || [[ -z "$general_output_dir" ]]; then
    echo "Input and output directories must be provided."
    usage
fi

# Convert input and output directories to absolute paths
input_dir=$(realpath "$input_dir")
general_output_dir=$(realpath "$general_output_dir")

# Create the general output directory if it doesn't exist
mkdir -p "$general_output_dir"

# Loop through all .gbk files in the specified directory
for gbk_file in "$input_dir/antiSMASH_output/"*.gbk; do
    # Extract the base name without the extension
    base_name=$(basename "$gbk_file" .gbk)

    # Corresponding .txt file in the RGI_output directory on the host
    txt_file_host="$input_dir/RGI_output/${base_name}.txt"

    # Check if the .txt file exists on the host
    if [ -f "$txt_file_host" ]; then
        docker run \
          --volume "$input_dir:/src/input" \
          --volume "$general_output_dir:/src/output" \
          ghcr.io/new-atlantis-labs/walker_bgc_bioactivity:latest \
          "/src/input/antiSMASH_output/${base_name}.gbk" \
          "/src/input/RGI_output/${base_name}.txt" \
          --output "/src/output/" \
          --seed 42 \
          --no_SSN \
          --antismash_version 5 \
          --rgi_version 3
    else
        echo "Warning: No matching txt file for $gbk_file"
    fi
done