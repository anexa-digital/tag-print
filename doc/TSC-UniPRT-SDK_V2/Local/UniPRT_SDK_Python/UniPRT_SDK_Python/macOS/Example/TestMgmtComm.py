from UniPRT.Comm.TcpComm import TcpComm
from UniPRT.Comm.UsbComm import UsbComm,UsbConnection
from UniPRT.Json.JsonMng import JsonMessenger, CommType, JsonMng, JsonComm
from UniPRT.Json.SettingsReadWrite import SettingsReadWrite, Setting
from UniPRT.Json.JsonConfig import Config, JsonConfig

MAX_INPUT_MSG_CAPACITY = 20
MAX_WAIT_TIME_SECS = 10


def main() -> None:
    usb_connection = UsbConnection()
    devices = usb_connection.available_devices()
    print(f"Available Devices: {devices}")
    vendor_id = devices[0][0]
    product_id = devices[0][1]

    # USB
    comm = UsbComm(vendor_id=vendor_id, product_id=product_id)
    commTyp = CommType.USB_COMM

    # TCP
    comm = TcpComm("192.168.101.62", 3007)
    commTyp = CommType.TCP_COMM
    comm.open()
    if comm.is_connected():
        json_messenger = JsonMessenger(
            comm_to_ptr=comm,
            comm_type=commTyp,
            max_input_msg_capacity=MAX_INPUT_MSG_CAPACITY,
            using_data_port=True,
        )
        command = "Cfg.Prop"
        content = '{\r\n"all" : null\r\n}\r\n'
        print(
            f'\r\nSend to Printer:\r\n"Command": "{command}"\r\n"Content":\r\n{content}'
        )
        track_number: JsonMng = (
            json_messenger.send_msg_and_wait_for_response_with_command(
                command=command, content=content, max_wait_time_secs=MAX_WAIT_TIME_SECS
            )
        )

        if track_number:
            received_string = track_number.str_response
            print(f"receivedString:{received_string}")

        # Setting Read Write
        json_comm = JsonComm(comm_to_ptr=comm, comm_type=commTyp)
        json_comm.set_using_data_port(True)
        setting = SettingsReadWrite(connection=comm)
        key = setting.get_value_for_key("Printer.Model")
        print(f"single key:{key}")

        keys = setting.get_values_for_keys(["BT.PairMethod", "BT.ConnectName"], 3000)
        print(f"keys::::{keys}")

        set_key = setting.set_value(value="BT-PTX5", key="BT.ConnectName", timeout=3000)
        print(f"set_key::::{set_key}")

        set_keys = setting.set_values(
            {"BT.PairMethod": "eNumericComp", "BT.ConnectName": "BT-PTX3"}, 3000
        )
        print(f"setkeys:::::{set_keys}")

        allprop = setting.get_all_properties(timeout=30000)
        print(f"allprop::\r\n{allprop}")

        prop = setting.get_properties_for_key("Printer.Model", timeout=3000)
        print(f"prop::\r\n{prop}")

        props = setting.get_properties_for_keys(["Printer.Firm.Version", "Printer.Status"], timeout=3000)
        print(f"props::{props}")


        #Only PTX can use these command under below.  
        config_cls = JsonConfig(connection=comm)

        config = config_cls.get_config_with_number(0, timeout=30000)
        print(f"allcfg::{config.to_string()}")
        config.set_name("43244343243")
        set_config = config_cls.set_config(config)
        print(f"set cfg::{set_config}")
        all_cfg = config_cls.get_all_config()
        print(f"{all_cfg}")

    print("NONE")


if __name__ == "__main__":
    main()
