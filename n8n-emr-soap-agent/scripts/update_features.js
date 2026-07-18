const fs = require('fs');
const html = fs.readFileSync('/tmp/soap_form.html', 'utf8');
let data = JSON.parse(fs.readFileSync('/tmp/wf.json', 'utf8'));
let wf = Array.isArray(data) ? data[0] : data;

// ---- New AI system prompt (adds risk_scores, prescription, patient_instructions) ----
const sys =
  "You are an experienced clinical documentation and decision-support assistant for a licensed physician. " +
  "Produce a professional DRAFT SOAP note plus decision support from CONTEXT and BULLETS, using standard medical terminology. " +
  "Rules: never give a definitive diagnosis (give a differential with brief reasoning); never issue final prescriptions (only suggest medication options for the physician to consider and adjust); " +
  "use ONLY the provided information and mark anything absent as [not documented]; never fabricate vitals, exam findings, or history; assess clinical urgency conservatively (favour caution). " +
  "Return ONLY a valid JSON object with EXACTLY these keys: " +
  "triage (object with level one of 'Routine','Urgent','Emergency' and rationale string), " +
  "chief_complaint (string), hpi (string), review_of_systems (string), objective (string), assessment (string), " +
  "differential_diagnosis (array of strings each 'Condition - brief rationale'), " +
  "plan (array of strings, actionable steps including treatment considerations, patient education, follow-up), " +
  "recommended_investigations (array of strings each 'Test - rationale'), " +
  "risk_scores (array of objects each with name, value, interpretation - ONLY include validated scores that are fully computable from the provided data such as HEART, Wells, CHA2DS2-VASc, BMI, eGFR; empty array if data is insufficient), " +
  "prescription (array of objects each with drug, dose, route, frequency, duration, notes - SUGGESTED options for the physician to consider and adjust; account for the patient's age, weight and allergies; never present as final orders; empty array if none), " +
  "patient_instructions (object with english and urdu strings giving plain-language home-care guidance, warning signs, and when to seek help; urdu must be a natural Urdu translation of the english text), " +
  "drug_safety (array of strings noting interactions or contraindications considering current medications and allergies; empty array if none identified), " +
  "follow_up_questions (array of strings: additional history, examination, or vitals to obtain to narrow the differential), " +
  "allergy_alerts (array of strings), red_flags (array of strings), icd10_suggestions (array of objects each with code and description).";

const jsonBody =
  '={{ JSON.stringify({ model: "llama-3.3-70b-versatile", temperature: 0.2, response_format: { type: "json_object" }, messages: [ { role: "system", content: ' +
  JSON.stringify(sys) +
  ' }, { role: "user", content: "CONTEXT: " + ($json.context_json || "{}") + "\\n\\nBULLETS:\\n" + ($json.bullets || "") + "\\n\\nReturn the professional SOAP note and decision support as a JSON object now." } ] }) }}';

