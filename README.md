# srt_file_translator
## Translage any SubRip file from any source language to any target language, and merger them into the target SubRip(.srt) file.

# How to usage:

```bash
Usage: python ./app.py test_file.srt [-src_lang en -dest_lang zh-CN -proxy http://youdomain:your_port]
Example:
    python ./app.py ./test/test_file.srt
    python ./app.py ./test/test_file.srt -src_lang en -dest_lang zh-TW
    python ./app.py ./test/test_file.srt -src_lang en -dest_lang ja
    python ./app.py ./test/test_file.srt -src_lang en -dest_lang zh-CN
    python ./app.py ./test/test_file.srt -src_lang en -dest_lang fr -proxy http://127.0.0.1:8118
```

# Installation
## srt_file_translator is available on pypi. To intall it you can:
```bash
sudo pip install srt_file_translator
```