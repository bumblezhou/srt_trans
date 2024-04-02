from googletrans import Translator
import pysrt
import os
import sys
import shutil

# Set environment variables (replace with your details)
os.environ['http_proxy'] = "http://127.0.0.1:8118"
os.environ['https_proxy'] = "http://127.0.0.1:8118"

def split_list(input_list, chunk_size):
    return [input_list[i:i+chunk_size] for i in range(0, len(input_list), chunk_size)]

def flatten_list(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]

def translate_srt(input_file, output_file, target_language):
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
        translation = translator.translate(source_text, src="en", dest=target_language)
        translated_lines = translation.text.split("@")
        translated_lines_list.append(translated_lines)

    translated_lines = flatten_list(translated_lines_list)
    # Translate each subtitle
    for sub, translated_line in zip(subs, translated_lines):
        # Merge the source subtitle and the translated subtitle.
        sub.text = "<font color='#ffff54'>" + sub.text + "</font>" + "\n" + translated_line

    # Save translated SRT file
    subs.save(output_file, encoding='utf-8')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("input target movie path!")
    else:
        input_file = sys.argv[1]
        output_file = str(input_file).replace(".srt", ".cn.srt")
        target_language = "zh-CN"  # Target language code (e.g., "fr" for French)
        translate_srt(input_file, output_file, target_language)
       
        os.remove(input_file)
        shutil.move(output_file, input_file)
