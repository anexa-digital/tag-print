# Estructura de Codificación EPC — Empacor RFID

## Resumen

Esquema para codificar códigos de despacho tipo `PVE-219836-WAR-3270806` en los 96 bits (12 bytes = 24 caracteres hex) del EPC de un tag RFID UHF.

---

## Estructura (24 hex chars)

| Posición | Largo | Contenido | Valores | Ejemplo |
|----------|-------|-----------|---------|---------|
| 0-1 | 2 | Formato/versión | EA-EF (solo letras hex) | `EA` = versión 1 |
| 2-3 | 2 | Prefijo 1 (tipo documento) | AA-AF (solo letras hex) | `AA` = PVE |
| 4-12 | 9 | Número 1 | Dígitos planos, zero-pad | `000219836` |
| 13-14 | 2 | Prefijo 2 (tipo ubicación) | BA-BF (solo letras hex) | `BB` = WAR |
| 15-23 | 9 | Número 2 | Dígitos planos, zero-pad | `003270806` |

**Total: 2 + 2 + 9 + 2 + 9 = 24 hex chars = 12 bytes = 96 bits**

---

## Diseño visual

```
E A A A 0 0 0 2 1 9 8 3 6 B B 0 0 3 2 7 0 8 0 6
└─┘ └─┘ └────────────┘ └─┘ └────────────┘
 EA  AA   000219836     BB   003270806
 │    │      │           │      │
 │    │      │           │      └─ 3270806 (zero-pad a 9 dígitos)
 │    │      │           └─ BB = WAR
 │    │      └─ 219836 (zero-pad a 9 dígitos)
 │    └─ AA = PVE
 └─ EA = Empacor formato v1
```

EPC hex resultante: `EAAA000219836BB003270806`

---

## Criterios de diseño

- **Pos 0-1 inicia con E**: La letra E identifica que el tag fue grabado por Empacor. El segundo carácter es la versión del formato (A=v1, B=v2...). Si la estructura cambia en el futuro, se incrementa la versión.
- **Solo letras hex (A-F) en identificadores**: Los bytes de metadata usan exclusivamente A-F, lo que los separa visualmente de los números (0-9) al leer un EPC en hex.
- **Números planos**: Los dígitos del número se colocan tal cual en el hex string, zero-padded a 9 posiciones. Se leen directamente sin conversión.
- **9 dígitos por número**: Soporta valores hasta 999,999,999. Suficiente para los 6 dígitos del primer grupo y 7 del segundo, con margen.

---

## Tablas de mapeo de prefijos

### Prefijo 1 — Tipo de documento (posición 2-3)

| Hex | Prefijo | Descripción |
|-----|---------|-------------|
| AA | PVE | |
| AB | PVZ | |
| AC | PVI | |
| AD | *(reservado)* | |
| AE | *(reservado)* | |
| AF | *(reservado)* | |

### Prefijo 2 — Tipo de ubicación (posición 13-14)

| Hex | Prefijo | Descripción |
|-----|---------|-------------|
| BA | DIR | |
| BB | WAR | |
| BC | DEV | |
| BD | AJU | |
| BE | *(reservado)* | |
| BF | *(reservado)* | |

> Nota: Hay capacidad para hasta 36 combinaciones por grupo (AA-FF con solo letras A-F).
> Por ahora se usan rangos AA-AF y BA-BF (6 por grupo). Si se necesitan más, se pueden
> extender a CA-CF, DA-DF, etc.

---

## Formato de versión (posición 0-1)

| Hex | Versión | Notas |
|-----|---------|-------|
| EA | v1 | Estructura actual (2+2+9+2+9) |
| EB | v2 | *(reservado para cambios futuros)* |
| EC | v3 | *(reservado)* |
| ED | v4 | *(reservado)* |
| EE | v5 | *(reservado)* |
| EF | v6 | *(reservado)* |

---

## Encode (código → EPC hex)

Entrada: `PVE-219836-WAR-3270806`

1. Parsear por guiones: `["PVE", "219836", "WAR", "3270806"]`
2. Lookup prefijo 1: `PVE` → `AA`
3. Zero-pad número 1 a 9 dígitos: `219836` → `000219836`
4. Lookup prefijo 2: `WAR` → `BB`
5. Zero-pad número 2 a 9 dígitos: `3270806` → `003270806`
6. Concatenar: `EA` + `AA` + `000219836` + `BB` + `003270806`
7. Resultado: `EAAA000219836BB003270806`

---

## Decode (EPC hex → código)

Entrada: `EAAA000219836BB003270806`

1. Validar que inicia con `E` (tag Empacor)
2. Leer pos 0-1: `EA` → formato v1
3. Leer pos 2-3: `AA` → lookup inverso → `PVE`
4. Leer pos 4-12: `000219836` → trim leading zeros → `219836`
5. Leer pos 13-14: `BB` → lookup inverso → `WAR`
6. Leer pos 15-23: `003270806` → trim leading zeros → `3270806`
7. Resultado: `PVE-219836-WAR-3270806`

---

## Más ejemplos

| Código original | EPC hex |
|---|---|
| `PVE-219836-WAR-3270806` | `EAAA000219836BB003270806` |
| `PVZ-001234-DIR-0000001` | `EAAB000001234BA000000001` |
| `PVI-999999-DEV-9999999` | `EAAC000999999BC009999999` |
| `PVE-100000-AJU-5555555` | `EAAA000100000BD005555555` |
