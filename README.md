# innolexia-levantamiento

Instrumentos de levantamiento de información para la fase de diagnóstico y diseño de implementación de IA en firmas de abogados (InnoLexIA · Oscar Gutiérrez Saavedra, Consultor de IA y LegalTech).

## Páginas publicadas (GitHub Pages)

| Ruta | Cliente | Versión |
|---|---|---|
| `nino-fonseca/index.html` | Firma de contratación estatal – Cristian Camilo Niño Fonseca | 5.0 (30-oct-2026) |
| `tamayo/index.html` | Firma de peritos partidores y liquidadores – José Óscar Tamayo Rivera | 1.2 (3-nov-2026) · 119 preguntas · 334 columnas (`fuentes/encabezados-matriz-tamayo.csv`) |

## Cómo funciona el instrumento

- Archivo HTML autónomo (sin dependencias de servidor). Diez módulos en dos fases de 90 minutos. Las preguntas se ramifican por perfil (Comprador / Proveedor) según la respuesta a D1.1; las matrices D2.2 y D2.3 muestran solo los documentos elegidos en D2.1; D3.5 y D9.3 son condicionales.
- El avance se guarda en `localStorage` del navegador (clave `innolexia_levantamiento_v5`).
- **Envío a la matriz.** Al cerrar la Fase 1 («Enviar avance de la Fase 1») o la Fase 2 («Enviar a la matriz»), la página hace `fetch(ENDPOINT, {method:"POST", mode:"no-cors", body: JSON})` hacia una aplicación web de Google Apps Script vinculada a la hoja «Matriz de levantamiento – Respuestas». El script (`fuentes/receptor-apps-script.gs`) escribe los encabezados si la fila 1 está vacía y añade una fila por envío, ubicando cada valor en la columna cuyo encabezado coincide exactamente con la clave del JSON. Las claves sin encabezado coincidente no se guardan. Por eso, cualquier cambio de redacción en `preguntas.json` debe reflejarse también en la fila 1 de la hoja y en `encabezados-matriz.csv`. La URL del endpoint está en la constante `ENDPOINT` al inicio del `<script>`.
- Las claves del JSON coinciden una a una con los encabezados de la hoja (`fuentes/encabezados-matriz.csv`, 314 columnas). Columnas de control: Marca temporal, ID de envío, Fase enviada, Firma configurada, Abogado configurado, Encuentro, Perfil (según D1.1); al final, Observaciones generales de la Fase 1 y 2.
- Descarga de copia en Excel (SheetJS desde cdnjs) y copia al portapapeles como respaldo.

## Personalización

Bloque `CONFIG` al inicio del `<script>` (`firma`, `abogado`, `encuentro`). Se muestra en la cabecera, prellena M0.1 y M0.3 y se envía en las columnas de control.

## Receptor multicliente

Cada instrumento tiene su propio despliegue de Apps Script (código `fuentes/receptor-apps-script.gs`, v3): el de contratación estatal está vinculado a su hoja y el de Tamayo a la suya. Cada instrumento envía en `CONFIG.sheetId` el ID de su propia hoja de respuestas; si no lo envía, el receptor escribe en la hoja a la que está vinculado. Las claves que empiezan por `_` no se guardan como columnas.

## Fuente del cuestionario

`fuentes/preguntas.json` (contratación estatal) y `fuentes/preguntas_tamayo.json` (peritos partidores y liquidadores, con bloque `meta` y condicionales `when` sobre D1.1, D1.2, D1.3, D1.6 (práctica pericial), D2.5 (método de avalúo), D3.2, D6.1 y D7.4) contienen los diez módulos con enunciados, ayudas, tipos (`text`, `email`, `textarea`, `chips`, `multi`, `rank`, `matrix`, `numbers`), opciones, filas, perfil (`C`/`P`), opciones excluyentes (`excl`), tope de selección (`max`), dependencias (`rowsFrom`) y condicionales (`showIf`). El HTML se genera a partir de este archivo; cualquier cambio al cuestionario debe hacerse allí y regenerar la página para que las columnas de la matriz sigan coincidiendo.


## Cambios v1.2 del instrumento Tamayo (3 de noviembre de 2026)

Síntesis de las sugerencias del revisor externo: opciones y escalas reformuladas en D1 a D9 (rangos en lugar de categorías subjetivas, columnas «No aplica / No sabe», terminología «sociedad patrimonial entre compañeros permanentes»); D1.3 sin el régimen de auxiliares (D9.5 se condiciona ahora a D1.2); preguntas nuevas D1.2b, D2.4b, D2.5b, D2.10 (práctica pericial, condicionada a D1.6), D3.6b, D4.5a, D7.4b, D7.5, D7.6, D8.2c, D8.4c, D8.7b, D8.7c y D8.8b; retiradas D1.9, D3.1b y D5.2b; D7.7 convertida en matriz; antiguas D7.5/D7.6 renumeradas como D7.9A/D7.9B. Las referencias nominadas en D9.6 (Circular Externa 002 de 2024 de la SIC, CONPES 4144 de 2025, Sentencia T-323 de 2024) deben verificarse en fuente oficial antes del informe. `fuentes/build.py` es el generador.
