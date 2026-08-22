# IronChain

**Policy-as-Code Engine para Agentes de Desarrollo IA.**

IronChain no es una herramienta de *vibe coding*. No te ayuda a "prompt-ear
mejor" ni a que el agente adivine tus intenciones. Es una capa de control
que se ejecuta **antes de que un agente (Claude Code, Cursor, Copilot Workspace,
etc.) pueda dar por finalizado un cambio**, y que verifica ese cambio contra
políticas explícitas, versionadas y auditables — igual que harías con
Terraform, OPA/Rego o cualquier otro motor de Policy-as-Code en infraestructura.

La premisa es simple: **un agente de IA puede escribir código correcto y
seguir siendo peligroso**. Puede tocar un archivo que no debía, romper un
contrato de datos que otro servicio consume, o instalar una dependencia
alucinada que ni siquiera existe (o que existe y es maliciosa). IronChain
existe para poner un límite duro ahí, sin depender de que el agente "se porte
bien".

## Arquitectura

```
ironchain/
├── ironchain.yaml              # Fuente única de verdad: políticas del repo
├── modules/
│   ├── guard/                  # Control de alcance y archivos
│   │   ├── guard.py
│   │   └── README.md
│   ├── schema/                 # Validación de contratos (WIP)
│   │   └── README.md
│   └── verify/                 # Anti-Slopsquat (WIP)
│       └── README.md
├── scripts/
│   └── install.sh              # Instala Guard como git hook
└── .github/
    └── workflows/
        └── ironchain-guard.yml # Integración lista para CI
```

Cada módulo es independiente y desacoplado: podés usar solo Guard hoy y sumar
Schema o Verify más adelante sin tocar nada existente. Ese es el punto de un
diseño plug-and-play — cada pieza se activa o desactiva declarando (o no) su
sección en `ironchain.yaml`.

## Módulos

| Módulo | Qué evita | Estado |
|---|---|---|
| **Guard** | Que el agente modifique paths críticos (`infra/`, CI/CD, migraciones) o archivos secretos (`.env`, claves, credenciales) | ✅ Funcional |
| **Schema** | Que el agente rompa contratos de datos (Zod, Prisma, tipos exportados, OpenAPI) sin que los consumidores se enteren | 🚧 En diseño |
| **Verify** | Que el agente instale un paquete alucinado o typosquateado (*slopsquatting*) antes de que llegue a tu `lockfile` | 🚧 En diseño |

## Quick start

```bash
git clone <tu-fork-de-ironchain>
cd tu-repo
cp ironchain.yaml.example ironchain.yaml   # o escribí el tuyo desde cero
pip install pyyaml

# Evaluación manual
python modules/guard/guard.py

# Instalación automática como pre-commit hook
bash scripts/install.sh
```

En CI, sumá `.github/workflows/ironchain-guard.yml` a tu repo y Guard corre en
cada Pull Request comparando contra la rama base.

## Filosofía de diseño

- **Falla cerrado, no abierto.** Si `ironchain.yaml` no existe o está mal
  formado, Guard bloquea. Preferimos un falso positivo a un agente sin freno.
- **Cero dependencias pesadas.** Guard usa únicamente `pyyaml`. Nada de
  frameworks, nada de servicios externos obligatorios.
- **Override humano, nunca de agente.** Cualquier excepción a una política
  requiere una variable de entorno seteada explícitamente por una persona, y
  queda registrada en el log — nunca es silenciosa.
- **Un archivo, una verdad.** `ironchain.yaml` es legible por humanos y por
  agentes. No hay estado oculto ni configuración implícita en otro lado.

## Roadmap

- [x] Guard v1 — control de alcance y archivos
- [ ] Schema v1 — diffing de contratos Zod/Prisma/OpenAPI
- [ ] Verify v1 — validación de paquetes contra npm/PyPI antes de instalar
- [ ] Reporte unificado (`ironchain report`) que agregue los tres módulos
- [ ] Integración nativa como *tool* invocable por Claude Code / Cursor

## Contribuir

Este es un proyecto open-source en etapa temprana. Issues y PRs son
bienvenidos, especialmente sobre los módulos Schema y Verify, que todavía
están en diseño. La única regla dura: cualquier feature nueva debe poder
desactivarse declarando o no su sección en `ironchain.yaml` — nada de
comportamiento forzado.

## Licencia

MIT (o la que definas para el repo).
