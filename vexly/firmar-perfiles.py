#!/usr/bin/env python3
"""Firma los perfiles de Vexly Remoto con la llave propia (secreto VEXLY_PERFIL_KEY).

Se corre al compilar, desde la raíz del repo, ANTES de compilar la parte de Rust:
  1. Lee la llave privada (32 bytes en base64) de la variable VEXLY_PERFIL_KEY.
  2. Firma vexly/perfiles/{cliente,tecnico}.json y escribe canela/custom-{cliente,tecnico}.txt,
     que es lo que ya leen todos los pasos de compilación.
  3. Pone la llave pública correspondiente en src/common.rs (solo en la copia del build).

Nunca imprime la llave privada. Requiere PyNaCl (libsodium, la misma que usa la app).
"""
import base64
import json
import os
import re
import sys

from nacl.signing import SigningKey, VerifyKey

RAIZ = os.getcwd()
COMMON = os.path.join(RAIZ, "src", "common.rs")
PATRON = re.compile(r'(const KEY: &str = ")([A-Za-z0-9+/=]{44})(";)')


def fallar(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


secreto = os.environ.get("VEXLY_PERFIL_KEY", "").strip()
if not secreto:
    fallar("falta el secreto VEXLY_PERFIL_KEY")
try:
    semilla = base64.b64decode(secreto, validate=True)
except Exception:
    fallar("VEXLY_PERFIL_KEY no es base64 valido")
if len(semilla) != 32:
    fallar(f"VEXLY_PERFIL_KEY debe tener 32 bytes y tiene {len(semilla)}")

llave = SigningKey(semilla)
publica = base64.b64encode(bytes(llave.verify_key)).decode()

# 1) Llave pública dentro de la app
codigo = open(COMMON, encoding="utf-8", newline="").read()  # conserva los saltos de línea
encontrados = PATRON.findall(codigo)
if len(encontrados) != 1:
    fallar(f"se esperaba 1 'const KEY' en src/common.rs y hay {len(encontrados)}")
codigo = PATRON.sub(lambda m: m.group(1) + publica + m.group(3), codigo)
open(COMMON, "w", encoding="utf-8", newline="").write(codigo)
print(f"llave publica de perfiles: {publica}")

# 2) Perfiles firmados
for variante in ("cliente", "tecnico"):
    origen = os.path.join(RAIZ, "vexly", "perfiles", f"{variante}.json")
    datos = json.load(open(origen, encoding="utf-8"))
    if datos.get("override-settings", {}).get("canela-variant") != variante:
        fallar(f"{origen}: canela-variant no dice '{variante}'")
    mensaje = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    firmado = bytes(llave.sign(mensaje))  # 64 bytes de firma + mensaje (formato libsodium)
    VerifyKey(base64.b64decode(publica)).verify(firmado)  # comprobación
    destino = os.path.join(RAIZ, "canela", f"custom-{variante}.txt")
    open(destino, "w", encoding="ascii", newline="").write(base64.b64encode(firmado).decode() + "\n")
    print(f"OK {destino} firmado")
