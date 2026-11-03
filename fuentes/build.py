import json, base64, csv, io, sys, re

import argparse
ap = argparse.ArgumentParser()
ap.add_argument('--src', default='preguntas.json')
ap.add_argument('--endpoint', default=''); ap.add_argument('--firma', default=''); ap.add_argument('--abogado', default=''); ap.add_argument('--encuentro', default=''); ap.add_argument('--sheet', default='')
ap.add_argument('--out', default='Instrumento_Levantamiento_IA_InnoLexIA.html')
A = ap.parse_args(); ENDPOINT = A.endpoint
RAW = json.load(open(A.src, encoding='utf-8'))
META_DEFAULT = {
  "subtitle": "Fase de diagnóstico y diseño · Firma de abogados especializada en contratación estatal · Jurisdicción: República de Colombia",
  "intro_branch": "__INTRO_BRANCH__",
  "phase1_desc": "Contexto de la firma, procesos, fuentes, información y tecnología",
  "phase2_desc": "Experiencia en IA, gobernanza, fuentes jurídicas y expectativas",
  "branch_cols": [{"id":"__PROFILE__","label":"Perfil (según D1.1)"}],
  "storage_key": "innolexia_levantamiento_v5",
  "title": "Levantamiento IA – Contratación Estatal",
  "version": "5.0 · octubre de 2026"}
if isinstance(RAW, dict):
    META = {**META_DEFAULT, **RAW.get('meta', {})}; Q = RAW['modules']
else:
    META = META_DEFAULT; Q = RAW
order = ['M0','D1','D2','D3','D4','D5','D6','D7','D9','D8']
Q = sorted(Q, key=lambda m: order.index(m['code']))
PHASE1 = {'M0','D1','D2','D3','D4','D5'}
OBS_DEFAULT = "Observaciones del módulo (aspectos no cubiertos, precisiones o matices que convenga registrar)"
for m in Q:
    m['phase'] = 1 if m['code'] in PHASE1 else 2
    obs = m.get('obs', True)
    if obs is not False:
        m['q'].append({"id": m['code']+".OBS", "label": obs if isinstance(obs, str) else OBS_DEFAULT, "type": "textarea"})
PHASES = {1: {"name":"Fase 1 · Encuentro 1","desc":META['phase1_desc'],"min":90},
          2: {"name":"Fase 2 · Encuentro 2","desc":META['phase2_desc'],"min":90}}
logo = base64.b64encode(open('logo_t.webp', 'rb').read()).decode()

# ---------- CSV header (debe coincidir con payload() del HTML) ----------
QBY = {q['id']: q for m in Q for q in m['q']}
OTRO = re.compile(r'^Otr[oa]s?\b')
def rows_of(q):
    if q.get('rowsFrom'):
        return [(META.get('otro_row_label','Otro tipo de documento indicado') if OTRO.match(o) else o) for o in QBY[q['rowsFrom']]['opt']]
    return q.get('rows', [])
headers = ['Marca temporal', 'ID de envío', 'Fase enviada', 'Firma configurada', 'Abogado configurado', 'Encuentro'] + [c['label'] for c in META['branch_cols']]
for m in Q:
    for q in m['q']:
        if q['type'] in ('matrix', 'numbers'):
            for r in rows_of(q):
                headers.append(f"{q['id']} {q['label']} – {r}")
        else:
            headers.append(f"{q['id']} {q['label']}")
            if q['type'] in ('chips','multi','rank') and any(OTRO.match(o) for o in q.get('opt', [])):
                headers.append(f"{q['id']} – Otro, ¿cuál?")
headers += ['Observaciones generales de la Fase 1', 'Observaciones generales de la Fase 2']
buf = io.StringIO(); csv.writer(buf).writerow(headers)
open('encabezados.csv', 'w', encoding='utf-8', newline='').write(buf.getvalue())

ICONS = {
 "id":"<circle cx='12' cy='8' r='4'/><path d='M4 21v-2a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v2'/>",
 "brief":"<rect x='3' y='7' width='18' height='13' rx='2'/><path d='M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18'/>",
 "flow":"<rect x='3' y='3' width='6' height='6' rx='1'/><rect x='15' y='15' width='6' height='6' rx='1'/><path d='M9 6h5a2 2 0 0 1 2 2v7'/>",
 "book":"<path d='M4 4h7a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4zM20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z'/>",
 "shield":"<path d='M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z'/><path d='M9 12l2 2 4-4'/>",
 "server":"<rect x='3' y='4' width='18' height='7' rx='2'/><rect x='3' y='13' width='18' height='7' rx='2'/><path d='M7 7.5h.01M7 16.5h.01'/>",
 "spark":"<path d='M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z'/><path d='M19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z'/>",
 "gavel":"<path d='M14 4l6 6M4 20l7-7M12 6l6 6M9 9l6 6'/><path d='M3 21h8'/>",
 "scale":"<path d='M12 3v18M5 7h14M3 21h18'/><path d='M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z'/>",
 "target":"<circle cx='12' cy='12' r='9'/><circle cx='12' cy='12' r='5'/><circle cx='12' cy='12' r='1'/>",
}

