# IronChain Roadmap

Este documento define la visión estratégica y las fases de desarrollo de **IronChain**, el Policy-as-Code Engine agnóstico para agentes de desarrollo IA.

## 🏛️ Filosofía de Arquitectura

IronChain no es un framework de agentes ni un asistente de código. Es un **firewall de cambios** e infraestructura de control independiente. 

Cualquier agente (Claude Code, Cursor, Codex, etc.) o desarrollador humano escribe código, pero todo cambio pasa necesariamente por el filtro de IronChain antes de darse por finalizado.

[ Agentes / Cursor / Claude ] ──► [ Git Diff ] ──► [ IRONCHAIN ENGINE ]
│
┌───────────────┼───────────────┐
▼               ▼               ▼
[ GUARD ]       [ SCHEMA ]      [ VERIFY ]
│               │               │
└───────────────┼───────────────┘
▼
[ Policy Engine ]
│
┌────────────┴────────────┐
▼                         ▼
ALLOW                      DENY
(Exit 0)                  (Exit 1)
│
▼
Human Override

---

## 🗺️ Fases de Desarrollo

### 🟢 Fase 1 — Consolidación de Guard (Actual)
Objetivo: Hacer que el control de alcance y archivos sea robusto, simple e indestructible.
- [x] Control de rutas protegidas (`protected_paths`) mediante patrones glob.
- [x] Detección de archivos secretos o sensibles (`secret_files`).
- [x] Soporte para comparación contra working tree local o ramas base en CI.
- [x] Override humano auditable mediante variables de entorno explícitamente requeridas.
- [x] Integración lista como `pre-commit` hook local y GitHub Actions.

### 🟡 Fase 2 — Módulo Schema (Contratos de Datos)
Objetivo: Evitar que el agente rompa contratos que otros servicios o clientes consumen silenciosamente.
- [ ] Diffing estructural de esquemas y contratos de API.
- [ ] Soporte inicial para esquemas de **Prisma** (`schema.prisma`), validaciones de **Zod**, tipos exportados en TypeScript y especificaciones **OpenAPI**.
- [ ] Detección de campos eliminados, renombrados o estrechamientos de tipos incompatibles sin migración.

### 🟠 Fase 3 — Módulo Verify (Anti-Slopsquatting)
Objetivo: Proteger la cadena de suministro de software frente a la alucinación de dependencias por parte de los agentes.
- [ ] Intercepción de instalaciones (`npm install`, `pip install`).
- [ ] Validación de existencia real de paquetes en registros públicos (npm / PyPI) para frenar nombres alucinados.
- [ ] Análisis de metadatos: antigüedad del paquete (`min_package_age_days`) y umbrales mínimos de descarga.
- [ ] Detección de similitud y distancia de edición (typosquatting / slopsquatting) frente a paquetes populares.

### 🔵 Fase 4 — CLI Unificada (`ironchain check`)
Objetivo: Migrar de scripts desacoplados a una interfaz de línea de comandos centralizada.
- [ ] Implementación del comando global `ironchain check`.
- [ ] Reportes unificados de estado para Guard, Schema y Verify en un solo output estructurado.
- [ ] Estandarización completa del esquema del contrato central en `ironchain.yaml`.

---

## 🤝 Contribuir

Las contribuciones, issues y propuestas de diseño para las fases **Schema** y **Verify** son completamente bienvenidas. Por favor, asegúrate de mantener el principio de diseño: **falla cerrado y cero dependencias pesadas innecesarias.**
