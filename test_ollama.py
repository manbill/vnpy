from ollama import chat
from ollama import ChatResponse
from ollama import Client
import asyncio
from ollama import AsyncClient
import requests
from bs4 import BeautifulSoup
from ollama import chat
from pydantic import BaseModel 
from typing import Literal, Optional,List
def llama32():
  response: ChatResponse = chat(model='llama3.2', messages=[
    {
      'role': 'user',
      'content': 'Why is the sky blue? 用中文回答',
    },
  ])
  # print(response['message']['content'])
  # or access fields directly from the response object
  print(response.message.content)

def streaming():
  stream = chat(
      model='llama3.2',
      messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
      stream=True,
  )

  for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)
    
def client():
  client = Client(
    host='http://localhost:11434',
    headers={'x-some-header': 'some-value'}
  )
  response = client.chat(model='llama3.2', messages=[
    {
      'role': 'user',
      'content': 'Why is the sky blue? 用中文回答',
    },
  ])
  print(response.message.content)
  
def asyncClient():
  async def chat():
    message = {'role': 'user', 'content': 'Why is the sky blue?'}
    response = await AsyncClient().chat(model='llama3.2', messages=[message])

  asyncio.run(chat())
  
  
def streamingAsync():
  async def chat():
    message = {'role': 'user', 
               'content': 'Why is the sky blue?'}
    async for part in await AsyncClient().chat(model='llama3.2', messages=[message], stream=True):
      print(part['message']['content'], end='', flush=True)

  asyncio.run(chat())
  


class Object(BaseModel):
    name: str
    confidence: float
    attributes: str

class ImageDescription(BaseModel):
    summary: str
    objects: List[Object]
    scene: str
    colors: List[str]
    time_of_day: Literal['Morning', 'Afternoon', 'Evening', 'Night']
    setting: Literal['Indoor', 'Outdoor', 'Unknown']
    text_content: Optional[str] = None
    
def image_roc():
    # 假设这是一个网页的 URL
    url = 'https://example.com/page-with-image'

    # 发送请求获取网页内容
    response = requests.get(url)
    html_content = response.text

    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 假设图片在某个特定的标签中，例如 <img> 标签
    image_tag = soup.find('img')  # 你可以使用更具体的条件来定位图片标签
    if image_tag and 'src' in image_tag.attrs:
        image_url = image_tag['src']
    else:
        raise ValueError("Image not found or no 'src' attribute in the image tag")

    # 如果图片 URL 是相对路径，转换为绝对路径
    if image_url.startswith('/'):
        base_url = '{uri.scheme}://{uri.netloc}'.format(uri=response.url)
        image_url = base_url + image_url

    # 将图片 URL 传递给 chat 函数
    response = chat(
        model='llama3.2-vision',
        format=ImageDescription.model_json_schema(),  # 传递响应的 schema
        messages=[
            {
                'role': 'user',
                'content': 'Analyze this image and describe what you see, including any objects, the scene, colors and any text you can detect.',
                'images': [image_url],
            },
        ],
        options={'temperature': 0},  # 设置温度为 0 以获得更确定的输出
    )

    # 解析响应内容
    image_description = ImageDescription.model_validate_json(response.message.content)
    print(image_description)
if __name__=='__main__':
    client()