#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
解析抖音分享链接，下载视频，并转成文字
参考: ParseDouyinShareUrl.php
"""

import argparse
import json
import os
import re
import random
import string
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# User Agent
USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1'


def create_session():
    """创建带重试机制的requests session"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def rand_seq(n):
    """生成随机字符串"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(n))


def generate_fixed_length_numeric_id(length):
    """生成固定位数的随机数字（前导零）"""
    max_num = 10 ** length
    random_num = random.randint(0, max_num - 1)
    return str(random_num).zfill(length)


def get_no_webp_url(url_list):
    """优先获取非 .webp 格式的图片 url"""
    for url in url_list:
        if '.webp' not in url:
            return url
    return url_list[0] if url_list else ''


def get_canonical_from_html(html_content):
    """从 HTML 字符串获取 canonical URL"""
    match = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def parse_video_id_from_path(url_path):
    """从路径中提取视频ID"""
    if not url_path:
        return None
    
    # 如果是完整URL，先解析
    if url_path.startswith('http://') or url_path.startswith('https://'):
        parsed = urlparse(url_path)
    else:
        parsed = urlparse('http://example.com' + url_path)
    
    # 判断网页精选页面的视频
    # https://www.douyin.com/jingxuan?modal_id=xxxx
    if parsed.query:
        query_params = parse_qs(parsed.query)
        if 'modal_id' in query_params and query_params['modal_id']:
            return query_params['modal_id'][0]
    
    # 判断其他页面的视频
    # https://www.iesdouyin.com/share/video/xxxx
    path = parsed.path.strip('/')
    if not path:
        return None
    
    path_parts = path.split('/')
    if path_parts:
        return path_parts[-1]
    
    return None


def convert_ssr_data_to_standard_format(video_data):
    """将 SSR 数据格式转换为标准格式"""
    avatar_url_list = []
    if 'author' in video_data and 'avatar_thumb' in video_data['author']:
        if isinstance(video_data['author']['avatar_thumb'], dict) and 'url_list' in video_data['author']['avatar_thumb']:
            avatar_url_list = video_data['author']['avatar_thumb']['url_list']
        elif isinstance(video_data['author']['avatar_thumb'], str):
            avatar_url_list = [video_data['author']['avatar_thumb']]
    
    result = {
        'desc': video_data.get('desc', ''),
        'author': {
            'sec_uid': video_data.get('author', {}).get('sec_uid', ''),
            'nickname': video_data.get('author', {}).get('nickname', ''),
            'avatar_thumb': {
                'url_list': avatar_url_list
            },
        },
    }
    
    # 处理视频数据
    if 'video' in video_data:
        video = video_data['video']
        play_url_list = []
        if 'playAddr' in video and 'url_list' in video['playAddr']:
            play_url_list = video['playAddr']['url_list']
        elif 'play_addr' in video and 'url_list' in video['play_addr']:
            play_url_list = video['play_addr']['url_list']
        
        cover_url_list = []
        if 'cover' in video and 'url_list' in video['cover']:
            cover_url_list = video['cover']['url_list']
        
        result['video'] = {
            'play_addr': {
                'url_list': play_url_list
            },
            'cover': {
                'url_list': cover_url_list
            },
        }
    
    # 处理图片数据
    if 'images' in video_data and isinstance(video_data['images'], list):
        result['images'] = video_data['images']
    
    return result


def extract_video_data_from_html(html, video_id):
    """从HTML中提取视频数据（多种方法）"""
    # 方法1: 尝试从 window._ROUTER_DATA 提取（主要方法）
    match = re.search(r'window\._ROUTER_DATA\s*=\s*(.*?)</script>', html, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            json_data = json.loads(json_str)
            if json_data and 'loaderData' in json_data:
                # HTML中的路径是固定的 "video_(id)/page"
                page_key = 'video_(id)/page'
                if page_key not in json_data['loaderData']:
                    page_key = f'video_{video_id}/page'
                
                if page_key in json_data['loaderData']:
                    page_data = json_data['loaderData'][page_key]
                    if 'videoInfoRes' in page_data and 'item_list' in page_data['videoInfoRes']:
                        if page_data['videoInfoRes']['item_list']:
                            return page_data['videoInfoRes']['item_list'][0]
                        elif 'filter_list' in page_data['videoInfoRes']:
                            filter_list = page_data['videoInfoRes']['filter_list']
                            for filter_item in filter_list:
                                if filter_item.get('aweme_id') == video_id:
                                    raise Exception(
                                        f"获取视频信息失败: {filter_item.get('filter_reason', '未知原因')} - {filter_item.get('detail_msg', '')}"
                                    )
        except json.JSONDecodeError:
            pass
    
    # 方法2: 尝试从 window._SSR_HYDRATED_DATA 提取
    match = re.search(r'window\._SSR_HYDRATED_DATA\s*=\s*({.+?});', html, re.DOTALL)
    if match:
        json_str = match.group(1)
        if '&' in json_str:
            import html as html_module
            json_str = html_module.unescape(json_str)
        try:
            json_data = json.loads(json_str)
            if json_data and 'defaultScope' in json_data and 'videoData' in json_data['defaultScope']:
                return convert_ssr_data_to_standard_format(json_data['defaultScope']['videoData'])
        except (json.JSONDecodeError, KeyError):
            pass
    
    # 方法3: 尝试从 RENDER_DATA script 标签提取
    match = re.search(r'<script[^>]*id=["\']RENDER_DATA["\'][^>]*>(.+?)</script>', html, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        if '%' in json_str:
            from urllib.parse import unquote
            json_str = unquote(json_str)
        try:
            json_data = json.loads(json_str)
            if json_data and 'defaultScope' in json_data:
                if 'videoData' in json_data['defaultScope']:
                    return convert_ssr_data_to_standard_format(json_data['defaultScope']['videoData'])
                elif 'aweme' in json_data['defaultScope']:
                    return convert_ssr_data_to_standard_format(json_data['defaultScope']['aweme'])
        except (json.JSONDecodeError, KeyError):
            pass
    
    # 方法4: 尝试从 window.RENDER_DATA 提取
    match = re.search(r'window\.RENDER_DATA\s*=\s*({.+?});', html, re.DOTALL)
    if match:
        json_str = match.group(1)
        if '&' in json_str:
            import html as html_module
            json_str = html_module.unescape(json_str)
        if '%' in json_str:
            from urllib.parse import unquote
            json_str = unquote(json_str)
        try:
            json_data = json.loads(json_str)
            if json_data and 'defaultScope' in json_data and 'videoData' in json_data['defaultScope']:
                return convert_ssr_data_to_standard_format(json_data['defaultScope']['videoData'])
        except (json.JSONDecodeError, KeyError):
            pass
    
    # 方法5: 尝试直接匹配 videoData 或 aweme_detail
    patterns = [
        r'"videoData":\s*({.+?}),',
        r'"aweme_detail":\s*({.+?}),',
        r'"itemList":\s*\[({.+?})\]',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            json_str = match.group(1)
            if '&' in json_str:
                import html as html_module
                json_str = html_module.unescape(json_str)
            if '%' in json_str:
                from urllib.parse import unquote
                json_str = unquote(json_str)
            try:
                json_data = json.loads(json_str)
                if json_data:
                    return convert_ssr_data_to_standard_format(json_data)
            except (json.JSONDecodeError, KeyError):
                pass
    
    return None


def get_redirect_url(session, video_url):
    """获取重定向后的视频地址"""
    if not video_url:
        return video_url
    
    try:
        response = session.get(video_url, allow_redirects=False, headers={'User-Agent': USER_AGENT}, timeout=10)
        if 300 <= response.status_code < 400:
            location = response.headers.get('Location')
            if location:
                return location
    except Exception:
        pass
    
    return video_url


def parse_video_id(video_id, session):
    """根据视频ID解析视频信息"""
    # 步骤1：请求抖音页面
    req_url = f"https://www.iesdouyin.com/share/video/{video_id}"
    
    response = session.get(req_url, headers={'User-Agent': USER_AGENT}, timeout=30)
    if not response.ok:
        raise Exception(f'请求失败: {response.status_code}')
    
    html = response.text
    
    # 步骤2：判断是否是图集（Note）
    is_note = False
    canonical = get_canonical_from_html(html)
    if canonical and '/note/' in canonical:
        is_note = True
    
    data = None
    
    # 获取图集
    if is_note:
        web_id = '75' + generate_fixed_length_numeric_id(15)
        a_bogus = rand_seq(64)
        
        api_url = (
            f'https://www.iesdouyin.com/web/api/v2/aweme/slidesinfo/?reflow_source=reflow_page'
            f'&web_id={web_id}&device_id={web_id}&aweme_ids=%5B{video_id}%5D'
            f'&request_source=200&a_bogus={a_bogus}'
        )
        
        api_response = session.get(api_url, headers={'User-Agent': USER_AGENT}, timeout=30)
        if api_response.ok:
            json_data = api_response.json()
            if json_data.get('aweme_details') and len(json_data['aweme_details']) > 0:
                data = json_data['aweme_details'][0]
            else:
                is_note = False
        else:
            is_note = False
    
    # 获取视频
    if not is_note:
        data = extract_video_data_from_html(html, video_id)
        if not data:
            raise Exception('从HTML中解析视频JSON信息失败，请检查抖音页面结构是否已更新')
    
    if not data:
        raise Exception('无法获取视频数据')
    
    # 获取图集图片地址
    images = []
    if 'images' in data and isinstance(data['images'], list):
        for image_item in data['images']:
            url_list = image_item.get('url_list', [])
            image_url = get_no_webp_url(url_list)
            if image_url:
                images.append({
                    'url': image_url,
                    'live_photo_url': image_item.get('video', {}).get('play_addr', {}).get('url_list', [None])[0],
                })
    
    # 步骤4：提取视频播放地址
    video_url = ''
    if not is_note and 'video' in data and 'play_addr' in data['video']:
        url_list = data['video']['play_addr'].get('url_list', [])
        if url_list:
            # 将 playwm 替换为 play，获取无水印视频
            video_url = url_list[0].replace('playwm', 'play')
    
    # 如果图集地址不为空时，因为没有视频，上面抖音返回的视频地址无法访问，置空处理
    if images:
        video_url = ''
    
    # 获取封面
    cover_url = ''
    if 'video' in data and 'cover' in data['video']:
        url_list = data['video']['cover'].get('url_list', [])
        if url_list:
            cover_url = get_no_webp_url(url_list)
    
    result = {
        'title': data.get('desc', ''),
        'video_url': video_url,
        'cover_url': cover_url,
        'images': images,
        'author': {
            'uid': data.get('author', {}).get('sec_uid', ''),
            'name': data.get('author', {}).get('nickname', ''),
            'avatar': data.get('author', {}).get('avatar_thumb', {}).get('url_list', [None])[0],
        },
    }
    
    # 步骤5：获取302重定向之后的真实视频地址
    if result['video_url']:
        result['video_url'] = get_redirect_url(session, result['video_url'])
    
    if not result['video_url'] and not result['images']:
        raise Exception('没有作品')
    
    return result


def parse_app_share_url(share_url, session):
    """解析App分享链接"""
    # 禁用重定向，获取重定向前的参数
    response = session.get(share_url, allow_redirects=False, headers={'User-Agent': USER_AGENT}, timeout=30)
    
    if 300 <= response.status_code < 400:
        location = response.headers.get('Location')
        if location:
            parsed_location = urlparse(location)
            if parsed_location.path:
                video_id = parse_video_id_from_path(parsed_location.path)
                if video_id:
                    # 检查是否是西瓜视频
                    if parsed_location.hostname and 'ixigua.com' in parsed_location.hostname:
                        raise Exception('西瓜视频暂不支持')
                    return parse_video_id(video_id, session)
    
    raise Exception('无法从分享链接中提取视频ID')


def parse_pc_share_url(share_url, session):
    """解析PC端分享链接"""
    video_id = parse_video_id_from_path(share_url)
    if not video_id:
        raise Exception('无法从URL中提取视频ID')
    return parse_video_id(video_id, session)


def parse_share_url(share_url, session):
    """解析分享链接"""
    parsed_url = urlparse(share_url)
    if not parsed_url.hostname:
        raise Exception('无效的URL')
    
    host = parsed_url.hostname
    
    if host in ['www.iesdouyin.com', 'www.douyin.com']:
        return parse_pc_share_url(share_url, session)
    elif host == 'v.douyin.com':
        return parse_app_share_url(share_url, session)
    else:
        raise Exception(f"不支持的域名: {host}")


def download_video(video_url, output_path, session):
    """下载视频"""
    response = session.get(video_url, headers={'User-Agent': USER_AGENT}, stream=True, timeout=60)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r下载进度: {percent:.1f}%", end='', flush=True)
    
    print()  # 换行
    return output_path


def main():
    parser = argparse.ArgumentParser(description='解析抖音分享链接，下载视频，并转成文字')
    parser.add_argument('url', type=str, help='抖音分享链接')
    parser.add_argument('--output-dir', type=str, default=None, help='输出目录，默认为当前工作目录下的 downloads/')
    parser.add_argument('--transcribe', action='store_true', help='是否转文字（需要安装FunASR）')
    parser.add_argument('--model', type=str, default='paraformer-zh', help='ASR模型，默认为 paraformer-zh')
    parser.add_argument('--vad-model', type=str, default='fsmn-vad', help='VAD模型，默认为 fsmn-vad')
    parser.add_argument('--punc-model', type=str, default='ct-punc', help='标点恢复模型，默认为 ct-punc')
    
    args = parser.parse_args()
    
    # 如果没有指定输出目录，智能判断下载位置
    if args.output_dir is None:
        current_cwd = Path.cwd().resolve()
        script_dir = Path(__file__).parent.resolve()
        skill_dir = script_dir.parent.resolve()  # skill根目录
        
        # 检测当前工作目录是否是skill目录（通过检查是否存在SKILL.md）
        # 大模型执行时会cd到skill目录，所以需要检测
        is_skill_dir = (current_cwd / "SKILL.md").exists() or \
                      (current_cwd == skill_dir) or \
                      (current_cwd == script_dir)
        
        if is_skill_dir:
            # 如果是在skill目录执行，使用用户主目录下的固定位置
            home_dir = Path.home()
            # 使用 Downloads/douyin-video-text 作为默认下载位置
            args.output_dir = str(home_dir / "Downloads" / "douyin-video-text")
            print(f"💡 检测到在skill目录执行，文件将保存到: {args.output_dir}")
        else:
            # 如果不在skill目录，使用当前工作目录（用户正常调用）
            args.output_dir = str(current_cwd / 'downloads')
    
    session = create_session()
    
    try:
        print(f"正在解析抖音分享链接: {args.url}")
        result = parse_share_url(args.url, session)
        
        print('解析成功！')
        print('')
        print('视频信息:')
        print(f'标题: {result.get("title", "未获取到")}')
        print(f'视频链接: {result.get("video_url", "无（图集）")}')
        print(f'封面: {result.get("cover_url", "未获取到")}')
        
        if result.get('images'):
            print('')
            print(f'图集图片 ({len(result["images"])} 张):')
            for index, image in enumerate(result['images']):
                print(f'  图片 {index + 1}: {image["url"]}')
                if image.get('live_photo_url'):
                    print(f'    Live Photo: {image["live_photo_url"]}')
        
        if result.get('author'):
            print('')
            print('作者信息:')
            print(f'昵称: {result["author"].get("name", "")}')
            print(f'UID: {result["author"].get("uid", "")}')
            print(f'头像: {result["author"].get("avatar", "")}')
        
        # 下载视频
        video_url = result.get('video_url')
        if video_url:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名（使用视频ID或标题）
            video_id = parse_video_id_from_path(args.url)
            if not video_id:
                video_id = 'video'
            filename = f"{video_id}.mp4"
            output_path = output_dir / filename
            
            print('')
            print(f'正在下载视频到: {output_path}')
            download_video(video_url, output_path, session)
            print(f'视频下载完成: {output_path}')
            
            # 转文字
            if args.transcribe:
                print('')
                print('正在转文字...')
                # 导入transcribe函数（从同目录的transcribe_audio_funasr.py）
                script_dir = Path(__file__).parent
                transcribe_script = script_dir / 'transcribe_audio_funasr.py'
                
                if transcribe_script.exists():
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("transcribe_audio_funasr", transcribe_script)
                    transcribe_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(transcribe_module)
                    
                    transcribe_result = transcribe_module.transcribe_audio(
                        str(output_path),
                        model=args.model,
                        vad_model=args.vad_model,
                        punc_model=args.punc_model
                    )
                    
                    if transcribe_result.get('code') == 'SUCCESS':
                        text = transcribe_result['data']['text']
                        print('')
                        print('转文字成功！')
                        print('识别文本:')
                        print(text)
                        
                        # 保存文本到文件
                        text_file = output_path.with_suffix('.txt')
                        text_file.write_text(text, encoding='utf-8')
                        print(f'文本已保存到: {text_file}')
                    else:
                        print(f'转文字失败: {transcribe_result.get("message", "未知错误")}')
                else:
                    print(f'警告: 找不到 transcribe_audio_funasr.py 文件: {transcribe_script}')
        else:
            print('')
            print('注意: 这是图集，没有视频可下载')
        
        # 输出JSON格式结果
        print('')
        print('JSON格式:')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return 0
        
    except Exception as e:
        print(f'解析失败: {str(e)}', file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
