import datetime
from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    BlobSasPermissions,
    generate_blob_sas,
)
from conf.settings import backend_settings


class SAS:
    @staticmethod
    def create_service_sas_blob(blob_client: BlobClient, account_key: str):
        start_time = datetime.datetime.now(datetime.timezone.utc)
        expiry_time = start_time + datetime.timedelta(days=1)

        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=blob_client.container_name,
            blob_name=blob_client.blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=expiry_time,
            start=start_time,
        )

        return sas_token

    def use_service_sas_blob(
        self, container_name, blob, blob_service_client: BlobServiceClient
    ):
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob
        )
        sas_token = self.create_service_sas_blob(
            blob_client=blob_client,
            account_key=blob_service_client.credential.account_key,
        )
        return f"{blob_client.url}?{sas_token}"


def get_asa_url(container_name, blob):
    sas = SAS()
    account_url = backend_settings.azure_storage_url
    account_key = backend_settings.azure_storage_key
    blob_service_client_account_key = BlobServiceClient(
        account_url, credential=account_key
    )

    url = sas.use_service_sas_blob(
        container_name=container_name,
        blob=blob,
        blob_service_client=blob_service_client_account_key,
    )
    return url
