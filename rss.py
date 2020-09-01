
import feedparser
import json,os,logging,subprocess,time
from re import findall
from requests import get

path = os.path.dirname(os.path.abspath(__file__))


def log(name):
    global path
    sys_log = logging.getLogger(name)
    sys_log.setLevel(level=logging.DEBUG)
    sys_hander = logging.FileHandler(f'{path}/{name}.txt')
    sys_hander.setLevel(logging.DEBUG)
    sys_form = logging.Formatter('%(asctime)s-[%(levelname)s]: %(message)s')
    sys_hander.setFormatter(sys_form)
    sys_log.addHandler(sys_hander)
    return sys_log

sys_log = log('Log')

def mark(link,ps=None):
    global path
    # 查询 Ps
    if not ps: 
        if not os.path.exists(path+'/mark.json'):
            ps = ''
        else:

            with open(path+'/mark.json','r') as r:
                sys_log.debug(f'mark.json not exists|{link}')
                mark = json.loads(r.read())
            if link not in mark:
                
                ps = ''
            else:
                ps = mark[link]
        return ps
    else:
    # 记录 ps
        if not os.path.exists(path+'/mark.json'):
            sys_log.debug('config.json not exists')
            mark = {}
            mark[link] = ps
            sys_log.info(f'new rss_link {link}')
        else:
            with open(path+'/mark.json','r') as r:
                mark = json.loads(r.read())
            if link not in mark:
                sys_log.info(f'new rss_link {link}')
            mark[link] = ps
        with open(path+'/mark.json','w') as w:
                w.write(json.dumps(mark,ensure_ascii=False,indent=4))
def get_speed(file_path,pass_time):
    for file_ in os.listdir(file_path):
        if ('mp4' in file_) or ('mkv' in file_) or ('flv' in file_):
            size = os.path.getsize(file_path+'/'+file_)
            speed = size/1024/1024/pass_time
            size = size/1024/1024
            return '%.3fMB/s' % speed,'%.3fMB' % size,file_
    return None,None,None
def command(cmd,i):
    start_time = time.time()
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out,err = p.communicate()
    
    try:
        result = out.splitlines()[i].decode('utf-8')  
    except Exception as e:
        sys_log.debug(f'command result error {e}')
        result = None
    pass_time = time.time() - start_time
    return result,pass_time 
