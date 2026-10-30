# innolexia-levantamiento

Instrumentos de levantamiento de información para la fase de diagnóstico y diseño de implementación de IA en firmas de abogados (InnoLexIA · Oscar Gutiérrez Saavedra, Consultor de IA y LegalTech).

## Páginas publicadas (GitHub Pages)

| Ruta | Cliente | Versión |
|---|---|---|
| `nino-fonseca/index.html` | Firma de contratación estatal – Cristian Camilo Niño Fonseca | 5.0 (30-oct-2026) |

## Cómo funciona el instrumento

- Archivo HTML autónomo (sin dependencias de servidor). Diez módulos en dos fases de 90 minutos. Las preguntas se ramifican por perfil (Comprador / Proveedor) según la respuesta a D1.1; las matrices D2.2 y D2.3 muestran solo los documentos elegidos en D2.1; D3.5 y D9.3 son condicionales.
- El avance se guarda en `localStorage` del navegador (clave `innolexia_levantamiento_v5`).
- **Envío a la matriz.** Al cerrar la Fase 1 («Enviar avance de la Fase 1») o la Fase 2 («Enviar a la matriz»), la página hace `fetch(ENDPOINT, {method:"POST", mode:"no-cors", body: JSON})` hacia una aplicación web de Google Apps Script vinculada a la hoja «Matriz de levantamiento – Respuestas». El script (`fuentes/receptor-apps-script.gs`) escribe los encabezados si la fila 1 está vacía, agrega como columna cualquier clave nueva y añade una fila por envío. La URL del endpoint está en la constante `ENDPOINT` al inicio del `<script>`.
- Las claves del JSON coinciden una a una con los encabezados de la hoja (`fuentes/encabezados-matriz.csv`, 314 columnas). Columnas de control: Marca temporal, ID de envío, Fase enviada, Firma configurada, Abogado configurado, Encuentro, Perfil (según D1.1); al final, Observaciones generales de la Fase 1 y 2.
- Descarga de copia en Excel (SheetJS desde cdnjs) y copia al portapapeles como respaldo.

## Personalización

Bloque `CONFIG` al inicio del `<script>` (`firma`, `abogado`, `encuentro`). Se muestra en la cabecera, prellena M0.1 y M0.3 y se envía en las columnas de control.

## Fuente del cuestionario

`fuentes/preguntas.json` contiene los diez módulos con enunciados, ayudas, tipos (`text`, `email`, `textarea`, `chips`, `multi`, `rank`, `matrix`, `numbers`), opciones, filas, perfil (`C`/`P`), opciones excluyentes (`excl`), tope de selección (`max`), dependencias (`rowsFrom`) y condicionales (`showIf`). El HTML se genera a partir de este archivo; cualquier cambio al cuestionario debe hacerse allí y regenerar la página para que las columnas de la matriz sigan coincidiendo.
