# https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=managed-identity%2Croles-azure-portal%2Csign-in-azure-cli

from azure.storage.blob.aio import BlobServiceClient
from conf.settings import backend_settings
import asyncio


class AzureBlobStorage:
    def __init__(self, container_name):
        self.container_name = container_name

        connect_url = backend_settings.azure_storage_connect_string
        self.blob_service_client = BlobServiceClient.from_connection_string(connect_url)

    async def create_container(self):
        await self.blob_service_client.create_container(self.container_name)
        print("\nContainer successfully created.\n")

    async def upload_file(self, blob_name, content, metadata):
        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        blob_client = container_client.get_blob_client(blob_name)
        await blob_client.upload_blob(
            data=content, metadata=metadata  # type: ignore
        )  # type: ignore

    async def delete_file(self, blob_name):
        blob_service_client = BlobServiceClient(
            backend_settings.azure_storage_url,
            credential=backend_settings.azure_storage_key,
        )
        container_client = blob_service_client.get_container_client(self.container_name)
        blob_client = container_client.get_blob_client(blob_name)
        await blob_client.delete_blob(delete_snapshots="include")  # type: ignore
