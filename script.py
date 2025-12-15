import sys
import json
import struct
import argparse

# === ОПЕРАЦИИ ===
OP_CODES = {
    "load": 31,
    "read": 121,
    "write": 26,
    "rol": 8
}

def parse_instruction(instr):
    op = instr["op"]
    a = OP_CODES[op]
    if op == "load":
        b = instr["const"]
        # 23 бита для константы => маска 0x7FFFFF
        if b < 0 or b > 0x7FFFFF:
            raise ValueError(f"Константа {b} выходит за пределы 23 бит")
        return (a, b, 4)
    elif op in ("read", "write", "rol"):
        b = instr["addr"]
        # 16 бит для адреса => маска 0xFFFF
        if b < 0 or b > 0xFFFF:
            raise ValueError(f"Адрес {b} выходит за пределы 16 бит")
        return (a, b, 3)
    else:
        raise ValueError(f"Неизвестная операция: {op}")

def assemble_to_intermediate(source_path):
    with open(source_path, "r", encoding="utf-8") as f:
        program = json.load(f)
    intermediate = []
    for instr in program:
        a, b, size = parse_instruction(instr)
        intermediate.append({"a": a, "b": b, "size": size})
    return intermediate

def serialize_instruction(a, b, size):
    if size == 4:
        # 7 бит A + 23 бита B = 30 бит → 4 байта
        value = (b << 7) | a
        return struct.pack('<I', value)  # Little-endian, 4 байта
    elif size == 3:
        # 7 бит A + 16 бит B = 23 бита → 3 байта
        value = (b << 7) | a
        return value.to_bytes(3, byteorder='little')
    else:
        raise RuntimeError("Неверный размер команды")

def main():
    parser = argparse.ArgumentParser(description="Ассемблер УВМ (вариант 29)")
    parser.add_argument("input", help="Путь к входному JSON-файлу")
    parser.add_argument("output", help="Путь к выходному бинарному файлу")
    parser.add_argument("--test", action="store_true", help="Режим тестирования")
    args = parser.parse_args()

    # Этап 1: промежуточное представление
    intermediate = assemble_to_intermediate(args.input)

    # Этап 2: сериализация в машинный код
    machine_code = b""
    for item in intermediate:
        machine_code += serialize_instruction(item["a"], item["b"], item["size"])

    # Запись в файл
    with open(args.output, "wb") as f:
        f.write(machine_code)

    print(f"Ассемблировано команд: {len(intermediate)}")

    # Тестовый вывод
    if args.test:
        print("Машинный код (в hex):")
        for i, byte in enumerate(machine_code):
            if i % 16 == 0 and i > 0:
                print()
            print(f"0x{byte:02X}, ", end="")
        print("\n")

if __name__ == "__main__":
    main()