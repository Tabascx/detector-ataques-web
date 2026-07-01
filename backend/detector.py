import re

PATTERNS = {
    "SQL Injection": [
        r"(?i)union(\s+all)?\s+select",
        r"(?i)or\s+1\s*=\s*1",
        r"(?i)'\s*or\s*'.*'\s*=\s*'",
        r"(?i)drop\s+table",
    ],
    "XSS": [
        r"(?i)<script.*?>",
        r"(?i)javascript:",
        r"(?i)on(error|load)\s*=",
    ],
    "Path Traversal": [
        r"\.\./\.\./",
        r"%2e%2e%2f",
    ],
    "Command Injection": [
        r";\s*(cat|whoami|rm|wget|curl)\b",
    ],
}

def analizar_linea(linea: str):
    for tipo_ataque, patrones in PATTERNS.items():
        for patron in patrones:
            if re.search(patron, linea):
                return tipo_ataque
    return None
