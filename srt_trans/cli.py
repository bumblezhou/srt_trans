from googletrans import Translator
import pysrt
import os
import sys
import shutil


def split_list(input_list, chunk_size):
    return [input_list[i:i+chunk_size] for i in range(0, len(input_list), chunk_size)]


def flatten_list(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def translate_srt(input_file, output_file, source_language, target_language):
    # Load SRT file
    subs = pysrt.open(input_file, encoding='utf-8')
    lines = [sub.text for sub in subs]
    # split all lines into small list of lines(no more than 200 lines in each sub list)
    sub_lines_list = split_list(lines, 200)

    # Initialize translator
    translator = Translator()

    translated_lines_list = []
    # Loop each each small list of lines, translate them.
    for sub_lines in sub_lines_list:
        source_text = "@".join(sub_lines)
        translation = translator.translate(source_text, src=source_language, dest=target_language)
        translated_lines = translation.text.split("@")
        translated_lines_list.append(translated_lines)

    translated_lines = flatten_list(translated_lines_list)
    # Translate each subtitle
    for sub, translated_line in zip(subs, translated_lines):
        # Merge the source subtitle and the translated subtitle.
        sub.text = "<font color='#ffff54'>" + sub.text + "</font>" + "\n" + translated_line

    # Save translated SRT file
    subs.save(output_file, encoding='utf-8')


def print_usage():
    print("""
        Usage: srt_file_translator test_file.srt [-src_lang en -dest_lang zh-CN -proxy http://youdomain:your_port]
        Example:
            srt_file_translator test_file.srt
            srt_file_translator test_file.srt -src_lang en -dest_lang zh-TW
            srt_file_translator test_file.srt -src_lang en -dest_lang ja
            srt_file_translator test_file.srt -src_lang en -dest_lang zh-CN
            srt_file_translator test_file.srt -src_lang en -dest_lang fr -proxy http://127.0.0.1:8118
    """)


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
    if len(sys.argv) == 6 and sys.argv[2] == "-src_lang" and sys.argv[4] == "-dest_lang":
        source_language = sys.argv[3]
        target_language = sys.argv[5]
    if len(sys.argv) == 8 and sys.argv[2] == "-src_lang" and sys.argv[4] == "-dest_lang" and sys.argv[6] == "-proxy":
        source_language = sys.argv[3]
        target_language = sys.argv[5]
        proxy = sys.argv[7]
        # Set environment variables (replace with your details)
        # os.environ['http_proxy'] = "http://127.0.0.1:8118"
        # os.environ['https_proxy'] = "http://127.0.0.1:8118"
        os.environ['http_proxy'] = proxy
        os.environ['https_proxy'] = proxy

    output_file = str(input_file).replace(".srt", f".{target_language}.srt")
    translate_srt(input_file, output_file, source_language, target_language)
    
    os.remove(input_file)
    shutil.move(output_file, input_file)


if __name__ == "__main__":
    main()