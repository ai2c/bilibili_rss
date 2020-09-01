# bilibili_rss

**请注意配置中的所有路径都应以/开头 且结尾不需要/**

---
> ## 功能
---
- 从rss订阅链更新B站视频，支持多个rss链且分别设置默认下载路径
- 按不同up主 不同收藏夹进行目录整理，番剧第\d话格式转为Ep\d
- 可选择下载后调用rclone上传并删除本地文件
- b站弹幕转字幕文件，在支持的客户端上可以实现弹幕效果如emby
    - emby播放效果
    ![image.png](https://kyun.ltyuanfang.cn/tc/2020/09/01/04a1e232615fa.png)
---
> ## 使用过程
---    
- >### 准备工作
    - bilibili_rss 文件 直接git clone到本地
    - 在bilibili_rss目录下运行 pip3 install -r requirements.txt
    - [danmaku2ass](https://github.com/1299172402/danmu2ass-simply) 中的danmaku2ass.py文件移动至**bilibili_rss**目录下 与config.json处在同一级目录
    - 安装[annie](https://github.com/iawia002/annie#specify-the-output-path-and-name)

- >### 使用
    - 配置config.json文件，可以配置不同的rss链，rss链后跟下载位置
    - rclone ((删除rclone键 关闭调用rclone上传功能) )
        - rclone.path是文件将要上传到云盘的地址
        - rclone.name添加云盘时的名字
        - rclone.cmd上传类型 copy or move 可选
    - linux下配置cron实现定时任务，建议频率半小时或一小时一次,自行决定。（脚本为单线程）
        ```shell
        */30 * * * * python3 /path/to/bilibili_Rss/rss.py
        ```
> ## 关于

- ### rss链接
    推荐使用[rsshub](https://docs.rsshub.app/social-media.html#bilibili)