// ---- New Parse SOAP JSON code ----
const parseLines = [
  "const j = $json;",
  "const aiText = j.choices?.[0]?.message?.content ?? j.message?.content ?? j.content ?? j.text ?? '';",
  "",
  "if (!aiText) {",
  "  const upstream = String(j.error || j.message || '').trim();",
  "  const low = upstream.toLowerCase();",
  "  let hint = 'Open the AI node and check the API credential/model.';",
  "  if (low.includes('too many requests') || low.includes('quota') || low.includes('rate') || low.includes('429')) {",
  "    hint = 'Rate limit / no quota on the AI provider. Wait a moment or top up the account, then retry.';",
  "  } else if (low.includes('authoriz') || low.includes('api key') || low.includes('credential') || low.includes('invalid') || low.includes('bad request')) {",
  "    hint = 'The AI provider rejected the request. Check the API key, base URL, and model on the AI node.';",
  "  }",
  "  return { success: false, error: upstream || 'AI response was empty', hint };",
  "}",
  "",
  "let d;",
  "try { d = JSON.parse(String(aiText).replace(/```json|```/gi, '').trim()); }",
  "catch (e) { return { success: false, error: 'Invalid JSON from model', raw: aiText }; }",
  "",
  "const S = (v) => (v == null || v === '') ? '[not documented]' : (typeof v === 'string' ? v : JSON.stringify(v));",
  "const A = (v) => Array.isArray(v) ? v : (v ? [v] : []);",
  "const item = (x) => (typeof x === 'string' ? x : JSON.stringify(x));",
  "",
  "const tri = (d.triage && typeof d.triage === 'object') ? d.triage : {};",
  "const triLevel = tri.level ? String(tri.level) : 'Routine';",
  "const triWhy = S(tri.rationale);",
  "const cc = S(d.chief_complaint);",
  "const hpi = S(d.hpi != null ? d.hpi : d.subjective);",
  "const ros = S(d.review_of_systems);",
  "const obj = S(d.objective);",
  "const assess = S(d.assessment);",
  "const ddx = A(d.differential_diagnosis);",
  "const plan = A(d.plan);",
  "const invest = A(d.recommended_investigations);",
  "const risk = A(d.risk_scores);",
  "const rx = A(d.prescription);",
  "const drug = A(d.drug_safety);",
  "const followups = A(d.follow_up_questions);",
  "const allergy = A(d.allergy_alerts);",
  "const red = A(d.red_flags);",
  "const icd = A(d.icd10_suggestions);",
  "const pi = (d.patient_instructions && typeof d.patient_instructions === 'object') ? d.patient_instructions : {};",
  "const instrEn = typeof pi.english === 'string' ? pi.english : (typeof d.patient_instructions === 'string' ? d.patient_instructions : '');",
  "const instrUr = typeof pi.urdu === 'string' ? pi.urdu : '';",
  "",
  "const L = [];",
  "L.push('SOAP NOTE - DRAFT (for physician review; not a final medical record)');",
  "L.push('TRIAGE: ' + triLevel + (triWhy && triWhy !== '[not documented]' ? ' - ' + triWhy : ''));",
  "L.push('');",
  "L.push('CHIEF COMPLAINT: ' + cc);",
  "L.push('');",
  "L.push('S - SUBJECTIVE');",
  "L.push('History of Present Illness: ' + hpi);",
  "L.push('Review of Systems: ' + ros);",
  "L.push('');",
  "L.push('O - OBJECTIVE');",
  "L.push(obj);",
  "L.push('');",
  "L.push('A - ASSESSMENT');",
  "L.push(assess);",
  "if (ddx.length) { L.push('Differential Diagnosis:'); ddx.forEach((x, i) => L.push('  ' + (i + 1) + '. ' + item(x))); }",
  "L.push('');",
  "L.push('CLINICAL RISK SCORES');",
  "if (risk.length) { risk.forEach((r) => { const nm = (r && r.name) || ''; const vl = (r && r.value != null) ? r.value : ''; const ip = (r && r.interpretation) || ''; L.push('  ' + nm + ': ' + vl + (ip ? ' - ' + ip : '')); }); } else { L.push('  [none computed from provided data]'); }",
  "L.push('');",
  "L.push('P - PLAN');",
  "if (plan.length) { plan.forEach((x, i) => L.push('  ' + (i + 1) + '. ' + item(x))); } else { L.push('  [not documented]'); }",
  "L.push('');",
  "L.push('SUGGESTED PRESCRIPTION (Rx) - for physician approval');",
  "if (rx.length) { rx.forEach((r, i) => { const parts = [r && r.drug, r && r.dose, r && r.route, r && r.frequency, r && r.duration].filter(Boolean).join(' | '); L.push('  ' + (i + 1) + '. ' + (parts || item(r)) + ((r && r.notes) ? '  (' + r.notes + ')' : '')); }); } else { L.push('  [none suggested]'); }",
  "L.push('');",
  "L.push('RECOMMENDED INVESTIGATIONS');",
  "if (invest.length) { invest.forEach((x, i) => L.push('  ' + (i + 1) + '. ' + item(x))); } else { L.push('  [none suggested]'); }",
  "L.push('');",
  "L.push('SUGGESTED FOLLOW-UP QUESTIONS / EXAM');",
  "if (followups.length) { followups.forEach((x, i) => L.push('  ' + (i + 1) + '. ' + item(x))); } else { L.push('  [none suggested]'); }",
  "L.push('');",
  "if (drug.length) { drug.forEach((x) => L.push('** DRUG SAFETY: ' + item(x))); }",
  "if (allergy.length) { allergy.forEach((x) => L.push('** ALLERGY ALERT: ' + item(x))); }",
  "if (red.length) { red.forEach((x) => L.push('** RED FLAG: ' + item(x))); }",
  "if (drug.length || allergy.length || red.length) { L.push(''); }",
  "if (icd.length) { L.push('ICD-10 (suggested):'); icd.forEach((c) => { const code = (c && (c.code || c.icd10)) || ''; const desc = (c && (c.description || c.desc)) || (typeof c === 'string' ? c : ''); L.push('  ' + code + ' - ' + desc); }); L.push(''); }",
  "L.push('Generated: ' + new Date().toISOString());",
  "L.push('Disclaimer: AI-generated draft. Must be reviewed, verified, and signed by a licensed physician.');",
  "",
  "return {",
  "  success: true,",
  "  formatted_note: L.join('\\n'),",
  "  draft: {",
  "    triage: { level: triLevel, rationale: triWhy },",
  "    chief_complaint: cc, hpi, review_of_systems: ros, objective: obj, assessment: assess,",
  "    differential_diagnosis: ddx, plan, recommended_investigations: invest,",
  "    risk_scores: risk, prescription: rx,",
  "    patient_instructions: { english: instrEn, urdu: instrUr },",
  "    drug_safety: drug, follow_up_questions: followups,",
  "    allergy_alerts: allergy, red_flags: red, icd10_suggestions: icd",
  "  },",
  "  generated_at: new Date().toISOString(),",
  "};"
];
const parseCode = parseLines.join("\n");

