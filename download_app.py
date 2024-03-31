import base64
import json
import subprocess

from flask import Flask, request, jsonify

app = Flask(__name__)

names = [
    '3-1-2019年05月程序员选择题第1-10题',
    '3-2-2019年05月程序员选择题第11-20题',
    '3-3-2019年05月程序员选择题第21-30题',
    '3-4-2019年05月程序员选择题第31-40题',
]

@app.route('/', methods=['POST'])
def aaa():
    data = request.data
    jd = json.loads(data)
    # print(jd)
    response = jd['response']
    response_json = json.loads(response)
    play_auth = response_json['data']['info']['playAuth']
    vod_video_id = response_json['data']['info']['vodVideoId']
    play_auth_decoded_bytes = base64.b64decode(play_auth).decode('utf-8')
    play_auth_decoded = json.loads(play_auth_decoded_bytes)
    video_title = play_auth_decoded['VideoMeta']['Title']

    # video_title = names[0]
    # names.pop(0)

    # print(play_auth_decoded)
    print('开始下载：' + video_title)

    stage = 'TEST'
    sub_stage = ''
    # stage = '0直播'
    # sub_stage = ''
    sub_stage = sub_stage.replace(" ", "-")
    video_out_path_base = 'cto_video'
    subject = '程序员'
    if sub_stage == '':
        video_out_path = '{}/{}/{}/{}'.format(video_out_path_base, subject, stage, video_title)
    else:
        video_out_path = '{}/{}/{}/{}/{}'.format(video_out_path_base, subject, stage, sub_stage, video_title)

    # 构建命令
    main_go_path = 'main.go'
    command = f"go run {main_go_path} aliyun -p \"{play_auth}\" -v {vod_video_id} -o={video_out_path} --chanSize 300"
    # 执行命令
    subprocess.run(command, shell=True)

    return jsonify({'code': 200, 'msg': '任务执行完成'})


if __name__ == '__main__':
    app.run(debug=True, port=15000)
