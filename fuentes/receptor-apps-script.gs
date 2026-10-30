/**
 * InnoLexIA – Receptor de respuestas de los instrumentos de levantamiento (v3, multicliente).
 * Script vinculado a la hoja «Matriz de levantamiento – Respuestas» (contratación estatal).
 * Si el envío trae la clave "_sheetId", escribe en esa otra hoja de cálculo (p. ej., la del cliente Tamayo);
 * si no la trae, escribe en la hoja vinculada. Las claves que empiezan por "_" no se guardan como columnas.
 * Escribe los encabezados si la fila 1 está vacía y agrega al final cualquier columna nueva.
 *
 * Actualización: Implementar > Administrar implementaciones > (lápiz) > Versión: Nueva versión > Implementar.
 * La URL /exec no cambia.
 */
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(10000);
  try {
    var datos = JSON.parse(e.postData.contents);
    var ss = datos._sheetId ? SpreadsheetApp.openById(datos._sheetId) : SpreadsheetApp.getActiveSpreadsheet();
    var hoja = ss.getSheets()[0];
    var claves = Object.keys(datos).filter(function (k) { return k.charAt(0) !== '_'; });
    var ultimaCol = hoja.getLastColumn();
    var encabezados = ultimaCol > 0 ? hoja.getRange(1, 1, 1, ultimaCol).getValues()[0] : [];
    if (encabezados.length === 0 || encabezados[0] === '') {
      encabezados = claves;
      hoja.getRange(1, 1, 1, encabezados.length).setValues([encabezados]);
      hoja.setFrozenRows(1);
    }
    var nuevas = claves.filter(function (k) { return encabezados.indexOf(k) === -1; });
    if (nuevas.length) {
      hoja.getRange(1, encabezados.length + 1, 1, nuevas.length).setValues([nuevas]);
      encabezados = encabezados.concat(nuevas);
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
  } finally {
    lock.releaseLock();
  }
}
function doGet() {
  return ContentService.createTextOutput('Receptor InnoLexIA activo (v3)').setMimeType(ContentService.MimeType.TEXT);
}
