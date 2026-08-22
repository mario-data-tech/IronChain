# Schema (WIP)

Validación de contratos. Detecta cuando un agente modifica un tipo, un modelo
Zod/Prisma o un endpoint de forma tal que rompe a los consumidores existentes
(frontend, otros servicios, clientes externos).

## Estado

🚧 En diseño. La primera versión funcional comparará snapshots del schema
(`prisma/schema.prisma`, tipos exportados, `openapi.yaml`) antes/después del
cambio del agente, y marcará como violación cualquier:

- Campo removido o renombrado sin migración.
- Tipo estrechado de forma incompatible (ej: `string | null` → `string`).
- Endpoint eliminado o con firma de respuesta alterada.

La configuración vive en la sección `schema:` de `ironchain.yaml`.
