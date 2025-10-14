<font size="5">

# RhizoVision Explorer CLI Usage Examples

The command line interface supports extensive configuration options for root analysis and batch processing. It can be run by invoking in a shell prompt or invoked from within a python script for sutomated analysis.

## Basic Usage

```bash
# Process a single image with default settings
./rv image.jpg

# Process all images in a directory
./rv /path/to/images/

# Process directory recursively with verbose output
./rv -r -v /path/to/images/
```

## Input and Output Options
```bash
# Specify ROI annotation CSV file
./rv --roipath rois.csv image.jpg

# Specify metadata CSV file (if implemented)
./rv --metafile meta.csv image.jpg

# Specify output CSV file
./rv -o results.csv image.jpg

# Specify output directory for processed images
./rv -op processed_images/ image.jpg

# Overwrite output file instead of appending
./rv -na image.jpg
```

## General Options
```bash
# Show help
./rv -h

# Show version/license/credits
./rv --version
./rv --license
./rv --credits
```

## Root Analysis Options
```bash
# Set root type (0=whole root, 1=broken roots)
./rv -rt 0 image.jpg

# Set segmentation threshold
./rv -t 180 image.jpg

# Invert image colors before processing
./rv -i image.jpg
```

## Filtering Options
```bash
# Keep only the largest component
./rv -kl image.jpg

# Filter background noise components
./rv --bgnoise image.jpg

# Filter foreground noise components
./rv --fgnoise image.jpg

# Set max background component size
./rv --bgnoise --bgsize 0.5 image.jpg

# Set max foreground component size
./rv --fgnoise --fgsize 0.5 image.jpg
```

## Smoothing and Pruning Options
```bash
# Enable contour smoothing
./rv --smooth image.jpg

# Set smoothing threshold
./rv -s --smooththreshold 1.5 image.jpg

# Enable root pruning
./rv --prune image.jpg

# Set root pruning threshold
./rv --prune --prunethreshold 2 image.jpg
```

## Unit Conversion and Analysis Options
```bash
# Enable pixel to physical unit conversion
./rv --convert image.jpg

# Set conversion factor
./rv --factordpi 0.1 image.jpg

# Use pixels per mm instead of DPI
./rv --factorpixels image.jpg

# Set diameter ranges (comma-separated)
./rv --dranges 1.0,3.0,6.0 image.jpg
```

## Output Image Options
```bash
# Save segmented images
./rv --segment image.jpg

# Save processed feature images
./rv --feature image.jpg

# Set suffix for segmented images
./rv --ssuffix _seg image.jpg

# Set suffix for processed images
./rv --fsuffix _features image.jpg
```

## Complete Example
```bash
./rv -r -v -rt 0 -t 140 --smooth --pixelconv --convfactor 0.05 \
    --dranges 1.0,2.5,5.0 --saveproc -o analysis.csv /path/to/images/
```

## Batch Processing a Whole Folder from Python (Single Invocation)

We can invoke rv from within a python script. This allows us to capture output and perform checks if any images failed to process and directly tie it to downstream analysis of features. When invoking rv by passing a directory, the rv program handles image file discovery and all files within a directory is analyzed. The images are analyzed recursively if '-r' switch is specified.


```python
import subprocess
import sys
import pandas as pd

# Choose options: -r for recursive, -v for verbose, custom output file, etc.
cmd = 'rv -r -o features.csv /mnt/E/cpp/github/RhizoVisionExplorer/imageexamples/crowns'
print('Running:', cmd)
result = subprocess.run(cmd, capture_output=False, text=True, shell=True)

if result.returncode != 0:
    print('rv failed with exit code', result.returncode, file=sys.stderr)
    sys.exit(result.returncode)

print('Folder processed successfully')
print(result.stdout.splitlines()[-1] if result.stdout else 'Done.')

# Do downstream analysis (requires pandas):
df = pd.read_csv('features.csv')
print("Loaded features.csv with", len(df), "rows")
```

## Selective Batch Processing with Python

We may want to exclude certain images from analysis (e.g., files ending with `_seg.png` or `_features.png`). You can use a Python script to filter the file list and call `rv` for each file individually. The script below gets the file list in python, filters it, invokes `rv` per image and appends features automatically to the default `features.csv` (unless you specify `-na`). It will STOP immediately if any invocation of `rv` returns a non–zero exit code.

Invoking `rv` per image enables custom filtering logic, capture output in case of an error and exit gracefully. A python script invoking `rv` multiple times may make use of multiprocessing to spawn multiple `rv` processes for faster processing of image dataset. As of the current beta version, the `rv` program is not implemented and tested to support the file locks to run in multiprocessing environment. Hence using python's multiprocessing is not recommended if the output file name is same for all the multiple processes. So, when running `rv` in multiple processes, please store the features output to different file (use different `-o` option) for each spawned process.

```python
import os
import subprocess
import sys
from pathlib import Path
import pandas as pd

# Configuration
input_dir = Path('/path/to/images')  # change this
rv_exe = Path('./rv')                # or an absolute path like Path('/usr/local/bin/rv')
extra_args = ["-v"]                  # add any global options you want (e.g., "--smooth")

# Gather candidate image files (non-recursive here; use rglob('*') for recursive)
image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}
image_files = [p for p in input_dir.iterdir() if p.suffix.lower() in image_extensions and p.is_file()]

# Filter out derived outputs you don't want to re-process
skip_suffixes = ('_seg.png', '_features.png')
selected = [p for p in image_files if not any(str(p.name).endswith(sfx) for sfx in skip_suffixes)]

if not selected:
    print("No images selected for analysis.")
    sys.exit(0)

for idx, img in enumerate(sorted(selected), start=1):
    cmd = [str(rv_exe), *extra_args, str(img)]
    print(f"[{idx}/{len(selected)}] Analyzing {img.name} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # Echo stdout/stderr to help diagnose, then abort
        print("ERROR: rv failed on", img, file=sys.stderr)
        if result.stdout:
            print("--- stdout ---", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print("--- stderr ---", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    # Optionally show trimmed stdout when verbose.
    if result.stdout.strip():
        print(result.stdout.strip().splitlines()[-1])  # last line (often a summary)

print("All images processed successfully.")

# Do downstream analysis (requires pandas):
df = pd.read_csv('features.csv')
```

</font>
