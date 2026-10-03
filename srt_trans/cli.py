import requests
import pysrt
import os
import sys
import shutil
import ffmpeg
import time

# 默认代理。如果命令行没有指定 -proxy，则使用本地 8118 端口
DEFAULT_PROXY = "http://127.0.0.1:8118"


def extract_subtitles(video_file, output_srt, track_number = 1):
    # Extract subtitles using FFmpeg
    try:
        (
            ffmpeg
            .input(video_file)
            .output(output_srt, map='s:' + str(track_number - 1))
            .run()
        )
        print(f'Subtitles extracted from {video_file} and saved to {output_srt}')
    except ffmpeg.Error as e:
        print(f'Error: {e}')


def split_list(input_list, chunk_size):
    return [input_list[i:i+chunk_size] for i in range(0, len(input_list), chunk_size)]


def flatten_list(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def multi_find(source_text, search_key):
    return [pos for pos in range(len(source_text)) if source_text.startswith(search_key, pos)]


def translate_text(text, source_lang='en', target_lang='zh-CN', proxy=DEFAULT_PROXY):
    # 使用 Google Translate 网页端的非官方接口
    url = 'https://translate.google.com/translate_a/single'

    params = {
        # client=gtx 容易返回 HTTP 429，当前使用 client=at
        'client': 'at',
        'sl': source_lang,
        'tl': target_lang,
        'dt': 't',
        'q': text,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    # 显式指定代理，避免 requests 是否读取系统代理环境变量的不确定性
    proxies = {
        'http': proxy,
        'https': proxy
    } if proxy else None

    # Google 接口偶尔会出现 429、网络超时等情况，最多重试 3 次
    for attempt in range(1, 4):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                proxies=proxies,
                timeout=30
            )

            # print(f"Google Translate: HTTP {response.status_code}, attempt {attempt}/3")

            if response.status_code == 200:
                result = response.json()

                # Google 返回的数据结构中，result[0] 保存翻译结果
                extracted_result = [raw_line[0] for raw_line in result[0] if raw_line and raw_line[0]]
                return extracted_result

            if response.status_code == 429:
                print("Google Translate: HTTP 429, retrying...")
            else:
                print(f"Google Translate: HTTP {response.status_code}")
                print(response.text[:500])

        except requests.RequestException as e:
            print(f"Google Translate request error: {e}, attempt {attempt}/3")

        if attempt < 3:
            time.sleep(attempt * 2)

    # 翻译失败时返回 None
    # translate_srt() 中会对此进行判断，避免 len(None) 导致程序崩溃
    return None


def translate_lines(lines, source_language, target_language, proxy):
    # 将一批字幕使用换行符连接起来，一次发送给 Google
    source_text = "\n".join(lines)

    translated_lines = translate_text(
        source_text,
        source_lang=source_language,
        target_lang=target_language,
        proxy=proxy
    )

    return translated_lines


def combine_lines(translated_lines):
    # Google 返回结果的换行结构异常时，尝试重新组合字幕行
    result = []
    temp_line = ""
    for raw_line in translated_lines:
        if str(raw_line).endswith("\n"):
            result.append(raw_line)
            temp_line = ""
        else:
            temp_line += raw_line
            continue
    result.append(translated_lines[-1])
    return result


def translate_srt(input_file, output_file, source_language, target_language, proxy):
    result = True

    # Load SRT file
    srt_file = pysrt.open(input_file, encoding='utf-8')
    lines = [sub.text for sub in srt_file]

    # 每次最多翻译 200 条字幕，避免逐条请求 Google
    sub_lines_list = split_list(lines, 200)

    translated_lines_list = []

    for sub_lines in sub_lines_list:
        translated_lines = translate_lines(
            sub_lines,
            source_language,
            target_language,
            proxy
        )

        # HTTP 请求失败时 translate_text() 返回 None
        # 必须先判断，否则直接 len(None) 会导致程序崩溃
        if translated_lines is None:
            print("Can not translate the subtitle correctly.")
            result = False
            break

        # 正常情况下，Google 返回的翻译行数应该与原字幕数量一致
        if len(translated_lines) == len(sub_lines):
            translated_lines_list.append(translated_lines)
        else:
            # 如果 Google 合并或拆分了换行，尝试恢复原来的字幕行数量
            translated_lines = combine_lines(translated_lines)

            if len(translated_lines) == len(sub_lines):
                translated_lines_list.append(translated_lines)
            else:
                print("Can not translate the subtitle correctly.")
                result = False
                break

    if not result:
        return result

    translated_lines = flatten_list(translated_lines_list)

    # 将中文翻译追加到原英文字幕下面
    for sub, translated_line in zip(srt_file, translated_lines):
        sub.text = "<font color='#ffff54'>" + sub.text + "</font>" + "\n" + translated_line

    # Save translated SRT file
    srt_file.save(output_file, encoding='utf-8')

    return result


def print_usage():
    print("""
        Usage: srt_trans test_file.srt [-src_lang en -dest_lang zh-CN -proxy http://youdomain:your_port]
        Example:
            srt_trans ./test_video.mkv
            srt_trans ./test_video.mkv -src_lang en -dest_lang zh-TW
            srt_trans ./test_video.mkv -src_lang en -dest_lang zh-CN -proxy http://127.0.0.1:8118
            srt_trans ./test_video.mkv -track_number 2
            srt_trans ./test_video.mkv -src_lang en -dest_lang zh-TW -track_number 2
            srt_trans ./test_video.mkv -src_lang en -dest_lang zh-CN -proxy http://127.0.0.1:8118 -track_number 2
            srt_trans test_file.srt
            srt_trans test_file.srt -src_lang en -dest_lang zh-TW
            srt_trans test_file.srt -src_lang en -dest_lang ja
            srt_trans test_file.srt -src_lang en -dest_lang zh-CN
            srt_trans test_file.srt -src_lang en -dest_lang fr -proxy http://127.0.0.1:8118
    """)


def pre_process_srt_file(input_file):
    # Load SRT file
    srt_file = pysrt.open(input_file, encoding='utf-8')
    for sub in srt_file:
        sub.text = str(sub.text).replace("\n", " ").replace("<i>", "").replace("</i>", "").replace("{\\an8}", "").replace("\"", "")
    srt_file.save(input_file, encoding='utf-8')


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"{input_file} not exists!")
        return
    
    source_language = "en"      # Source language code (e.g., "en" for English)
    target_language = "zh-CN"   # Target language code (e.g., "zh-CN" for Simple Chinese)
    proxy = DEFAULT_PROXY       # 如果没有指定 -proxy，则默认使用 http://127.0.0.1:8118
    
    if str(input_file).lower().endswith(".mkv"):
        track_number = 1
        video_file = ""

        if len(sys.argv) == 2:
            pass

        elif len(sys.argv) == 4 and sys.argv[2] == "-track_number":
            track_number = sys.argv[3]

        elif len(sys.argv) == 6 and sys.argv[2] == "-src_lang" and sys.argv[4] == "-dest_lang":
            source_language = sys.argv[3]
            target_language = sys.argv[5]

        elif len(sys.argv) == 8 and sys.argv[2] == "-src_lang" and sys.argv[4] == "-dest_lang" and sys.argv[6] == "-track_number":
            source_language = sys.argv[3]
            target_language = sys.argv[5]
            track_number = sys.argv[7]

        elif len(sys.argv) == 8 and sys.argv[2] == "-src_lang" and sys.argv[4] == "-dest_lang" and sys.argv[6] == "-proxy":
            source_language = sys.argv[3]
            target_language = sys.argv[5]
            proxy = sys.argv[7]

        elif len(sys.argv) == 10 and sys.argv[2] == "-src_lang" and sys.argv[4] == "-dest_lang" and sys.argv[6] == "-proxy" and sys.argv[8] == "-track_number":
            source_language = sys.argv[3]
            target_language = sys.argv[5]
            proxy = sys.argv[7]
            track_number = sys.argv[9]

        else:
            print("Invalid arguments!")
            return

        if not str(track_number).isdigit():
            print("Invalid track_number, it should be an int!")
            return

        video_file = input_file
        input_file = video_file.replace(".mkv", ".srt")
        extract_subtitles(video_file, input_file, int(track_number))

    else:
        if len(sys.argv) == 2:
            pass

        elif len(sys.argv) == 6 and sys.argv[2] == "-src_lang" and sys.argv[4] == "-dest_lang":
            source_language = sys.argv[3]
            target_language = sys.argv[5]

        elif len(sys.argv) == 8 and sys.argv[2] == "-src_lang" and sys.argv[4] == "-dest_lang" and sys.argv[6] == "-proxy":
            source_language = sys.argv[3]
            target_language = sys.argv[5]
            proxy = sys.argv[7]

        else:
            print("Invalid arguments!")
            return

    pre_process_srt_file(input_file)

    output_file = str(input_file).replace(".srt", f".{target_language}.srt")

    translate_result = translate_srt(
        input_file,
        output_file,
        source_language,
        target_language,
        proxy
    )

    if not translate_result:
        return

    os.remove(input_file)
    shutil.move(output_file, input_file)

    print(f"Translation completed: {input_file}")


if __name__ == "__main__":
    main()