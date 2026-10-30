/**
 * InnoLexIA – Receptor de respuestas del instrumento de levantamiento.
 * Script vinculado a la hoja de cálculo "Matriz de levantamiento – Respuestas".
 * Despliegue: Implementar > Nueva implementación > Aplicación web
 *   Ejecutar como: Yo (su cuenta)   |   Quién tiene acceso: Cualquier persona
 */
var NOMBRE_HOJA = 'Respuestas';

function doPost(e) {
  try {
    var datos = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var hoja = ss.getSheetByName(NOMBRE_HOJA) || ss.getSheets()[0];
    var ultimaCol = hoja.getLastColumn();
    var encabezados = ultimaCol > 0 ? hoja.getRange(1, 1, 1, ultimaCol).getValues()[0] : [];
    if (encabezados.length === 0 || encabezados[0] === '') {
      encabezados = Object.keys(datos);
      hoja.getRange(1, 1, 1, encabezados.length).setValues([encabezados]);
    }
    var fila = encabezados.map(function (h) {
      var v = datos[h];
      return v === undefined || v === null ? '' : v;
    });
    hoja.appendRow(fila);
    return ContentService.createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService.createTextOutput('Receptor InnoLexIA activo').setMimeType(ContentService.MimeType.TEXT);
}