html = r'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<style>
:root{
  /* Paleta del logo InnoLexIA: azul marino, azul medio, cian, hielo */
  --navy:#0E2A5A; --blue:#1E4F9C; --cyan:#35B3D0; --cyan-soft:#CFEAF3; --ice:#EAF3FA;
  --bg:#F4F8FC; --card:#FFFFFF; --ink:#13223F; --muted:#5A6B88; --line:#D3E0EC;
  --ok:#1C7C54; --warn:#9A6B12; --err:#B3261E;
  --display:"Montserrat","Segoe UI",Arial,sans-serif; --body:"Source Sans 3","Segoe UI",Arial,sans-serif;
  /* Layout: cabecera clara con el logo, banda de gradiente, pasos numerados, un módulo por tarjeta */
  color-scheme: light;
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.55}
.wrap{max-width:1000px;margin:0 auto;padding:0 16px}
/* Cabecera */
header.brand{background:linear-gradient(180deg,#FFFFFF 0%,var(--ice) 100%);position:relative;overflow:hidden}
header.brand::after{content:"";position:absolute;right:-80px;top:-60px;width:420px;height:420px;background:
  radial-gradient(circle at 30% 30%,rgba(53,179,208,.18),transparent 60%),
  conic-gradient(from 20deg,rgba(30,79,156,.06),rgba(53,179,208,.12),rgba(30,79,156,.04),rgba(53,179,208,.10));
  clip-path:polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%);pointer-events:none}
.brand-row{display:flex;align-items:center;gap:32px;padding:30px 0 26px;position:relative;z-index:1;flex-wrap:wrap}
.brand-row img{width:210px;max-width:100%;filter:drop-shadow(0 6px 14px rgba(14,42,90,.18))}
.brand-text{flex:1 1 480px;min-width:0}
.brand-text h1{font-family:var(--display);font-weight:800;color:var(--navy);font-size:1.7rem;line-height:1.2;margin:0 0 8px;text-wrap:balance;max-width:22ch}
.brand-text p{margin:0 0 12px;color:var(--muted);max-width:60ch}
.consultor{font-family:var(--display);font-weight:600;font-size:.9rem;display:inline-flex;align-items:center;gap:8px;background:linear-gradient(90deg,var(--navy),var(--blue) 70%,var(--cyan));color:#fff;padding:8px 16px;border-radius:999px}
.consultor::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--cyan-soft)}
.cliente{margin-top:14px;display:flex;flex-wrap:wrap;gap:8px}
.cliente span{display:inline-flex;align-items:center;gap:6px;background:#fff;border:1.5px solid var(--cyan);color:var(--navy);font-family:var(--display);font-weight:600;font-size:.82rem;padding:6px 12px;border-radius:999px}
.cliente span::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--cyan)}
.band{height:6px;background:linear-gradient(90deg,var(--navy),var(--blue),var(--cyan))}
/* Intro */
.intro{display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 24px;margin:22px 0 18px}
.intro p{margin:0 0 8px;text-align:justify;hyphens:auto;max-width:72ch}
.intro p:last-child{margin:0}
.kpis{display:grid;gap:10px}
.kpi{background:var(--ice);border-radius:12px;padding:10px 16px;text-align:center;min-width:120px}
.kpi b{font-family:var(--display);font-size:1.4rem;color:var(--navy);display:block;line-height:1.1}
.kpi span{font-size:.8rem;color:var(--muted)}
/* Pasos */
.steps{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 10px}
.steps button{display:flex;align-items:center;gap:8px;font-family:var(--display);font-weight:600;font-size:.8rem;border:1px solid var(--line);background:var(--card);color:var(--muted);padding:6px 12px 6px 6px;border-radius:999px;cursor:pointer}
.steps button i{display:inline-grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--ice);color:var(--navy);font-style:normal;font-size:.75rem}
.steps button.active{background:var(--navy);color:#fff;border-color:var(--navy)}
.steps button.active i{background:var(--cyan);color:#062338}
.steps button.done i{background:var(--cyan);color:#062338}
.steps button.done i::before{content:"✓"}
/* Pestañas de fase */
.phases{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:0 0 14px}
.phase{border:1.5px solid var(--line);border-radius:14px;padding:12px 16px;background:var(--card);cursor:pointer;text-align:left;font:inherit;color:var(--ink);display:grid;gap:3px}
.phase b{font-family:var(--display);color:var(--navy);font-size:.95rem}
.phase span{font-size:.85rem;color:var(--muted)}
.phase small{font-family:var(--display);font-weight:600;color:var(--cyan);font-size:.75rem;letter-spacing:.04em}
.phase.active{border-color:var(--navy);background:linear-gradient(180deg,var(--ice),#fff);box-shadow:0 6px 18px rgba(14,42,90,.08)}
.phase.locked{opacity:.6}
.phase.done b::after{content:" ✓";color:var(--cyan)}
.endcard .card-head{background:linear-gradient(135deg,var(--navy),var(--blue) 70%,var(--cyan));color:#fff}
.endcard .card-head h2,.endcard .card-head .code{color:#fff}
.endcard .card-head p{color:rgba(255,255,255,.9)}
.endcard .card-head p b{color:#fff}
.endcard .icon{background:rgba(255,255,255,.18)}
.endcard .resumen{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:6px 0 18px}
.endcard .resumen div{background:var(--ice);border-radius:12px;padding:12px 14px}
.endcard .resumen b{font-family:var(--display);font-size:1.3rem;color:var(--navy);display:block}
.endcard .resumen span{font-size:.82rem;color:var(--muted)}
.endcard p{text-align:justify;max-width:72ch}
/* Barra de avance fija */
.avance{position:sticky;top:0;z-index:20;background:rgba(244,248,252,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);margin:0 -16px 18px;padding:10px 16px 12px}
.avance-top{display:flex;justify-content:space-between;align-items:baseline;gap:12px;font-family:var(--display);font-size:.82rem;color:var(--muted);margin-bottom:6px}
.avance-top b{color:var(--navy);font-size:1.05rem}
.avance-top .pct{font-weight:800;font-size:1.25rem;background:linear-gradient(90deg,var(--blue),var(--cyan));-webkit-background-clip:text;background-clip:text;color:transparent}
.segs{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:4px}
.seg{height:10px;border-radius:999px;background:var(--cyan-soft);overflow:hidden;position:relative;cursor:pointer}
.seg i{position:absolute;inset:0;width:0;background:linear-gradient(90deg,var(--blue),var(--cyan));transition:width .3s}
.seg.active{outline:2px solid var(--navy);outline-offset:1px}
.seg.done i{background:var(--navy)}
.progress{display:none}
/* Tarjeta de módulo */
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:0;margin-bottom:18px;overflow:hidden;box-shadow:0 10px 30px rgba(14,42,90,.06)}
.card-head{display:flex;gap:18px;align-items:flex-start;padding:24px 28px 20px;background:linear-gradient(180deg,var(--ice),#fff)}
.icon{flex:0 0 56px;width:56px;height:56px;border-radius:16px;background:linear-gradient(135deg,var(--navy),var(--cyan));display:grid;place-items:center}
.icon svg{width:28px;height:28px;fill:none;stroke:#fff;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.card-head .code{font-family:var(--display);color:var(--cyan);font-weight:700;font-size:.78rem;letter-spacing:.1em}
.card-head h2{font-family:var(--display);color:var(--navy);font-size:1.35rem;margin:2px 0 8px;text-wrap:balance}
.card-head p{margin:0;text-align:justify;hyphens:auto;color:var(--muted);max-width:78ch}
.card-head p b{color:var(--navy);font-family:var(--display);font-size:.8rem;letter-spacing:.04em;text-transform:uppercase;margin-right:6px}
.card-body{padding:8px 28px 26px}
.field{margin:18px 0 0;padding-top:18px;border-top:1px solid var(--line)}
.field:first-child{border-top:0;padding-top:4px}
.field .qid{font-family:var(--display);font-weight:700;color:var(--blue);font-size:.8rem;margin-right:6px}
.field label.main,.field .main{font-weight:600;display:block;margin-bottom:10px;text-align:justify}
.help{color:var(--muted);font-size:.9rem;margin:-4px 0 8px}
.req{color:var(--err)}
input[type=text],input[type=email],input[type=number],textarea{font:inherit;width:100%;padding:11px 13px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--ink)}
textarea{min-height:100px;resize:vertical}
input:focus,textarea:focus,button:focus-visible,.chip input:focus-visible+span{outline:3px solid var(--cyan);outline-offset:1px}
/* Chips */
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{position:relative}
.chip input{position:absolute;opacity:0;inset:0;width:100%;height:100%;cursor:pointer;margin:0}
.chip span{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border:1.5px solid var(--line);border-radius:999px;background:#fff;color:var(--ink);font-size:.95rem;cursor:pointer;transition:all .15s}
.chip span::before{content:"";width:9px;height:9px;border-radius:50%;border:1.5px solid var(--line);background:#fff}
.chip input:checked+span{background:var(--navy);border-color:var(--navy);color:#fff}
.chip input:checked+span::before{background:var(--cyan);border-color:var(--cyan)}
.chip.multi span::before{border-radius:3px}
.chip.multi input:checked+span{background:var(--cyan-soft);border-color:var(--cyan);color:var(--navy)}
.chip.multi input:checked+span::before{background:var(--navy);border-color:var(--navy)}
.chip input:disabled+span{opacity:.45;cursor:not-allowed}
.perfil{display:inline-block;font-family:var(--display);font-weight:700;font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;padding:3px 8px;border-radius:6px;margin-right:8px;vertical-align:middle}
.perfil.C{background:var(--ice);color:var(--navy)}
.perfil.P{background:var(--cyan-soft);color:#0B5A6E}
.perfil.T{background:var(--cyan-soft);color:var(--navy)}
.chip.rk span::before{display:none}
.chip.rk .pos{display:inline-grid;place-items:center;min-width:22px;height:22px;border-radius:50%;background:var(--ice);color:var(--navy);font-family:var(--display);font-size:.75rem;margin-right:2px}
.chip.rk.on span{background:var(--navy);border-color:var(--navy);color:#fff}
.chip.rk.on .pos{background:var(--cyan);color:#062338}
.chip.excl span{border-style:dashed}
.otro input{max-width:420px}
/* Matriz */
.matrix-wrap{overflow-x:auto}
table.matrix{border-collapse:separate;border-spacing:0;width:100%;min-width:560px;font-size:.93rem}
table.matrix th{font-family:var(--display);font-weight:600;font-size:.76rem;color:var(--navy);padding:8px 6px;text-align:center;background:var(--ice)}
table.matrix th:first-child{text-align:left;border-radius:10px 0 0 10px}
table.matrix th:last-child{border-radius:0 10px 10px 0}
table.matrix td{padding:9px 6px;border-bottom:1px solid var(--line);text-align:center}
table.matrix td:first-child{text-align:left;font-weight:600;color:var(--ink);width:38%}
table.matrix tr:hover td{background:#F8FBFE}
.radio{appearance:none;width:20px;height:20px;border:2px solid var(--line);border-radius:50%;cursor:pointer;vertical-align:middle;transition:all .15s}
.radio:checked{border-color:var(--navy);background:radial-gradient(circle,var(--cyan) 45%,var(--navy) 50%)}
/* Números */
.numbers{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
.numbers label{display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid var(--line);border-radius:10px;padding:6px 6px 6px 12px;font-size:.95rem}
.numbers input{width:84px;padding:7px 10px}
/* Acciones */
.actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:space-between;align-items:center;margin-top:8px}
.btn{font-family:var(--display);font-weight:600;font-size:.95rem;border:0;padding:12px 20px;border-radius:12px;cursor:pointer;background:var(--navy);color:#fff;display:inline-flex;align-items:center;gap:8px}
.btn.secondary{background:var(--ice);color:var(--navy)}
.btn.cyan{background:var(--cyan);color:#062338}
a.btn{text-decoration:none}
.btn:disabled{opacity:.5;cursor:not-allowed}
.final{display:none;margin-top:18px}
.final .card-body{padding-top:16px}
.final p{text-align:justify;max-width:72ch;margin:0 0 14px}
.status{padding:12px 14px;border-radius:10px;border:1px solid var(--line);background:#fff;display:none;margin-top:14px}
.status.ok{display:block;border-color:var(--ok);color:var(--ok)}
.status.warn{display:block;border-color:var(--warn);color:var(--warn)}
.status.err{display:block;border-color:var(--err);color:var(--err)}
.field.invalid{background:#FFF7F6;border-radius:10px;padding-left:10px;padding-right:10px}
footer{color:var(--muted);font-size:.9rem;padding:28px 16px 44px;text-align:center}
footer b{color:var(--navy);font-family:var(--display)}
@media (max-width:700px){.phases{grid-template-columns:1fr}.intro{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(3,1fr)}.card-head,.card-body{padding-left:18px;padding-right:18px}.brand-row{gap:16px;padding:22px 0}.brand-text{flex:1 1 480px;min-width:0}
.brand-text h1{font-size:1.4rem}}
@media (prefers-reduced-motion:reduce){.progress span,.chip span{transition:none}}
</style>
</head>
<body>
<header class="brand"><div class="wrap">
  <div class="brand-row">
    <img src="data:image/webp;base64,__LOGO__" alt="InnoLexIA">
    <div class="brand-text">
      <h1>Instrumento de levantamiento de información para la implementación de IA</h1>
      <p>__SUBTITLE__</p>
      <span class="consultor">Oscar Gutiérrez Saavedra – Consultor de IA y LegalTech</span>
      <div class="cliente" id="cliente" style="display:none"></div>
    </div>
  </div>
</div></header>
<div class="band"></div>

<main class="wrap">
  <section class="intro">
    <div>
      <p>Este instrumento recoge la información necesaria para diagnosticar el estado actual de la firma y diseñar la implementación de la herramienta de inteligencia artificial que mejor se ajuste a su práctica. Se desarrolla en dos fases de 90 minutos, previstas para dos encuentros de trabajo, con diez módulos en total; __INTRO_BRANCH__ cada módulo indica la finalidad de la información que solicita y cierra con un espacio de observaciones para registrar lo que no haya quedado cubierto. El levantamiento se rige por el ordenamiento jurídico colombiano, por lo que las referencias normativas corresponden a normas de la República de Colombia y su vigencia se verifica en fuentes oficiales. La mayoría de las preguntas se responden con un clic; las de texto libre se reservan para lo que solo usted puede describir.</p>
      <p>Sus respuestas se guardan automáticamente en este navegador mientras avanza y, al finalizar, se envían a la matriz de diagnóstico. Las preguntas marcadas con <span class="req">*</span> son obligatorias. La información suministrada se trata con carácter confidencial y solo para los fines de la consultoría.</p>
    </div>
    <div class="kpis" style="grid-template-columns:repeat(3,1fr)">
      <div class="kpi"><b>2</b><span>fases de 90 min</span></div><div class="kpi"><b id="k-mod">10</b><span>módulos</span></div>
      <div class="kpi"><b id="k-q">0</b><span>preguntas</span></div>
      
    </div>
  </section>

  <div class="phases" id="phases"></div>
  <div class="avance" role="progressbar" aria-valuemin="0" aria-valuemax="100" id="avance">
    <div class="avance-top"><span><span id="av-fase"></span> · <b id="av-mod"></b></span><span><span id="av-count"></span> · <span class="pct" id="av-pct">0 %</span></span></div>
    <div class="segs" id="segs"></div>
  </div>
  <nav class="steps" id="steps" aria-label="Módulos"></nav>
  <div class="progress" aria-hidden="true"><span id="bar"></span></div>

  <form id="form" novalidate>
    <div id="panel"></div>
    <div class="actions">
      <button type="button" class="btn secondary" id="prev">← Anterior</button>
      <span id="counter" style="color:var(--muted);font-size:.95rem"></span>
      <button type="button" class="btn" id="next">Siguiente →</button>
    </div>
  </form>

  <section class="card final endcard" id="final"></section>
</main>

<footer>
  <b>InnoLexIA</b> · Oscar Gutiérrez Saavedra – Consultor de IA y LegalTech · Pereira, Colombia<br>
  Instrumento de uso exclusivo para la consultoría de implementación de IA · Versión __VERSION__
</footer>

<script>
/* =====================================================================
   CONFIGURACIÓN DEL INSTRUMENTO (editable con cualquier editor de texto)
   ENDPOINT : URL de la aplicación web de Google Apps Script (termina en /exec)
   CONFIG   : personalización visible en la cabecera y en la matriz
   ===================================================================== */
const ENDPOINT = "__ENDPOINT__";
const CONFIG = {
  sheetId:   "__SHEET__",      // ID de la hoja de Google destino (vacío = hoja vinculada al script)
  firma:     "__FIRMA__",      // Nombre de la firma de abogados (ej. "Pérez & Asociados S.A.S.")
  abogado:   "__ABOGADO__",    // Abogado(a) o socio(a) que diligencia (ej. "Dra. Ana Pérez – Socia directora")
  encuentro: "__ENCUENTRO__"   // Fecha o referencia del encuentro (ej. "Encuentro 1 · 4 de noviembre de 2026")
};
const MODULOS = __QUESTIONS__;
const ICONS = __ICONS__;
const PHASES = __PHASES__;
const KEY = "__KEY__";
const BRANCH_COLS = __BRANCH_COLS__;
let idx = 0, data = {}, view = "module";
try { data = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { data = {}; }
const $ = s => document.querySelector(s);
(function applyConfig(){
  const tags=[]; if(CONFIG.firma) tags.push("Firma: "+CONFIG.firma); if(CONFIG.abogado) tags.push(CONFIG.abogado); if(CONFIG.encuentro) tags.push(CONFIG.encuentro);
  if(tags.length){const c=$("#cliente");c.style.display="flex";c.innerHTML=tags.map(t=>`<span>${t.replace(/[&<>"']/g,x=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[x]))}</span>`).join("");}
  if(CONFIG.firma && !data["M0.1"]) data["M0.1"]=CONFIG.firma;
  if(CONFIG.abogado && !data["M0.3"]) data["M0.3"]=CONFIG.abogado.replace(/^Abogado:\s*/,"");
  if(CONFIG.firma) document.title="Levantamiento IA – "+CONFIG.firma;
})();
const steps=$("#steps"), panel=$("#panel"), bar=$("#bar");
const esc = s => String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const QBY = {}; MODULOS.forEach(m=>m.q.forEach(q=>QBY[q.id]=q));
const OTRO = /^Otr[oa]s?\b/; const OTRO_ROW=__OTRO_ROW__;
const hasOtro = q => ["chips","multi","rank"].includes(q.type) && (q.opt||[]).some(o=>OTRO.test(o));
const otroSel = q => {const v=data[q.id]; return Array.isArray(v)?v.some(o=>OTRO.test(o)):(typeof v==="string"&&OTRO.test(v));};

/* ---- Perfil (D1.1) y visibilidad condicional ---- */
function profiles(){
  const v=data["D1.1"]||"";
  if(/exclusivamente a entidades/.test(v)) return {C:true,P:false};
  if(/exclusivamente a proponentes/.test(v)) return {C:false,P:true};
  return {C:true,P:true};
}
function profileLabel(){const p=profiles();return p.C&&p.P?"Comprador y Proveedor":p.C?"Comprador":"Proveedor";}
function cond(c){ let v=data[c.q]; if(c.row) v=(v&&typeof v==="object")?v[c.row]:undefined;
  const arr=Array.isArray(v)?v:(v===undefined||v===""?[]:[v]);
  if(c.any) return c.any.some(o=>arr.includes(o));
  if(c.notIn) return !(arr.length && arr.every(o=>c.notIn.includes(o)));
  return true; }
function visible(q){
  if(q.profile && !profiles()[q.profile]) return false;
  if(q.when){ const ws=Array.isArray(q.when)?q.when:[q.when]; if(!ws.every(cond)) return false; }
  if(q.showIf){const s=q.showIf; let v=data[s.q];
    if(s.row){v=(v&&typeof v==="object")?v[s.row]:undefined;}
    if(v!==undefined && v!=="" && s.notIn && s.notIn.includes(v)) return false;}
  return true;
}
function rowsOf(q){
  if(q.rowsFrom){const sel=data[q.rowsFrom]; return Array.isArray(sel)?sel.map(o=>OTRO.test(o)?OTRO_ROW:o):[];}
  return q.rows||[];
}
const visQ = m => m.q.filter(visible);
const phaseOf = i => MODULOS[i].phase;
const modsOf = ph => MODULOS.map((m,i)=>[m,i]).filter(([m])=>m.phase===ph);
const lastOf = ph => modsOf(ph).slice(-1)[0][1];
const firstOf = ph => modsOf(ph)[0][1];

function filled(q){const v=data[q.id];
  if(v===undefined||v===null) return false;
  if(Array.isArray(v)) return v.length>0;
  if(typeof v==="object") return Object.values(v).some(x=>String(x).trim()!=="");
  return String(v).trim()!=="";}
function moduleComplete(m){const qs=visQ(m);return qs.filter(q=>q.req).every(filled) && qs.some(filled);}
function phaseComplete(ph){return modsOf(ph).every(([m])=>moduleComplete(m));}
function phaseStats(ph){const qs=modsOf(ph).flatMap(([m])=>visQ(m));const n=qs.filter(filled).length;return {n,t:qs.length,pct:qs.length?Math.round(100*n/qs.length):0};}
function save(){try{localStorage.setItem(KEY,JSON.stringify(data));}catch(e){}}
function updateKpis(){const t=MODULOS.reduce((a,m)=>a+visQ(m).length,0);$("#k-q").textContent=t;$("#k-mod").textContent=MODULOS.length;}

function renderPhases(){
  const ph=phaseOf(idx); const box=$("#phases"); box.innerHTML="";
  [1,2].forEach(p=>{const st=phaseStats(p);const b=document.createElement("button");b.type="button";
    b.className="phase"+(p===ph?" active":"")+(phaseComplete(p)?" done":"")+(p===2&&!data._fase1Cerrada&&ph!==2?" locked":"");
    b.innerHTML=`<small>${esc(PHASES[p].name)} · ${PHASES[p].min} min</small><b>${esc(PHASES[p].desc)}</b><span>${st.n} de ${st.t} respuestas · ${st.pct} %</span>`;
    b.onclick=()=>{view="module";idx=firstOf(p);render();};box.appendChild(b);});
}
function renderNav(){
  const ph=phaseOf(idx); steps.innerHTML="";
  modsOf(ph).forEach(([m,i],k)=>{const b=document.createElement("button");b.type="button";
    b.innerHTML=`<i>${moduleComplete(m)?"":k+1}</i>${esc(m.code)} · ${esc(m.title)}`;
    b.className=(i===idx&&view==="module"?"active ":"")+(moduleComplete(m)?"done":"");b.onclick=()=>{view="module";idx=i;render();};steps.appendChild(b);});
  const st=phaseStats(ph); bar.style.width=st.pct+"%";
  const segs=$("#segs"); segs.innerHTML="";
  modsOf(ph).forEach(([m,i])=>{const d=document.createElement("div");const qs=visQ(m);const n=qs.filter(filled).length;
    d.className="seg"+(i===idx&&view==="module"?" active":"")+(n===qs.length&&n>0?" done":"");d.title=m.code+" · "+m.title+" ("+n+"/"+qs.length+")";
    d.innerHTML=`<i style="width:${qs.length?Math.round(100*n/qs.length):0}%"></i>`;d.onclick=()=>{view="module";idx=i;render();};segs.appendChild(d);});
  $("#av-fase").textContent=PHASES[ph].name;
  $("#av-mod").textContent=view==="end"?"Cierre de la fase":MODULOS[idx].code+" · "+MODULOS[idx].title;
  $("#av-count").textContent=st.n+" de "+st.t+" respuestas de la fase";
  $("#av-pct").textContent=st.pct+" %";
  $("#avance").setAttribute("aria-valuenow",st.pct);
  $("#counter").textContent=view==="end"?"":`Módulo ${modsOf(ph).findIndex(([,i])=>i===idx)+1} de ${modsOf(ph).length} de la ${PHASES[ph].name.split(" · ")[0]} ${BRANCH_COLS.some(c=>c.id==='__PROFILE__')?' · Perfil: '+profileLabel():''}`;
  renderPhases(); updateKpis();
}

function otroHtml(q){
  if(!hasOtro(q)) return "";
  return `<div class="otro" data-otro="${q.id}" style="${otroSel(q)?"":"display:none"};margin-top:10px"><input type="text" name="${q.id}::otro" placeholder="Indique cuál" value="${esc(data[q.id+".otro"]||"")}" aria-label="Otro, ¿cuál?"></div>`;
}
function fieldHtml(q){
  const v=data[q.id]; const req=q.req?' <span class="req" title="Obligatoria">*</span>':"";
  const tag=q.profile?`<span class="perfil ${q.profile}">${q.profile==="C"?"Perfil Comprador":"Perfil Proveedor"}</span>`:(q.tag?`<span class="perfil T">${esc(q.tag)}</span>`:"");
  let h=`<div class="field" data-id="${q.id}"><span class="main"><span class="qid">${esc(q.id.replace(".OBS",""))}${q.id.endsWith(".OBS")?" · OBS":""}</span>${tag}${esc(q.profile?q.label.replace(/^(Perfil Comprador|Perfil Proponente o proveedor|Clientes del perfil Comprador|Clientes del perfil Proponente o proveedor|Documentos recurrentes del perfil Comprador|Documentos recurrentes del perfil Proponente o proveedor)\.\s*/,""):q.label)}${req}</span>`;
  if(q.help) h+=`<div class="help">${esc(q.help)}</div>`;
  if(q.max&&q.type==="multi") h+=`<div class="help">Seleccione hasta ${q.max} opciones.</div>`;
  switch(q.type){
    case "textarea": h+=`<textarea id="f_${q.id}" name="${q.id}">${esc(v||"")}</textarea>`; break;
    case "chips": h+=`<div class="chips">`+q.opt.map(o=>`<label class="chip"><input type="radio" name="${q.id}" value="${esc(o)}" ${v===o?"checked":""}><span>${esc(o)}</span></label>`).join("")+`</div>`+otroHtml(q); break;
    case "multi": {const arr=Array.isArray(v)?v:[]; const full=q.max&&arr.length>=q.max; const exOn=(q.excl||[]).some(e=>arr.includes(e));
      h+=`<div class="chips">`+q.opt.map(o=>{const isEx=(q.excl||[]).includes(o);const dis=!arr.includes(o)&&(full||(exOn)||(arr.length>0&&isEx&&!exOn&&false));
        return `<label class="chip multi${isEx?" excl":""}"><input type="checkbox" name="${q.id}" value="${esc(o)}" ${arr.includes(o)?"checked":""} ${dis?"disabled":""}><span>${esc(o)}</span></label>`;}).join("")+`</div>`+otroHtml(q); break;}
    case "rank": {const arr=Array.isArray(v)?v:[];
      h+=`<div class="chips rank">`+q.opt.map(o=>{const pos=arr.indexOf(o);const dis=pos<0&&arr.length>=q.max;
        return `<label class="chip rk${pos>=0?" on":""}"><input type="checkbox" name="${q.id}" value="${esc(o)}" ${pos>=0?"checked":""} ${dis?"disabled":""}><span><b class="pos">${pos>=0?pos+1:""}</b>${esc(o)}</span></label>`;}).join("")+`</div>`+otroHtml(q); break;}
    case "matrix": {const obj=v&&typeof v==="object"?v:{}; const rows=rowsOf(q);
      if(!rows.length){h+=`<div class="help" style="background:var(--ice);padding:10px 12px;border-radius:10px">Seleccione primero los documentos en la pregunta anterior; aquí aparecerán solo los elegidos.</div>`;break;}
      h+=`<div class="matrix-wrap"><table class="matrix"><thead><tr><th></th>`+q.opt.map(o=>`<th>${esc(o)}</th>`).join("")+`</tr></thead><tbody>`;
      rows.forEach((r,ri)=>{h+=`<tr><td>${esc(r)}</td>`+q.opt.map(o=>`<td><input class="radio" type="radio" name="${q.id}::${ri}" value="${esc(o)}" ${obj[r]===o?"checked":""} aria-label="${esc(r)}: ${esc(o)}"></td>`).join("")+`</tr>`;});
      h+=`</tbody></table></div>`; break;}
    case "numbers": {const obj=v&&typeof v==="object"?v:{};
      h+=`<div class="numbers">`+q.rows.map((r,ri)=>`<label><span>${esc(r)}</span><input type="number" min="0" name="${q.id}::${ri}" value="${esc(obj[r]??"")}"></label>`).join("")+`</div>`; break;}
    default: h+=`<input type="${q.type}" id="f_${q.id}" name="${q.id}" value="${esc(v||"")}">`;
  }
  return h+`</div>`;
}
function renderModule(){
  const m=MODULOS[idx]; const qs=visQ(m);
  panel.innerHTML=`<section class="card"><div class="card-head"><div class="icon"><svg viewBox="0 0 24 24">${ICONS[m.icon]}</svg></div>
    <div><span class="code">${esc(PHASES[m.phase].name.toUpperCase())} · MÓDULO ${esc(m.code)}</span><h2>${esc(m.title)}</h2><p><b>Finalidad</b>${esc(m.objective)}</p></div></div>
    <div class="card-body">${qs.map(fieldHtml).join("")}${m.code==="D9"?`<p class="help" style="margin-top:18px;text-align:justify">Nota. El inventario es una guía de levantamiento y no sustituye la verificación de vigencia, modificaciones, derogatorias y condicionamientos de constitucionalidad de cada norma en SUIN-Juriscol, Secretaría del Senado o Diario Oficial. Los instrumentos señalados con «verificar vigencia» o «en verificación» se confirmarán en fuente oficial durante la fase de diseño.${KEY.includes("tamayo")?" Las referencias al régimen de insolvencia de la persona natural corresponden al informe normativo con corte al 30 de octubre de 2026; los artículos 572 a 576 del CGP provienen de reproducción secundaria y deben cotejarse con los Diarios Oficiales n.º 53.027 y 53.286.":""}</p>`:""}</div></section>`;
  panel.style.display="block"; $("#form .actions").style.display="flex"; $("#final").style.display="none";
  const ph=phaseOf(idx);
  $("#prev").disabled=idx===firstOf(ph)&&ph===1;
  $("#next").textContent=idx===lastOf(ph)?(ph===1?"Finalizar Fase 1 →":"Finalizar Fase 2 →"):"Siguiente →";
}
function renderEnd(ph){
  const st=phaseStats(ph); const obsKey="FASE"+ph+".OBS";
  const faltan=modsOf(ph).filter(([m])=>!visQ(m).filter(q=>q.req).every(filled)).map(([m])=>m.code+" "+m.title);
  let h=`<div class="card-head"><div class="icon"><svg viewBox="0 0 24 24"><path d="M4 12l5 5L20 6"/></svg></div>
    <div><span class="code">${esc(PHASES[ph].name.toUpperCase())}</span><h2>${ph===1?"Ha concluido la Fase 1 del levantamiento":"Ha concluido el levantamiento de información"}</h2>
    <p>${ph===1?"Gracias por el tiempo dedicado a este primer encuentro. Sus respuestas quedaron guardadas en este navegador. La Fase 2 cubre la experiencia en IA, la gobernanza, las fuentes jurídicas y las expectativas de la firma, y toma alrededor de 90 minutos. Si desea continuar ahora, haga clic en «Continuar a la Fase 2»; si prefiere hacerlo en el segundo encuentro, puede cerrar esta página y retomar desde el mismo navegador.":"Con la Fase 2 queda completo el instrumento. Al enviar, las respuestas de ambas fases se registran en la matriz de diagnóstico de InnoLexIA; también puede descargar una copia en Excel para su archivo."}</p></div></div>
    <div class="card-body">
    <div class="resumen"><div><b>${st.n} / ${st.t}</b><span>respuestas de la fase</span></div><div><b>${st.pct} %</b><span>avance de la fase</span></div><div><b>${modsOf(ph).filter(([m])=>moduleComplete(m)).length} / ${modsOf(ph).length}</b><span>módulos completos</span></div></div>
    ${faltan.length?`<div class="status warn" style="display:block;margin:0 0 16px">Quedan obligatorias sin responder en: ${esc(faltan.join(", "))}. Puede volver a esos módulos desde la barra superior.</div>`:""}
    <div class="field" style="border-top:0;padding-top:0" data-id="${obsKey}"><span class="main">Observaciones generales de la ${esc(PHASES[ph].name.split(" · ")[0])}. Registre cualquier aspecto que haya quedado por fuera y deba cubrirse en el diagnóstico.</span>
      <textarea id="f_${obsKey}" name="${obsKey}">${esc(data[obsKey]||"")}</textarea></div>
    <div class="actions" style="justify-content:flex-start;margin-top:18px">`;
  if(ph===1) h+=`<button type="button" class="btn cyan" id="go2">Continuar a la Fase 2 →</button><button type="button" class="btn secondary" id="send1">Enviar avance de la Fase 1</button><button type="button" class="btn secondary" id="xlsx">Descargar copia en Excel</button>${ENDPOINT?`<a class="btn secondary" id="ping" href="${ENDPOINT}" target="_blank" rel="noopener">Probar conexión con la matriz</a>`:""}`;
  else h+=`<button type="button" class="btn cyan" id="send">Enviar a la matriz</button><button type="button" class="btn secondary" id="xlsx">Descargar copia en Excel</button><button type="button" class="btn secondary" id="copy">Copiar respuestas</button><button type="button" class="btn secondary" id="back1">← Revisar la Fase 1</button>${ENDPOINT?`<a class="btn secondary" id="ping" href="${ENDPOINT}" target="_blank" rel="noopener">Probar conexión con la matriz</a>`:""}`;
  h+=`</div><div class="status" id="status" role="status"></div></div>`;
  const f=$("#final"); f.innerHTML=h; f.style.display="block"; panel.style.display="none"; $("#form .actions").style.display="none";
  f.querySelector("textarea").addEventListener("input",e=>{data[obsKey]=e.target.value;save();});
  if(ph===1){$("#go2").onclick=()=>{data._fase1Cerrada=true;save();view="module";idx=firstOf(2);render();};
    $("#send1").onclick=()=>sendPayload("Fase 1",$("#send1"));}
  else{$("#send").onclick=()=>{if(allValid())sendPayload("Completo (Fases 1 y 2)",$("#send"));};$("#back1").onclick=()=>{view="module";idx=firstOf(1);render();};$("#copy").onclick=copyAll;}
  $("#xlsx").onclick=downloadXlsx;
}
function render(){renderNav(); if(view==="end") renderEnd(phaseOf(idx)); else renderModule(); window.scrollTo({top:0,behavior:"smooth"});}

/* ---- Captura de respuestas ---- */
panel.addEventListener("input",e=>{
  const name=e.target.name; if(!name) return;
  const [qid,sub]=name.split("::"); const q=QBY[qid]; if(!q) return;
  let rerender=false;
  if(sub==="otro"){data[qid+".otro"]=e.target.value;save();return;}
  if(q.type==="multi"){
    const val=e.target.value; let arr=Array.isArray(data[qid])?[...data[qid]]:[];
    if(e.target.checked){ if((q.excl||[]).includes(val)) arr=[val]; else {arr=arr.filter(x=>!(q.excl||[]).includes(x)); arr.push(val);} }
    else arr=arr.filter(x=>x!==val);
    data[qid]=arr; rerender=true;
  } else if(q.type==="rank"){
    const val=e.target.value; let arr=Array.isArray(data[qid])?[...data[qid]]:[];
    if(e.target.checked){ if(arr.length<q.max) arr.push(val);} else arr=arr.filter(x=>x!==val);
    data[qid]=arr; rerender=true;
  } else if(q.type==="matrix"||q.type==="numbers"){
    const rows=rowsOf(q); const obj=(data[qid]&&typeof data[qid]==="object")?{...data[qid]}:{}; obj[rows[+sub]]=e.target.value; data[qid]=obj;
  } else { data[qid]=e.target.value; if(q.type==="chips") rerender=true; }
  save();
  const f=e.target.closest(".field"); if(f) f.classList.remove("invalid");
  // Cambios que alteran la visibilidad de otras preguntas o requieren refrescar el campo
  if(qid==="D1.1"||q.rowsFrom||Object.values(QBY).some(x=>x.rowsFrom===qid||(x.showIf&&x.showIf.q===qid)||(x.when&&(Array.isArray(x.when)?x.when:[x.when]).some(c=>c.q===qid)))) { const y=window.scrollY; renderModule(); window.scrollTo(0,y); }
  else if(rerender){ const y=window.scrollY; const old=panel.querySelector(`.field[data-id="${qid}"]`); if(old){const tmp=document.createElement("div");tmp.innerHTML=fieldHtml(q);old.replaceWith(tmp.firstElementChild);} window.scrollTo(0,y); }
  renderNav();
});

function setStatus(k,msg){const s=$("#status");if(!s)return;s.className="status "+k;s.textContent=msg;}
function validate(m){let ok=true;visQ(m).filter(q=>q.req&&!filled(q)).forEach(q=>{ok=false;const f=panel.querySelector(`.field[data-id="${q.id}"]`);if(f)f.classList.add("invalid");});
  if(!ok) alertInline("Faltan respuestas obligatorias en este módulo (resaltadas).");return ok;}
function alertInline(msg){let a=$("#inline-alert");if(!a){a=document.createElement("div");a.id="inline-alert";a.className="status warn";panel.parentNode.insertBefore(a,panel.nextSibling);}a.style.display="block";a.textContent=msg;setTimeout(()=>{a.style.display="none";},4000);}
$("#prev").onclick=()=>{const ph=phaseOf(idx);if(idx===firstOf(ph)&&ph===2){view="end";idx=lastOf(1);render();}else if(idx>0){idx--;render();}};
$("#next").onclick=()=>{if(!validate(MODULOS[idx]))return;const ph=phaseOf(idx);if(idx===lastOf(ph)){view="end";render();}else{idx++;render();}};

/* ---- Carga útil: mismas columnas que la hoja ---- */
function payload(fase){
  const out={"Marca temporal":new Date().toLocaleString("es-CO",{timeZone:"America/Bogota"}),
             "ID de envío":(data._id||=(Date.now().toString(36)+Math.random().toString(36).slice(2,6))),
             "Fase enviada":fase,
             "Firma configurada":CONFIG.firma||"", "Abogado configurado":CONFIG.abogado||"", "Encuentro":CONFIG.encuentro||"",
  };
  BRANCH_COLS.forEach(c=>{ if(c.id==="__PROFILE__") out[c.label]=profileLabel(); else { const v=data[c.id]; out[c.label]=Array.isArray(v)?v.join(" | "):(v??""); } });
  if(CONFIG.sheetId) out["_sheetId"]=CONFIG.sheetId;
  MODULOS.forEach(m=>m.q.forEach(q=>{const v=data[q.id]; const vis=visible(q);
    if(q.type==="matrix"||q.type==="numbers"){
      const obj=(v&&typeof v==="object")?v:{};
      const allRows=q.rowsFrom?QBY[q.rowsFrom].opt.map(o=>OTRO.test(o)?OTRO_ROW:o):q.rows;
      allRows.forEach(r=>out[`${q.id} ${q.label} – ${r}`]=vis?(obj[r]??""):"");
    } else {
      let val="";
      if(vis){ if(q.type==="rank") val=(Array.isArray(v)?v:[]).map((o,i)=>`${i+1}. ${o}`).join(" | "); else val=Array.isArray(v)?v.join(" | "):(v??""); }
      out[`${q.id} ${q.label}`]=val;
      if(hasOtro(q)) out[`${q.id} – Otro, ¿cuál?`]=vis?(data[q.id+".otro"]||""):"";
    }}));
  out["Observaciones generales de la Fase 1"]=data["FASE1.OBS"]||""; out["Observaciones generales de la Fase 2"]=data["FASE2.OBS"]||"";
  return out;
}
function allValid(){const missing=MODULOS.filter(m=>!visQ(m).filter(q=>q.req).every(filled));
  if(missing.length){setStatus("warn","Faltan respuestas obligatorias en: "+missing.map(m=>m.code+" "+m.title).join(", ")+". Vuelva a esos módulos desde las pestañas de fase.");return false;}return true;}
async function sendPayload(fase,btn){
  if(!ENDPOINT){setStatus("err","El destino de envío aún no está configurado. Descargue la copia en Excel y envíela al consultor.");return;}
  btn.disabled=true;setStatus("warn","Enviando…");
  try{await fetch(ENDPOINT,{method:"POST",mode:"no-cors",headers:{"Content-Type":"text/plain;charset=utf-8"},body:JSON.stringify(payload(fase))});
    setStatus("ok",fase==="Fase 1"?"Avance de la Fase 1 enviado a la matriz. Puede continuar ahora o en el segundo encuentro.":"Respuestas enviadas a la matriz de diagnóstico. Gracias por su tiempo.");}
  catch(err){setStatus("err","No fue posible enviar (sin conexión o destino inaccesible). Descargue la copia en Excel y envíela al consultor.");}
  btn.disabled=false;
}
function downloadXlsx(){
  const ph=phaseOf(idx); const p=payload(view==="end"&&ph===1?"Fase 1":"Completo (Fases 1 y 2)");
  const nombre="Levantamiento_IA_"+(data["M0.1"]||"firma").replace(/[^\w\-]+/g,"_")+".xlsx";
  if(window.XLSX){const wb=XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb,XLSX.utils.json_to_sheet(Object.entries(p).filter(([k,v])=>v!=="").map(([k,v])=>({Pregunta:k,Respuesta:v}))),"Respuestas");
    XLSX.utils.book_append_sheet(wb,XLSX.utils.json_to_sheet([p]),"Fila matriz");XLSX.writeFile(wb,nombre);}
  else{const csv=Object.entries(p).map(([k,v])=>`"${k.replace(/"/g,'""')}","${String(v).replace(/"/g,'""')}"`).join("\n");
    const a=document.createElement("a");a.href=URL.createObjectURL(new Blob(["﻿"+csv],{type:"text/csv"}));a.download=nombre.replace(".xlsx",".csv");a.click();}
  setStatus("ok","Copia descargada.");
}
async function copyAll(){try{await navigator.clipboard.writeText(JSON.stringify(payload("Completo (Fases 1 y 2)"),null,2));setStatus("ok","Respuestas copiadas al portapapeles.");}
  catch(e){setStatus("err","El navegador no permitió copiar. Use la descarga en Excel.");}}
if(data._fase1Cerrada && !phaseComplete(2)) idx=firstOf(2);
render();
</script>
</body>
</html>
'''
html = (html.replace('__LOGO__', logo).replace('__QUESTIONS__', json.dumps(Q, ensure_ascii=False))
            .replace('__ICONS__', json.dumps(ICONS)).replace('__PHASES__', json.dumps(PHASES, ensure_ascii=False)).replace('__ENDPOINT__', ENDPOINT).replace('__TITLE__', ('Levantamiento IA – '+A.firma) if A.firma else META.get('title','Levantamiento IA – InnoLexIA')).replace('__SUBTITLE__', META['subtitle']).replace('__INTRO_BRANCH__', META['intro_branch']).replace('__VERSION__', META['version']).replace('__KEY__', META['storage_key']).replace('__BRANCH_COLS__', json.dumps(META['branch_cols'], ensure_ascii=False)).replace('__OTRO_ROW__', json.dumps(META.get('otro_row_label','Otro tipo de documento indicado'), ensure_ascii=False)).replace('__SHEET__', A.sheet).replace('__FIRMA__', A.firma).replace('__ABOGADO__', A.abogado).replace('__ENCUENTRO__', A.encuentro))
open(A.out, 'w', encoding='utf-8').write(html)
print('ok', len(html)//1024, 'KB', len(headers), 'columnas', sum(len(m['q']) for m in Q), 'preguntas')