let done = { ai: false, parse: false, ui: false };
for (const node of wf.nodes) {
  if (node.name === 'OpenAI - SOAP Draft') {
    node.parameters.jsonBody = jsonBody;
    done.ai = true;
  }
  if (node.name === 'Parse SOAP JSON') {
    node.parameters.jsCode = parseCode;
    done.parse = true;
  }
  if (node.name === 'Respond - Browser UI') {
    node.parameters = node.parameters || {};
    node.parameters.respondWith = 'text';
    node.parameters.responseBody = html;
    node.parameters.options = { responseHeaders: { entries: [{ name: 'Content-Type', value: 'text/html; charset=utf-8' }] } };
    done.ui = true;
  }
}
// ---- Add voice transcription pipeline (Groq Whisper), idempotent ----
if (!wf.nodes.some(n => n.name === 'Webhook - Transcribe')) {
  wf.nodes.push(
    { parameters: { httpMethod: 'POST', path: 'soap-transcribe', responseMode: 'responseNode', options: {} }, id: 'tr111111-1111-1111-1111-111111111111', name: 'Webhook - Transcribe', type: 'n8n-nodes-base.webhook', typeVersion: 2.1, position: [240, 640], webhookId: 'tr111111-1111-1111-1111-111111111112' },
    { parameters: { method: 'POST', url: 'https://api.groq.com/openai/v1/audio/transcriptions', authentication: 'predefinedCredentialType', nodeCredentialType: 'openAiApi', contentType: 'multipart-form-data', sendBody: true, bodyParameters: { parameters: [ { name: 'model', value: 'whisper-large-v3' }, { parameterType: 'formBinaryData', name: 'file', inputDataFieldName: 'file' } ] }, options: {} }, id: 'tr222222-2222-2222-2222-222222222222', name: 'Groq Whisper', type: 'n8n-nodes-base.httpRequest', typeVersion: 4.2, position: [520, 640], onError: 'continueRegularOutput', credentials: { openAiApi: { id: 'soapOpenAiCred01', name: 'Groq (Llama 3.3 70B)' } } },
    { parameters: { respondWith: 'json', responseBody: '={{ { text: ($json.text || ($json.error && $json.error.message) || "") } }}', options: {} }, id: 'tr333333-3333-3333-3333-333333333333', name: 'Respond - Transcript', type: 'n8n-nodes-base.respondToWebhook', typeVersion: 1.1, position: [800, 640] }
  );
  wf.connections['Webhook - Transcribe'] = { main: [[{ node: 'Groq Whisper', type: 'main', index: 0 }]] };
  wf.connections['Groq Whisper'] = { main: [[{ node: 'Respond - Transcript', type: 'main', index: 0 }]] };
  done.transcribe = 'added';
} else { done.transcribe = 'present'; }

fs.writeFileSync('/tmp/wf_out.json', JSON.stringify(wf, null, 2));
console.log('Updated: ' + JSON.stringify(done));
