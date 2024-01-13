import asyncio
import os

import aiohttp

from logger import get_logger

logger = get_logger(__name__)


class OpenApi:
    def __init__(self, token):
        self.base_url = os.environ.get("OPENAI_API_URL")
        self.headers = {"X-API-Key": "admin", "Authorization": f"Bearer {token}"}

    async def process_file(self, data):
        """
        {
          "brain_id": "AAAAA1",
          "filename": "sample.pdf",
          "filepath": "sample.pdf",
          "filetype": "pdf",
          "chunk_size": 1000,
          "chunk_overlap": 100,
          "file_id": "jgyf",
          "supabase_file_name": "sadsc",
          "supabase_bucket_name": "sdscs"
        }
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/process_file",
                json=data,
                headers=self.headers,
                # proxy="http://127.0.0.1:7890",
            ) as response:
                text = await response.text()
                logger.info(f"process_file,args:{data},result:{text}")
                rs = await response.json()
                logger.info(f"process_file,args:{data},result:{rs}")
                return rs

    async def delete_vector(self, data):
        """
        {
          "brain_id": "AAAAA1",
          "filename": "sample.pdf"
        }
        """
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/delete_vector",
                json=data,
                headers=self.headers,
                # proxy="http://127.0.0.1:7890",
            ) as response:
                text = await response.text()
                logger.info(f"delete_vector,args:{data},result:{text}")
                rs = await response.json()
                logger.info(f"delete_vector,args:{data},result:{rs}")
                return rs

    async def chat_qa(self, data):
        """
        {
          "brain_id": "AAAAA1",
          "chat_id": "chat1234",
          "question": "what is the future of smart city?"
        }
        """
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.base_url}/chat_qa", json=data, headers=self.headers
            ) as response:
                text = await response.text()
                logger.info(f"chat_qa,args:{data},result:{text}")
                rs = await response.json()
                logger.info(f"chat_qa,args:{data},result:{rs}")
                return rs
        # 需要关注结果

    async def process_file_m(self, data):
        """
        {
          "brain_id": "AAAAA1",
          "filename": "sample.pdf",
          "filepath": "sample.pdf",
          "filetype": "pdf",
          "chunk_size": 1000,
          "chunk_overlap": 100,
          "file_id": "jgyf",
          "supabase_file_name": "sadsc",
          "supabase_bucket_name": "sdscs"
        }
        """
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.base_url}/process_file_m",
                json=data,
                headers=self.headers,
                # proxy="http://127.0.0.1:7890",
            ) as response:
                text = await response.text()
                logger.info(f"process_file,args:{data},result:{text}")
                rs = await response.json()
                logger.info(f"process_file,args:{data},result:{rs}")
                return rs

    async def delete_vector_m(self, data):
        """
        {
          "brain_id": "AAAAA1",
          "filename": "sample.pdf"
        }
        """
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/delete_vector_m",
                json=data,
                headers=self.headers,
                # proxy="http://127.0.0.1:7890",
            ) as response:
                text = await response.text()
                logger.info(f"delete_vector,args:{data},result:{text}")
                rs = await response.json()
                logger.info(f"delete_vector,args:{data},result:{rs}")
                return rs

    async def chat_qa_m(self, data):
        """
        {
          "brain_id": "AAAAA1",
          "chat_id": "chat1234",
          "question": "what is the future of smart city?"
        }
        """
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.base_url}/chat_qa_m", json=data, headers=self.headers
            ) as response:
                text = await response.text()
                logger.info(f"chat_qa,args:{data},result:{text}")
                rs = await response.json()
                logger.info(f"chat_qa,args:{data},result:{rs}")
                return rs
        # 需要关注结果


if __name__ == "__main__":
    data = {
        "brain_id": "AAAAA1",
        "filename": "sample.pdf",
        "filepath": "sample.pdf",
        "filetype": "pdf",
        "chunk_size": 1000,
        "chunk_overlap": 100,
        "file_id": "jgyf",
        "supabase_file_name": "sadsc",
        "supabase_bucket_name": "sdscs",
    }
    # while 1:
    asyncio.run(OpenApi("adsfsafs").process_file(data))
