# Verify (WIP)

Anti-Slopsquat. Valida la autenticidad y reputación de un paquete **antes**
de que el agente lo instale, para frenar el patrón de "el agente alucina un
nombre de paquete parecido a uno real y lo instala igual" (slopsquatting).

## Estado

🚧 En diseño. La primera versión funcional interceptará `npm install` / `pip
install` y chequeará contra el registro correspondiente:

- Antigüedad mínima del paquete (`min_package_age_days`).
- Descargas semanales mínimas (`min_weekly_downloads`).
- Similitud (distancia de edición) con paquetes populares, para detectar
  typosquatting.
- Existencia real del paquete (evita instalar nombres alucinados).

La configuración vive en la sección `verify:` de `ironchain.yaml`.
