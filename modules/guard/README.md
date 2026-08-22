# Guard

Control de alcance y archivos. Es la primera línea de defensa: evita que un agente
toque paths críticos (infraestructura, CI/CD, migraciones) o archivos secretos,
sin importar cuán "razonable" le haya parecido el cambio.

## Requisitos

```bash
pip install pyyaml
```

## Uso

```bash
# Evaluar el estado actual del working tree contra ironchain.yaml
python modules/guard/guard.py

# Comparar contra una rama base (útil en CI)
python modules/guard/guard.py --base-ref origin/main
```

Código de salida `0` = OK. Código de salida `1` = violación (bloquea el pipeline
o el hook). Código de salida `2` = error de configuración (falla cerrado).

## Instalación como git hook

```bash
cp scripts/install.sh . && bash install.sh
```

Esto agrega Guard como `pre-commit`, así ningún commit —humano o de agente—
pasa sin ser evaluado primero.

## Override humano

Si una excepción es legítima, un humano puede setear la variable definida en
`allow_override_env` (por defecto `IRONCHAIN_ALLOW_OVERRIDE`) antes de reintentar.
El bypass queda impreso en el log de forma explícita, nunca es silencioso.
