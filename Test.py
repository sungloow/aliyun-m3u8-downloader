import json
import subprocess
import base64

# JSON数据
json_data = '''
{
    "status": 1,
    "msg": "加载成功",
    "data": {
        "info": {
            "isSeventyFive": 0,
            "playAuth": "eyJTZWN1cml0eVRva2VuIjoiQ0FJU2lBTjFxNkZ0NUIyeWZTaklyNWJHZU9PSGxLaDE1SnJmY0hMcnFtTUFUY0pnaTdDVHR6ejJJSDFQZlhGdEFlMFp0LzArbVdsUTV2d2FscklxRXNRZkd4ZWRNWkVwdHNrSXJseitKb0hidk5ldTBic0hoWnY5NWVwOW5wNmlqcUhvZU96Y1lJNzMwWjdQQWdtMlEwWVJySkwrY1RLOUphYk1VL21nZ29KbWFkSTZSeFN4YVNFOGF2NWRPZ3BscnIwSVZ4elBNdnIvSFJQMnVtN1pIV3R1dEEwZTgzMTQ1ZmFRejlHaTZ4YlRpM2I5ek9FVXFPYVhKNFMvUGZGb05ZWnlTZjZvd093VUVxL2R5M3hvN3hGYjFhRjRpODRpL0N2YzdQMlFDRU5BK3dtbFB2dTJpOE5vSUYxV2E3UVdJWXRncmZQeGsrWjEySmJOa0lpbDVCdFJFZHR3ZUNuRldLR216c3krYjRIUEROc2ljcXZoTUhuZ3k4MkdNb0tQMHprcGVuVUdMZ2hIQ2JGRFF6MVNjVVYxRVd1RWNmYjdvZ21TUDFqOEZQZS92ZnRvZ2NZdi9UTEI1c0dYSWxXRGViS2QzQnNETjRVMEIwRlNiRU5OaERTOEt2SlpLbFVkTGdvL1Yrek5WL2xhYUJGUHRLWFdtaUgrV3lOcDAzVkxoZnI2YXVOcGJnUHIxVVFwTlJxQUFRRHd3OHZ0eTJGdWtKRkhzOXloRnhXZ0p1am1NR2JFc0xMMWYzTVpqa09XQzNENUtseVJtcFN5L3dUY0NIZmFOOFdXKzNVcE01bVRyeVhwb2lqYVQrSGNXN2pLWDJpT2lBQlFGWnJUU0Z0dnM4QXhpRGQxRkNHSmMwb3ErTmxpY1F5aFZBTEhHSkJSS0tkZTNHWFNEYm9IbS9QVUgzbTB3K0hGTmtFazVOb2lJQUE9IiwiQXV0aEluZm8iOiJ7XCJDSVwiOlwiTXZtVlBNZzVEalZWbXRMbVBLaWRNV1FVNzVRaTAyZkR3ZVVIZVVneHBvQlRuM05ZU0FJMkI4c0ZJd3J1YlJHVlRPaUFmNWdLenFkTk02THVmM1loaCtsTENUYU9qYldJbG5HT3V3dFpTQVU9XCIsXCJDYWxsZXJcIjpcIjVhaXlIVnd0QTdpaWppWXRhbmRpclpOay9qai9Cbk5XR21GWnZvTnVDZzg9XCIsXCJFeHBpcmVUaW1lXCI6XCIyMDI0LTAzLTMwVDEyOjQ4OjUwWlwiLFwiTWVkaWFJZFwiOlwiYjYxZThiNTQ4YjA0NDA4MjkzOWQzNTRjMjFiY2I2MWRcIixcIlBsYXlEb21haW5cIjpcInYzMC41MWN0by5jb21cIixcIlNpZ25hdHVyZVwiOlwibFlGdWFkZVFmaHVwUEJUSitKRVNHajE5WUdJPVwifSIsIlZpZGVvTWV0YSI6eyJTdGF0dXMiOiJOb3JtYWwiLCJWaWRlb0lkIjoiYjYxZThiNTQ4YjA0NDA4MjkzOWQzNTRjMjFiY2I2MWQiLCJUaXRsZSI6IuesrDHoioLvvJrmtYvor5Xov4fnqIvlkoznrqHnkIbvvIjkuIrvvIkiLCJDb3ZlclVSTCI6Imh0dHBzOi8vdjMwLjUxY3RvLmNvbS9iNjFlOGI1NDhiMDQ0MDgyOTM5ZDM1NGMyMWJjYjYxZC9zbmFwc2hvdHMvZjM1YzA0YzM2MjFkNDQxOWJkOTg5YWQ3YzgzMTY2Y2YtMDAwMDUuanBnIiwiRHVyYXRpb24iOjk3Mi45MzkzfSwiQWNjZXNzS2V5SWQiOiJTVFMuTlVzM1kzeXdUU1g0clRaTmNVQU1MZHU4VSIsIlBsYXlEb21haW4iOiJ2MzAuNTFjdG8uY29tIiwiQWNjZXNzS2V5U2VjcmV0IjoiSFh1UlpnYUtKQkhkaUFhQ0c0UzFaUTI2dXlORTNZWk1hYnptNkxoMW1HSHgiLCJSZWdpb24iOiJjbi1zaGFuZ2hhaSIsIkN1c3RvbWVySWQiOjExMzI2MzE0MjEwNTc3Nzd9",
            "vodVideoId": "b61e8b548b044082939d354c21bcb61d",
            "videoId": "883143",
            "lessonId": "871179",
            "format": "m3u8",
            "encryptType": 1,
            "nexturl": "https://edu.51cto.com//center/course/lesson/index?id=11768_871178&type=wejob",
            "prevurl": "https://edu.51cto.com//center/course/lesson/index?id=11768_886745&type=wejob",
            "htime": 0,
            "utime": 0,
            "reportLogUrl": "https://edu.51cto.com/center/player/log/time?type=wejoboutcourse"
        }
    }
}
'''
# 解析JSON数据
data = json.loads(json_data)
play_auth = data['data']['info']['playAuth']
vod_video_id = data['data']['info']['vodVideoId']
play_auth_decoded_bytes = base64.b64decode(play_auth).decode('utf-8')
play_auth_decoded = json.loads(play_auth_decoded_bytes)

stage = '4软件评测师-测试技术篇'
sub_stage = '第2章 软件测试应用技术'
# stage = '直播'
# sub_stage = ''
sub_stage = sub_stage.replace(" ", "-")

video_title = play_auth_decoded['VideoMeta']['Title']
video_out_path_base = 'cto_video'
if sub_stage == '':
    video_out_path = '{}/{}/{}'.format(video_out_path_base, stage, video_title)
else:
    video_out_path = '{}/{}/{}/{}'.format(video_out_path_base, stage, sub_stage, video_title)

# 构建命令
main_go_path = 'main.go'
command = f"go run {main_go_path} aliyun -p \"{play_auth}\" -v {vod_video_id} -o={video_out_path} --chanSize 1"
# 执行命令
subprocess.run(command, shell=True)