def update(link,ps,local_default_path,rclone):
    req = get(link,timeout=10)
    sys_log.debug(f'requests status_code: {req.status_code}')
    res = req.content.decode('utf-8')
    rss = feedparser.parse(res)
    try:
        sys_log.info(f'feed_title: <{rss.feed.title}>')
    except:
        sys_log.debug('feed_title 获取失败')
    typ = None
    if '的 bilibili 收藏夹' in rss.feed.title:
        up_name = rss.feed.title.split('的 bilibili 收藏夹')[0].strip()
        Rss_title = rss.feed.title.split('的 bilibili 收藏夹')[1].strip()
        sys_log.info(f'up主昵称: {up_name}')
        sys_log.info(f'收藏夹: {Rss_title}')
        typ = 'collection'
    
    else:
        
        try:
            Rss_title = rss.feed.title
            sys_log.info(f'feed_title: <{rss.feed.title}>')
        except:
            sys_log.debug('feed_title 获取失败')
            return ps
        sys_log.info(f'Rss_title: {Rss_title}')
    sys_log.debug(f'entries 数量: {len(rss.entries)}')
    sys_log.debug(f'rssKeys: {rss.keys()}')
    sys_log.debug(f'itemKey: {rss.entries[0].keys()}')
    if len(rss.entries) == 0:
        sys_log.info('this link has zero content')
        return ''
    
    items = rss.entries
    i = 0
    tasks = []
    for item in items:
        if item.id == ps or i >= 20:
            
            break
        else:
            tasks.append(item)
            i += 1
    sys_log.info(f'tasks length: {i}')
    # tasks 反转 由下向上执行
    tasks.reverse()
    i = 1
    for task in tasks:
        task_title = findall(r'第\d{1,3}话',task.title)
        if len(task_title) == 1:
            task_title = task_title[0]
            typ = 'bangumi'
            sys_log.info(f'typ: bangumi| {task.title}')
        #item_title = task.title
        #item_summary = task.summary
        #date = task.published
        task.title = task.title.strip()
        poster = None
        res = findall(r'img src=".*jpg',task.summary)
        if len(res) == 1:
            poster = res[0][9:]
        date = None
        if 'published' in task:
            date = task.published
        sys_log.info(f'【task {i}】 title: {task.title}  date: {date}')
        sys_log.info(f' poster: {poster}')
        sys_log.info(f' summary: {task.summary}')
        i += 1
        #item_link = task.link
        sys_log.info(f'    link: {task.link}')
        if typ == 'collection':
            task_path = local_default_path+f'/{up_name}/{Rss_title}/{task.title}'
        elif typ == 'bangumi':
            episode = task_title.replace('第','Ep').replace('话','')
            origin_title = task.title
            task.title = Rss_title+'.'+task.title.replace(task_title,episode)
            task.title = task.title.replace(' ','.')
            task_path = local_default_path+f'/{Rss_title}/{task.title}'
            pass
        else:
            task_path = local_default_path+f'/{Rss_title}/{task.title}'
        

        #os.system(f'annie -C -o {task_path} {task.link}')
        
        if os.path.exists(task_path):
            files = os.listdir(task_path)
            sys_log.info(f'文件夹已存在 将删除目录下文件： {files}')
            for file_ in files:
                os.remove(task_path+'/'+file_)
        else:
            os.makedirs(task_path)
        # 保存封面
        if poster and not os.path.exists(f'{task_path}/poster.jpg'):
            with open(f'{task_path}/poster.jpg','wb') as w:
                w.write(get(poster).content)
                sys_log.info(f'save poster success')   
        file_path,pass_time = command(f'annie -C -o "{task_path}" {task.link}',-1)
        file_path = file_path.replace('Merging video parts into ','')
        #os.system(f'chmod -R 755 {chmod_path}')
        sys_log.debug(f'annie result: {file_path}')
        file_name = file_path.split('/')[-1]
        file_dir = file_path.replace(file_name,'')
        speed,size,file_ = get_speed(task_path,pass_time)
        sys_log.info(f'下载完成：{file_} {size} | {speed} ')
        
        file_xml = file_path.replace(file_name.split('.')[-1],'')+'xml'
        sys_log.debug(f'file_info: 👇\nfile_path: {file_path} \nfile_name: {file_name}\nfile_xml: {file_xml}')
        danmaku2ass = path+'/danmaku2ass.py'
        danmaku_result,pass_time = command(f'python3 {danmaku2ass} "{file_xml}"', -1)
        sys_log.debug(f'danmaku_result: {danmaku_result}')
        if typ == 'bangumi':
            files = os.listdir(task_path)
            sys_log.info(f'typ bangumi rename： {task.title}')
            for file_ in files:
                os.rename(task_path+'/'+file_,task_path+'/'+file_.replace(origin_title,task.title))
        #os.system(f'chmod -R 755 {chmod_path}')
        if rclone:
            rclone_name = rclone['name']
            rclone_path = rclone['path']
            rclone_cmd = rclone['cmd']
            remote_path = task_path.replace(local_default_path,'')
            sys_log.debug(f'rclone {rclone_cmd} "{task_path}/" {rclone_name}:"{rclone_path}{remote_path}"')
            result,pass_time = command(f'rclone {rclone_cmd} "{task_path}/" {rclone_name}:"{rclone_path}{remote_path}"',-1)
            t = '%.3f' % pass_time
            sys_log.debug(f'rclone upload pass_time {t}m result {result}')
            
        if 'Succeed :' not in danmaku_result:
            sys_log.debug(f'danmaku2ass error')
            break
        else:
            ps = task.id
            mark(link,ps)
    
def main():
    global path
    sys_log.info('rssBili start')
    sys_log.debug(f'pwd: {path}')
    if not os.path.exists(path+'/danmaku2ass.py'):
        print('Error: not find danmaku2ass.py')
        return 
        #raise 'Error: not find danmaku2ass.py'
    if os.path.exists(path+'/config.json'):
        with open(path+'/config.json','r') as r:
            config = json.loads(r.read())
        links = config['rss']
        if 'rclone' in config.keys():
            rclone = config['rclone']
        else:
            rclone = None
        # 开始更新rss_link
        for link in links:
            local_default_path = links[link] 
            print('updating',link)
            sys_log.info(f'start update {link}')
            sys_log.info('')
            ps = mark(link)
            update(link,ps,local_default_path,rclone)
            
            sys_log.info(f'stop update {link}')
    else:
        sys_log.debug('Error: not find config.json')

    sys_log.info('rssBili stop')
    pass

if __name__ == "__main__":
    
    main()