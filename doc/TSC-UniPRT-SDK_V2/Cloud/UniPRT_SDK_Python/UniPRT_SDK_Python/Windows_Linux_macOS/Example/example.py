from UniPRT_Cloud.Comm.MqttComm import MqttComm, DataTransferType
import asyncio


async def callback(topic, payload):
    print(payload)
    print(topic)


async def main():
    x = MqttComm(
        "BROKER_URL",
        8883,
        "USER",
        "PASSWORD",
        "CA.CRT FILE",
        "CLIENT.CRT FILE",
        "CLIENT.KEY FILE",
    )

    await x.open()
    await x.read("#", callback)

    message = ["PRINT 1"]

    write_request = MqttComm.make_tsc_data_transfer_bulk(message, DataTransferType.TEXT)
    print(f"WRITE REQUEST:::::{write_request}")
    await x.write("test", write_request[0])

    pcl_request = MqttComm.make_tsc_data_pcl_command("EPL")
    print(f"PCL REQUEST:::::{pcl_request}")

    download_file_request = MqttComm.make_tsc_download_file_command("test.com/aaa.png")
    print(f"DOWNFILE REQUEST::::{download_file_request}")

    abort_request = MqttComm.make_tsc_abort_command()
    print(f"ABORT REQUEST{abort_request}")


asyncio.run(main())
