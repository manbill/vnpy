import requests
from bs4 import BeautifulSoup
import ollama
import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 初始化翻译器和概要生成器，使用本地部署的 ollama 模型
async def translator(text,target_language):
    response = ollama.chat('llama3.2',messages=[
    {
      'role': 'user',
      'content': f'英文翻译成中文：\n{text}',
    },
  ])
async def summarizer(text,max_length=150, min_length=30, do_sample=False):
    response = ollama.chat('llama3.2',messages=[
    {
      'role': 'user',
      'content': f'summarize the article\n{text}',
    },
  ])
    return response.message.content


# 设置 Chrome 选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
chrome_options.add_argument("--disable-gpu")

# 指定 ChromeDriver 的路径
chrome_driver_path = 'D:/vnpy/chromedriver.exe'
def get_driver(chrome_driver_path):
    try:
        # 创建 WebDriver 对象
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"获取driver出错: {str(e)}")
        exit()
driver=get_driver(chrome_driver_path)
# 抓取网页内容
# 1. 访问网页并等待加载完成
url = "https://www.bloomberg.com/latest?utm_source=homepage&utm_medium=web&utm_campaign=latest"
driver.get(url)
# 等待页面加载完成，可以使用显式等待或隐式等待
# 这里使用显式等待来等待特定元素出现
# 定义一个函数来等待包含特定子字符串类名的元素出现
def element_has_class(driver, class_substring):
    elements = driver.find_elements(By.XPATH, f"//*[contains(@class, '{class_substring}')]")
    return len(elements) > 0

# 等待新闻列表的 div 元素出现
try:
    WebDriverWait(driver, 10).until(lambda driver: element_has_class(driver, 'LineupContentArchiveFiltered_itemContainer'))
except Exception as e:
    print(f"页面加载出错: {str(e)}")
    driver.quit()
    exit()

# 获取页面内容
html_content = driver.page_source

# 2. 解析网页内容
news_div_elements = driver.find_elements(By.XPATH, f"//*[contains(@class, 'LineupContentArchiveFiltered_itemContainer')]")


if not news_div_elements:
    print("未找到新闻列表的 div 元素")
    driver.quit()
    exit()

# 提取新闻的标题、链接和时间
news_list = []
for news in news_div_elements:
    timestamp_elem = news.find_element(By.XPATH, ".//*[contains(@class, 'LineupContentArchiveFiltered_itemTimestamp')]")
    if timestamp_elem:
        timestamp = timestamp_elem.text.strip()
    else:
        timestamp = "未知时间"

    story_link_elem = news.find_element(By.XPATH, ".//*[contains(@class, 'LineupContentArchiveFiltered_storyLink') and @href]")
    if story_link_elem:
        news_title = story_link_elem.text.strip()
        news_url = story_link_elem.get_attribute('href')
        news_list.append((timestamp, news_title, news_url))
    else:
        continue

# 异步函数来获取新闻内容并生成概要
async def fetch_and_summarize(session, url):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return "未能获取新闻内容"
            news_html_content = await response.text()
            news_soup = BeautifulSoup(news_html_content, 'html.parser')
            news_article = news_soup.find('article')
            if news_article:
                news_text = news_article.get_text(separator=' ')
                # 生成新闻概要
                summary = await summarizer(news_text, max_length=150, min_length=30, do_sample=False)
                # 翻译新闻概要
                translated_summary = await translator(summary, target_language='zh')
                return translated_summary['translation']
            else:
                return "未能提取新闻内容"
    except Exception as e:
        return f"请求出错: {str(e)}"

# 异步主函数
async def main(news_list):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for timestamp, news_title, news_url in news_list:
            # 翻译新闻标题
            translated_title = await translator(news_title, target_language='zh')
            translated_title = translated_title['translation']
            task = fetch_and_summarize(session, news_url)
            tasks.append(task)

        # 等待所有任务完成
        translated_summaries = await asyncio.gather(*tasks)

        # 输出结果
        for (timestamp, news_title, news_url), translated_summary in zip(news_list, translated_summaries):
            print(f"时间: {timestamp}")
            print(f"新闻标题: {translated_title}")
            print(f"新闻概要: {translated_summary}")
            print("-" * 50)

# 运行异步主函数
if __name__ == "__main__":
    asyncio.run(main(news_list))