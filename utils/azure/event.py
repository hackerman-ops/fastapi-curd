# https://learn.microsoft.com/en-us/python/api/overview/azure/eventgrid-readme?view=azure-python

import os
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, EventGridEvent

key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

event = EventGridEvent(
    data={"team": "azure-sdk"},
    subject="Door1",
    event_type="Azure.Sdk.Demo",
    data_version="2.0",
)

credential = AzureKeyCredential(key)
client = EventGridPublisherClient(endpoint, credential)

client.send(event)
