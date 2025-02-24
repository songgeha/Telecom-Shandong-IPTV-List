import requests
from urllib.parse import urlparse
import os

def classify_channel(tvg_id, channel_name):
    """分类逻辑"""
    lower_tvg_id = str(tvg_id).lower()
    
    if 'cctv' in lower_tvg_id or 'cgtn' in lower_tvg_id:
        return '央视频道'
    elif '卫视' in tvg_id:
        return '卫视频道'
    elif '山东' in tvg_id:
        return '山东频道'
    return '其它频道'

def process_m3u(url):
    """处理单个M3U URL"""
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        content = response.text
    except Exception as e:
        print(f"⚠️ 无法获取 {url}: {str(e)}")
        return False

    # 初始化分类容器
    categories = {
        '央视频道': [],
        '卫视频道': [],
        '山东频道': [],
        '其它频道': []
    }

    lines = [line.strip() for line in content.split('\n') if line.strip()]
    current_channel = {}
    
    for line in lines:
        if line.startswith('#EXTINF'):
            # 解析元数据
            tvg_id = ''
            if 'tvg-id="' in line:
                tvg_id = line.split('tvg-id="')[1].split('"')[0]
            
            channel_name = line.split(',')[-1].strip()
            current_channel = {
                'tvg_id': tvg_id,
                'name': channel_name
            }
        elif current_channel and line.startswith('http'):
            # 分类处理
            category = classify_channel(
                current_channel['tvg_id'],
                current_channel['name']
            )
            
            # 验证URL有效性
            if line.startswith(('http://', 'https://')):
                entry = f"{current_channel['name']},{line}"
                categories[category].append(entry)
            
            current_channel = {}
    
    # 生成输出内容
    output = []
    for category in ['央视频道', '卫视频道', '山东频道', '其它频道']:
        if categories[category]:
            output.append(f"{category},#genre#")
            output += categories[category]
            output.append('')  # 空行分隔
    
    # 生成文件名
    path = urlparse(url).path
    base_name = os.path.basename(path).split('.')[0]
    output_file = f"{base_name}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output).strip())
    
    print(f"✅ 成功生成: {output_file}")
    return True

if __name__ == '__main__':
    # 需要处理的M3U列表
    m3u_urls = [
        'https://raw.githubusercontent.com/sumingyd/Telecom-Shandong-IPTV-List/main/Unicom-Shandong.m3u',
        # 添加更多URL...
    ]

    for url in m3u_urls:
        print(f"\n处理中: {url}")
        process_m3u(url)
