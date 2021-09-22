# *encoding=utf-8
import os
import argparse
import pandas as pd


# download video with youtube-dl
def download(save_path):
    if os.path.exists(save_path):
        print(save_path, 'already exist!')
        return 0
    print(save_path, 'start download')
    print('youtube-dl -o %s --no-part %s' % (save_path, url))
    return os.system(('youtube-dl -o %s --no-part %s' % (save_path, url)))


# cut video with ffmpeg
def video_cut(input_path, output_path, start_time, continue_time=5):
    command = 'ffmpeg -ss %s -t %s -accurate_seek -i "%s" -codec copy -avoid_negative_ts 1 "%s"' % (
        str(start_time), str(continue_time), input_path, output_path)
    print(command)
    return os.system(command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='pugcq_mos.xls', help='Path to pugcq mos file.')
    parser.add_argument('-d', '--download_dir', type=str, default='downloads', help='Path to save downloaded videos.')
    parser.add_argument('-o', '--output_dir', type=str, default='videos', help='Path to output final videos.')
    args = parser.parse_args()
    excel_path = args.input
    download_dir = args.download_dir
    output_dir = args.output_dir

    # read data
    data = pd.read_excel(excel_path)
    data = pd.Series(data.iloc[:, 0])
    data = data.str.split("[\./-]", expand=True)
    path_list = data.iloc[:, 0]
    start_time_list = data.iloc[:, 1]
    path_suffix = "https://www.bilibili.com/video/"
    url_list = path_suffix + path_list
    print(len(path_list))

    # create output dir
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # handle
    for i in range(len(url_list)):
        url = url_list[i]
        file_name = url.split('/')[-1] + '.mp4'
        save_path = os.path.join(download_dir, file_name)
        results = download(save_path)

        cut_file_name = url.split('/')[-1] + "-" + str(start_time_list[i]) + ".mp4"
        cut_path = os.path.join(output_dir, cut_file_name)
        if os.path.exists(save_path) and not os.path.exists(cut_path):
            # cut twice for exact video time
            results = video_cut(save_path, file_name, start_time_list[i])
            results = video_cut(file_name, cut_path, 0)
            os.remove(file_name)
        print()

    print('done')
