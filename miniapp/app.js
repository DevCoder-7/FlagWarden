const tg = window.Telegram?.WebApp;
if (tg) { tg.ready(); tg.expand(); }
const initData = tg?.initData || "";
const debugId = new URLSearchParams(location.search).get("debug_id") || "10001";

function authHeaders(){ return initData ? {"X-Telegram-Init-Data": initData} : {"X-Debug-Telegram-Id": debugId}; }
async function api(path) {
  const headers = authHeaders();
  const r = await fetch(path,{headers});
  if(!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

function esc(x){
  return String(x).replace(/[&<>"']/g, (m) => {
    const map = {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"};
    return map[m];
  });
}

async function load(){
 try{
  const [me,challenges,recs]=await Promise.all([api('/api/me'),api('/api/challenges'),api('/api/recommendations')]);
  document.getElementById('role').textContent=me.role;
  document.getElementById('hello').textContent=`Welcome${me.username?`, @${me.username}`:''}.`;
  document.getElementById('score').textContent=me.total_score;
  document.getElementById('streak').textContent=me.streak;
  document.getElementById('solved').textContent=me.solved.length;
  const skills=document.getElementById('skills');
  const skillEntries=Object.entries(me.skills).sort((a,b)=>b[1]-a[1]);
  skills.classList.remove('muted');
  skills.innerHTML=skillEntries.length?skillEntries.map(([k,v])=>`<div class="skill"><span>${esc(k)}</span><div class="bar"><i style="width:${Math.min(100,v)}%"></i></div><b>${Math.round(v)}</b></div>`).join(''):'<span class="muted">No mastery data yet. Solve a challenge to begin.</span>';
  document.getElementById('recommendations').innerHTML=recs.length?recs.map(r=>`<div class="recommendation"><strong>${esc(r.title)}</strong><small>${esc(r.reason)}</small></div>`).join(''):'<span class="muted">All published challenges solved.</span>';
  document.getElementById('challengeCount').textContent=`${challenges.length} published`;
  document.getElementById('challenges').innerHTML=challenges.map(c=>`<div class="challenge ${c.solved?'done':''}"><strong>${c.solved?'✅ ':''}${esc(c.title)}</strong><small>${esc(c.category)} · ${esc(c.difficulty)} · ${c.points} XP</small><div>${c.skills.map(s=>`<span class="tag">${esc(s)}</span>`).join('')}</div></div>`).join('');
  if(me.role!=='USER'){
    document.getElementById('studio').classList.remove('hidden');
    try{const drafts=await api('/api/admin/drafts'); document.getElementById('drafts').innerHTML=drafts.length?drafts.map(d=>`<div class="recommendation"><strong>${esc(d.challenge_id)} v${esc(d.version)}</strong><small>${esc(d.status)}</small></div>`).join(''):'<span class="muted">No challenge drafts yet.</span>';}catch(e){document.getElementById('drafts').textContent=e.message;}
  }
 }catch(e){document.querySelector('main').innerHTML=`<section class="card"><h2>Authentication required</h2><p class="muted">${esc(e.message)}</p><p>When running locally, use <code>?debug_id=10001</code> with ALLOW_DEBUG_AUTH=true.</p></section>`;}
}
load();

const draftTemplate={
  id:"custom-learning-001", title:"My Original Challenge", category:"web-security", difficulty:"easy", status:"draft", version:"1.0.0",
  author:"Glenn Josia Devano", reviewer:null, learning_objectives:["Explain one clearly scoped security concept."], skills:["web.example"], points:100,
  hints:[{cost:10,text:"Provide a progressive hint without revealing the answer."}],
  verifier:{type:"quiz_choice",choices:["Correct defensive concept","Distractor"],correct_index:0,flag_prefix:"FLAGWARDEN"},
  safety:{scope:"concept_only",notes:"Authorized educational use only."},
  debrief:{concept:"Security concept",why_it_works:"Explain why the concept matters.",remediation:"Explain the defensive control.",references:[]}
};
document.getElementById('draftJson').value=JSON.stringify(draftTemplate,null,2);
document.getElementById('createDraft').addEventListener('click',async()=>{
  const msg=document.getElementById('studioMessage');
  try{
    const challenge=JSON.parse(document.getElementById('draftJson').value);
    const r=await fetch('/api/admin/drafts',{method:'POST',headers:{...authHeaders(),'Content-Type':'application/json'},body:JSON.stringify({challenge})});
    if(!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
    const created=await r.json(); msg.textContent=`Saved ${created.challenge_id} as ${created.status}.`;
    const drafts=await api('/api/admin/drafts'); document.getElementById('drafts').innerHTML=drafts.map(d=>`<div class="recommendation"><strong>${esc(d.challenge_id)} v${esc(d.version)}</strong><small>${esc(d.status)}</small></div>`).join('');
  }catch(e){msg.textContent=e.message;}
});
