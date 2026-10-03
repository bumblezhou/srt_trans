# srt_trans
A tool which can translate any SubRip file from any source language to any target language, and merger them into the original SubRip(.srt) file. It can also extract subtitles from any mkv files, and translate the subtitles into any language you want.

## How to usage:

```bash
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
```

## How to package
```bash
pip install wheel
python setup.py sdist bdist_wheel
```

## How to publish to pypi
```bash
pip install twine
twine upload dist/*
```

## Installation
### srt_trans is available on pypi. To intall it you can:
```bash
sudo pip install srt_trans
```
