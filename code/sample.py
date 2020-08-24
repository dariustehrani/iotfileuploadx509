import os
import asyncio
from six.moves import input
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import X509
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobClient

async def main():
    hostname = os.getenv("HOSTNAME")
    # The device that has been created on the portal using X509 CA signing or Self signing capabilities
    device_id = os.getenv("DEVICE_ID")

    x509 = X509(
        cert_file=os.getenv("X509_CERT_FILE"),
        key_file=os.getenv("X509_KEY_FILE"),
        pass_phrase=os.getenv("PASS_PHRASE"),
    )

    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_x509_certificate(
        hostname=hostname, device_id=device_id, x509=x509
    )

    # define behavior for receiving a message
    async def message_listener(device_client):
        while True:
            message = await device_client.receive_message()  # blocking call
            print("the data in the message received was ")
            print(message.data)
            print("custom properties are")
            print(message.custom_properties)

    # define behavior for halting the application
    def stdin_listener():
        while True:
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break

    # Schedule task for message listener
    asyncio.create_task(message_listener(device_client))

    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)

    # Wait for user to indicate they are done listening for messages
    await user_finished

    # Finally, disconnect
    await device_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

CONNECTION_STRING = os.getenv("CONNECTION_STRING", "nostring")
PATH_TO_FILE = r"[/pythoniot/azure.pdf]"

try:  
   os.environ["CONNECTION_STRING"]
except KeyError: 
   print ("Please set the connection string via docker environment")
   sys.exit(1)


async def store_blob(blob_info, file_name):
    try:
        sas_url = "https://{}/{}/{}{}".format(
            blob_info["hostName"],
            blob_info["containerName"],
            blob_info["blobName"],
            blob_info["sasToken"]
        )

        print("\nUploading file: {} to Azure Storage as blob: {} in container {}\n".format(file_name, blob_info["blobName"], blob_info["containerName"]))

        # Upload the specified file
        with BlobClient.from_blob_url(sas_url) as blob_client:
            with open(file_name, "rb") as f:
                result = blob_client.upload_blob(f, overwrite=True)
                return (True, result)

    except FileNotFoundError as ex:
        # catch file not found and add an HTTP status code to return in notification to IoT Hub
        ex.status_code = 404
        return (False, ex)

    except AzureError as ex:
        # catch Azure errors that might result from the upload operation
        return (False, ex)

async def main():
    try:
        print ( "IoT Hub file upload sample, press Ctrl-C to exit" )

        conn_str = CONNECTION_STRING
        file_name = PATH_TO_FILE
        blob_name = os.path.basename(file_name)

        device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

        # Connect the client
        await device_client.connect()

        # Get the storage info for the blob
        storage_info = await device_client.get_storage_info_for_blob(blob_name)

        # Upload to blob
        success, result = await store_blob(storage_info, file_name)

        if success == True:
            print("Upload succeeded. Result is: \n") 
            print(result)
            print()

            await device_client.notify_blob_upload_status(
                storage_info["correlationId"], True, 200, "OK: {}".format(file_name)
            )

        else :
            # If the upload was not successful, the result is the exception object
            print("Upload failed. Exception is: \n") 
            print(result)
            print()

            await device_client.notify_blob_upload_status(
                storage_info["correlationId"], False, result.status_code, str(result)
            )

    except Exception as ex:
        print("\nException:")
        print(ex)

    except KeyboardInterrupt:
        print ( "\nIoTHubDeviceClient sample stopped" )

    finally:
        # Finally, disconnect the client
        await device_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(main())
    #loop.close()