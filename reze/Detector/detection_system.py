from pymodbus.client import ModbusTcpClient
import time
from datetime import datetime

TARGET = '127.0.0.1'
PORT = 502
POLL_INTERVAL = 0.05
TANK_JUMP_THRESHOLD = 50  # change above 50 = attack

client = ModbusTcpClient(TARGET, port=PORT)
client.connect()

print("=" * 40)
print("    ICS DETECTOR   ")
print("=" * 40)
print("\n[*] Monitoring OpenPLC registers...")
print("    Press Ctrl+C to stop\n")

# Baseline
baseline_regs = client.read_holding_registers(address=0, count=8).registers
baseline_coils = client.read_coils(address=0, count=8).bits[:8]
print(f"    Baseline Registers: {baseline_regs}")
print(f"    Baseline Coils: {list(baseline_coils)}\n")

prev_regs = list(baseline_regs)

try:
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        regs = client.read_holding_registers(address=0, count=8).registers
        coils = client.read_coils(address=0, count=8).bits[:8]

        # Check for HVAC coil manipulation first (Priority)
        hvac_attack_detected = False
        for i, (current, base) in enumerate(zip(coils, baseline_coils)):
            if current != base:
                print(f"[{timestamp}] [ATTACK] Coil {i} manipulated: {base} → {current}")
                hvac_attack_detected = True

        # Tank jump detection (Only if change is above 50)
        # Reports if there is no HVAC threat OR if both are happening
        for i, (current, prev) in enumerate(zip(regs, prev_regs)):
            jump = abs(current - prev)
            if jump > TANK_JUMP_THRESHOLD:
                print(f"[{timestamp}] [ATTACK] Register {i} jumped by {jump}: {prev} → {current}")

        prev_regs = list(regs)

        print(f"[{timestamp}] [OK] Regs={list(regs[:4])} Coils={list(coils[:4])}", end='\r')

        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    print("\n\n[*] Detector stopped.")
    client.close()
