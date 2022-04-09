#!/bin/bash
__doc__="
Requirements:
    sudo apt install ghostscript
"
INPUT_FPATH=$1
OUTPUT_FPATH=$2

gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$OUTPUT_FPATH" "$INPUT_FPATH"
