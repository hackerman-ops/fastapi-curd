#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving batch messages from a Service Bus Queue asynchronously.
"""

import asyncio
from azure.servicebus.aio import ServiceBusClient

CONNECTION_STR = "Endpoint=sb://asb-mtw-sea-np-core.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=rvLyI/aMxWaliXxIhGMmq3Q9HUglNFDMN+ASbHb6Ieg="
TOPIC_NAME = "egst-mtw-global-upload-trigger"


async def main():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:
        receiver = servicebus_client.get_subscription_receiver(
            topic_name=TOPIC_NAME, subscription_name="upload-trigger"
        )
        async with receiver:
            received_msgs = await receiver.receive_messages(
                max_message_count=10, max_wait_time=5
            )
            for msg in received_msgs:
                print(str(msg))
                await receiver.complete_message(msg)


asyncio.run(main())
