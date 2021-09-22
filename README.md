# PUGCQ dataset construction

## Requirements

* numpy
* pandas
* scipy   
* python-docx
* youtube-dl
* ffmpeg

Run this script to install the required environment:
```
sh install_requirements.sh
```       

## Run
1. Build the video dataset  
```angular2html
python video_download.py -i <input_path> -d <download_dir> -o <output_dir>
```          
"-i", "--input", Path to pugcq mos file    
"-d", "--download_dir", Directory of downloaded videos     
"-o", "--output_dir", Directory of output final videos
         
           
2. Process and summarize the original subject labels
```angular2html
python mos_build.py -i <input_dir> -o <output_dir>  
```
"-i", "--input_dir", Directory of original pugcq subject labels      
"-o", "--output_dir", Directory of Directory of output mos      
