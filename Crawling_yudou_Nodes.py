import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime

# 获取文章列表页的所有文章链接
def get_article_links(base_url="https://www.yudou66.cc/"):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = [a['href'] for a in soup.select("article h2 a") if a['href'].startswith("http")]
    return links

# 提取txt链接
def get_txt_link(article_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(article_url, headers=headers)
    if resp.status_code != 200:
        return None
    match = re.search(r'https://yy\.yudou66\.top/\d{6}/\d{8}.*?\.txt', resp.text)
    return match.group(0) if match else None

# 验证txt文件内容是否有效
def is_valid_txt(content):
    # 检查内容是否为空，或者是否包含无效的词语（例如“测试”，“删除”等）
    if not content.strip():  # 内容为空
        return False
    invalid_keywords = ["测试", "删除", "合成"]
    for keyword in invalid_keywords:
        if keyword in content:
            return False
    return True

# 下载并保存有效的txt文件，使用时间戳确保文件名唯一
def download_and_save_txt(url):
    filename = url.split("/")[-1]
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # 为了确保文件名唯一，添加时间戳（年月日时分秒）
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{filename}"
    
    # 构建保存文件的完整路径
    file_path = os.path.join(script_dir, filename)
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text
            # 验证文件内容是否有效
            if is_valid_txt(content):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ 保存成功: {file_path}")
            else:
                print("❌ 文件内容无效，未保存")
        else:
            print(f"❌ 无法下载: {url}")
    except Exception as e:
        print(f"⚠️ 下载失败: {url}，错误信息: {e}")

# 主程序
if __name__ == "__main__":
    print("📥 开始爬取文章页面...")
    articles = get_article_links()
    print(f"🔗 共找到 {len(articles)} 篇文章，开始处理第1篇...")

    # 只爬取第一个有效的txt文件
    for url in articles:
        print(f"\n🔍 处理文章: {url}")
        txt_link = get_txt_link(url)
        if txt_link:
            print(f"📄 找到TXT链接: {txt_link}")
            download_and_save_txt(txt_link)
            break  # 找到第一个有效的文件后就停止
        else:
            print("🚫 没有找到TXT链接")
