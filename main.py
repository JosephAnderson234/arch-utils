#!/usr/bin/env python3
import struct, argparse
import numpy as np

def to_hex_bits(v, bits):
    if bits == 32:
        u = int.from_bytes(struct.pack('!f', np.float32(v).item()), 'big')
        return f'0x{u:08x}', f'{u:032b}'
    else:
        u = np.float16(v).view(np.uint16).item()
        return f'0x{u:04x}', f'{u:016b}'

def group_bits(s):
    """Recibe una cadena de bits (por ejemplo '01010101') y la devuelve agrupada en 4 en 4.
    También acepta cadenas con prefijo '0x' (devuelve la representación binaria agrupada).
    """
    # si vienen con 0x, asumimos que son hex y convertimos a bin
    if s.startswith('0x'):
        # convertir hex a int y luego a bin con longitud múltiplo de 4
        width = (len(s) - 2) * 4
        val = int(s[2:], 16)
        b = f"{val:0{width}b}"
    else:
        b = s
    # agrupar en 4
    parts = [b[i:i+4] for i in range(0, len(b), 4)]
    return ' '.join(parts)

def cast(v, bits):
    return np.float32(v) if bits == 32 else np.float16(v)

def operate(a, b, bits, op):
    A = cast(a, bits)
    B = cast(b, bits)
    if op == 'sum':
        C = cast(A + B, bits)
    elif op == 'sub':
        C = cast(A - B, bits)
    elif op == 'mul':
        C = cast(A * B, bits)
    elif op == 'div':
        C = cast(A / B, bits)
    else:
        raise ValueError("Unsupported op")
    return A, B, C

def main():
    ap = argparse.ArgumentParser(description="Operaciones decimales en IEEE-754 half/single")
    ap.add_argument("a", type=float, help="Operando A (decimal base 10)")
    ap.add_argument("b", type=float, help="Operando B (decimal base 10)")
    ap.add_argument("--bits", type=int, choices=[16,32], required=True, help="Formato IEEE: 16=half, 32=single")
    ap.add_argument("--op", type=str, choices=["sum","sub","mul","div"], default="sum",
                    help="Operación: sum (por defecto), sub, mul, div")
    ap.add_argument("--hex-only", dest="hex_only", action="store_true",
                    help="Imprime solo: A_hex B_hex R_hex")
    ap.add_argument("--csv", action="store_true", help="Imprime CSV: a_hex,b_hex,r_hex (sin 0x)")
    args = ap.parse_args()

    A, B, R = operate(args.a, args.b, args.bits, args.op)
    ahex, abits = to_hex_bits(A, args.bits)
    bhex, bbits = to_hex_bits(B, args.bits)
    rhex, rbits = to_hex_bits(R, args.bits)

    if args.csv:
        print(f"{ahex[2:]},{bhex[2:]},{rhex[2:]}")
        return

    if args.hex_only:
        print(f"{ahex} {bhex} {rhex}")
        return

    op_sym = {"sum":"+","sub":"-","mul":"*","div":"/"}[args.op]
    print(f"Formato: IEEE-{args.bits}  |  Op: {args.op} ({op_sym})")
    print("---------------------------------------------")
    print(f"A = {A} -> {ahex}  bits={group_bits(abits)}")
    print(f"B = {B} -> {bhex}  bits={group_bits(bbits)}")
    print("---------------------------------------------")
    print(f"R = A {op_sym} B = {R} -> {rhex}  bits={group_bits(rbits)}")

if __name__ == "__main__":
    main()
