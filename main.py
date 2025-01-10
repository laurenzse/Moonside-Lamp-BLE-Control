import asyncio
from bleak import BleakScanner, BleakClient

lamp_name = "MOONSIDE-S1"
characteristic_description = "Nordic UART RX"

async def main():
    lamp_address = None
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == lamp_name:
            lamp_address = d.address
            break
    if lamp_address is None:
        print("Device not found")
        return
    async with BleakClient(lamp_address) as client:
        rx_characteristic = None
        for characteristic_index, characteristic in client.services.characteristics.items():
            if characteristic.description == characteristic_description:
                rx_characteristic = characteristic
                break
        if rx_characteristic is None:
            print("Characteristic not found")
            return
        command = "LEDOFF"
        hex_buffer_command = bytes.fromhex(command.encode('ascii').hex())
        await client.write_gatt_char(rx_characteristic, hex_buffer_command, response=True)

asyncio.run(main())