'use strict';
const $ = id => document.getElementById(id);
let token = '', epoch = 0, selected = null, scan = null, reviews = [], next = null, limit = 50, busy = false, tab = 'original', currentJSON = '', reviewError = '', signature = '';
let selectedSource='automated', artifactRevision=0, artifacts=null, artifactStamp='', artifactLoading=false, artifactError='', outputChoices=[], imageURL='', imageLoading=false, imageError='';
const pretty = value => JSON.stringify(value, null, 2);
const date = value => new Date(value).toLocaleString();
let profileData = null, methodsAt = 0, methodsBusy = false, methodsSignature = '', selectionDirty = false, savingMethod = false, methodRevision = 0;
const methodNames = {direct_vision:'Image → LLM',managed_ocr_rules:'Image → OCR → rules',managed_ocr_llm:'Image → OCR → LLM',prebuilt_document_mapping:'Image → document extraction',custom_document_mapping:'Image → custom document extraction',document_annotations:'Image → OCR with structured annotations'};
const methodDescriptions = {
  direct_vision:'The image goes directly to the selected vision model.',
  managed_ocr_rules:'OCR reads the image, then local rules extract the payment fields.',
  managed_ocr_llm:'OCR reads the image, then an LLM extracts the payment fields from the text and layout.'
};
const modelNames = {'gpt-4.1-mini-2025-04-14':'OpenAI · GPT-4.1 mini','gemini-3.5-flash-lite':'Google · Gemini 3.5 Flash-Lite','mistral-small-2603':'Mistral · Small 2603','claude-haiku-4-5-20251001':'Anthropic · Claude Haiku 4.5','Qwen/Qwen3.5-9B':'Together · Qwen 3.5 9B','mistral-ocr-4-1':'Mistral OCR 4.1'};
const providerNames = {openai:'OpenAI',gemini:'Google',mistral:'Mistral',anthropic:'Anthropic',together:'Together',xai:'xAI'};
const namedModel = (value,provider) => provider?`${providerNames[provider]||provider} · ${modelNames[value]?.split(' · ').at(-1)||value}`:modelNames[value]||value;
const methodName = value => methodNames[value] || value || 'Method unavailable';
const profileName = p => (p.method==='managed_ocr_llm'?`${modelNames[p.processor]||p.processor} → ${modelNames[p.model]||p.model}`:namedModel(p.model||p.processor,p.provider)||p.id)+(p.component_ids?.includes('invoice-context@1')?' · Invoice context':'');
const usable = profile => profile?.implemented && profile.enabled && profile.configured;
function element(tag,text,className) {const node=document.createElement(tag);node.textContent=text;if(className)node.className=className;return node;}
function selectedMethodProfile() {return profileData?.profiles.find(p=>p.id===$('extraction-profile').value);}
function updateMethodChoice() {
  const profile=selectedMethodProfile();
  const applied=!!profile&&profile.id===profileData?.default_extract_profile_id&&profile.version===profileData?.default_extract_profile_version;
  $('method-description').textContent=methodDescriptions[$('extraction-method').value]||'';
  $('apply-method').textContent=savingMethod?'Saving…':applied?'Selected':'Use for next scan';
  $('apply-method').disabled=savingMethod||!usable(profile)||applied;
  $('extraction-method').disabled=savingMethod||!$('extraction-method').options.length;
  $('extraction-profile').disabled=savingMethod||!$('extraction-profile').options.length;
}
function populateProfiles(preferred) {
  const choices=(profileData?.profiles||[]).filter(p=>usable(p)&&p.method===$('extraction-method').value);
  $('extraction-profile').replaceChildren(...choices.map(p=>{const option=element('option',profileName(p));option.value=p.id;return option;}));
  if(choices.some(p=>p.id===preferred))$('extraction-profile').value=preferred;
  updateMethodChoice();
}
function renderMethods() {
  const signature=pretty(profileData);if(signature===methodsSignature)return;methodsSignature=signature;
  const profiles=profileData?.profiles||[];
  const current=profiles.find(p=>p.id===profileData?.default_extract_profile_id);
  const matches=current?.version===profileData?.default_extract_profile_version;
  $('current-selection').textContent=current?`Current: ${methodName(current.method)} · ${profileName(current)}${usable(current)&&matches?'':' · unavailable'}`:'No current selection';
  const desired=selectionDirty?selectedMethodProfile():current;
  const methods=[...new Set(profiles.filter(usable).map(p=>p.method))].sort((a,b)=>Object.keys(methodNames).indexOf(a)-Object.keys(methodNames).indexOf(b));
  $('extraction-method').replaceChildren(...methods.map(method=>{const option=element('option',methodName(method));option.value=method;return option;}));
  if(desired&&methods.includes(desired.method))$('extraction-method').value=desired.method;
  populateProfiles(desired?.id);
}
async function loadMethods(force=false) {
  if(!token||methodsBusy||savingMethod||(!force&&Date.now()-methodsAt<60000))return;
  methodsBusy=true;const version=epoch,revision=methodRevision;
  try {
    const profiles=await api('/v1/profiles');
    if(version!==epoch||revision!==methodRevision)return;
    profileData=profiles;renderMethods();methodsAt=Date.now();
    $('methods-error').textContent='';
  }catch(e){
    if(version===epoch&&revision===methodRevision){profileData=null;renderMethods();$('current-selection').textContent='Could not load current selection';$('methods-error').textContent='Could not load methods. Use Refresh to try again.';}
  }finally{methodsBusy=false;}
}
async function saveMethod(event) {
  event.preventDefault();
  const profile=selectedMethodProfile();if(!usable(profile)||savingMethod)return;
  const version=epoch;methodRevision++;savingMethod=true;updateMethodChoice();$('methods-error').textContent='';
  try {
    await api('/v1/admin/selection',{method:'PUT',body:pretty({id:profile.id,version:profile.version})});
    if(version!==epoch)return;
    profileData.default_extract_profile_id=profile.id;profileData.default_extract_profile_version=profile.version;
    selectionDirty=false;renderMethods();methodsAt=0;
    $('methods-error').textContent='Saved. Existing drafts keep their original method.';
  }catch(e){if(version===epoch)$('methods-error').textContent=e.message;}
  finally{savingMethod=false;if(version===epoch)updateMethodChoice();}
}
function renderScanMethod() {
  $('scan-method').replaceChildren(...(scan?.runs||[]).map(run=>{
    const row=element('div','');
    const stages=run.diagnostics?.stages||[];
    const path=stages.map(s=>s.method==='interpretation'?'LLM interpretation':s.method==='vision'?'Image LLM':s.method==='rules'?'Rules':s.method==='ocr'?'OCR':s.method).join(' → ');
    const models=[...new Set(stages.map(s=>s.returned_model||s.requested_model).filter(Boolean))].join(' → ');
    const timing=run.diagnostics?.timings_ms?.total;
    row.append(element('strong',`${path||'Extraction'}${models?' · '+models:''}`),element('p',`${run.profile_id}@${run.profile_version}${timing==null?'':' · '+(timing/1000).toFixed(2)+' s backend'}`,'muted'));return row;
  }));
}
function error(message) { $('error').textContent = message; $('error').hidden = !message; }
async function request(path, options={}) {
  const response = await fetch(path, {...options,headers: {Authorization: `Bearer ${token}`,'Content-Type':'application/json'}, cache:'no-store', redirect:'error'});
  if (!response.ok) throw Error(response.status === 401 ? 'Access token was not accepted.' : `Could not load this data (${response.status}).`);
  return response;
}
async function api(path, options={}) {return (await request(path,options)).json();}
function resetArtifacts() {
  artifactRevision++;artifacts=null;artifactStamp='';artifactLoading=false;artifactError='';outputChoices=[];
  if(imageURL)URL.revokeObjectURL(imageURL);
  imageURL='';imageLoading=false;imageError='';
  $('uploaded-image').removeAttribute('src');$('sent-image').hidden=true;
  $('provider-choice').replaceChildren();$('provider-controls').hidden=true;
}
function beginSelection(id,source) {
  resetArtifacts();selected=id;selectedSource=source;scan=null;currentJSON='';
  if(tab==='image'&&source!=='mobile')tab='original';
  $('image-tab').hidden=source!=='mobile';$('json').textContent='Loading…';
  $('output-note').textContent='';$('review-controls').hidden=true;
  $('selected').hidden=true;$('empty').hidden=false;
}
function clearSelection() {
  resetArtifacts();selectedSource='automated';$('image-tab').hidden=true;
  selected=null; scan=null; reviews=[]; currentJSON=''; reviewError=''; signature='';
  renderInvoiceContext(null);
  $('selected').hidden=true; $('empty').hidden=false; $('json').textContent='';
  $('changes').replaceChildren(); $('review-choice').replaceChildren();
}
let networkBusy=false, networkSignature='';
function clearNetwork() {
  networkSignature=''; $('network-addresses').replaceChildren();
  $('network-status').textContent='Checking addresses…';
  $('network-warning').textContent=''; $('network-warning').hidden=true;
  $('network-copy-status').textContent='';
}
async function loadNetwork() {
  if(!token||networkBusy)return;
  networkBusy=true;const version=epoch;
  try {
    const data=await api('/v1/admin/connection');
    if(version!==epoch)return;
    const signature=JSON.stringify([data.automatic,data.addresses,data.warnings]);
    if(signature===networkSignature)return;
    networkSignature=signature;$('network-copy-status').textContent='';
    const addresses=data.addresses.filter(address=>address.kind!=='link_local');
    $('network-status').textContent=data.warnings.length?'Needs attention':addresses.length?'Ready':'No hotspot address';
    $('network-help').textContent=data.automatic
      ? 'Connect the Mac to your iPhone’s Personal Hotspot. Enter the Mac address in the app’s Connection settings, then tap Reconnect.'
      : 'Automatic network updates are off for this server. Use the address below if available.';
    $('network-addresses').replaceChildren(...addresses.map(address=>{
      const row=element('div',undefined,'network-address');
      const label=element('label','Mac address');
      const input=document.createElement('input');input.type='text';input.readOnly=true;input.value=address.url;
      input.setAttribute('aria-label',label.textContent);input.spellcheck=false;
      const copy=element('button','Copy address');copy.type='button';
      copy.addEventListener('click',async()=>{
        try {
          await navigator.clipboard.writeText(address.url);
          if(version===epoch)$('network-copy-status').textContent='Address copied.';
        } catch {
          if(version!==epoch)return;
          input.focus();input.select();
          $('network-copy-status').textContent='Address selected. Copy it using your device’s copy command.';
        }
      });
      label.append(input);row.append(label,copy);return row;
    }));
    if(!addresses.length)$('network-addresses').append(element('p','Connect the Mac to your iPhone’s Personal Hotspot.','muted'));
    $('network-warning').textContent=data.warnings.join(' ');$('network-warning').hidden=!data.warnings.length;
  } catch(e) {
    if(version!==epoch)return;
    clearNetwork();$('network-status').textContent='Unavailable';
    $('network-warning').textContent='Could not refresh Mac addresses. Keep the admin open on the Mac at 127.0.0.1 to recover after a network change.';
    $('network-warning').hidden=false;
  } finally {networkBusy=false;}
}
function disconnect() {
  epoch++; token=''; limit=50; clearSelection();clearNetwork();
  profileData=null; methodsAt=0; methodsSignature=''; selectionDirty=false;
  $('current-selection').textContent='';$('method-description').textContent='';$('methods-error').textContent='';
  for(const id of ['extraction-method','extraction-profile','scan-method'])$(id).replaceChildren();
  updateMethodChoice();
  $('workspace').hidden=true; $('login').hidden=false; $('disconnect').hidden=true; $('connection').textContent='Disconnected';
  $('scans').replaceChildren(); $('token').value=''; error('');
}
function valueAt(payment, path) { return path.split('/').slice(1).reduce((obj,key)=>obj?.[key],payment)?.value ?? null; }
function renderOutput() {
  if (!scan) return;
  for(const name of ['original','provider','image','reviews'])$(name+'-tab').setAttribute('aria-selected',tab===name);
  $('output').setAttribute('aria-labelledby',tab+'-tab');
  $('json').hidden=tab==='image';$('sent-image').hidden=tab!=='image'||!imageURL;
  $('provider-controls').hidden=tab!=='provider'||!outputChoices.length;
  $('copy').hidden=tab==='image';$('copy').disabled=false;$('copy').textContent='Copy JSON';
  $('review-controls').hidden=tab!=='reviews'||reviews.length===0;
  $('review-count').textContent=reviews.length;
  let output=scan;
  $('output-note').textContent='';
  if(tab==='image') {
    currentJSON='';$('output-note').textContent=imageError||(imageURL?'':'Loading image…');
    loadImage();return;
  }
  if(tab==='provider') {
    const choice=outputChoices.find(item=>item.key===$('provider-choice').value);
    currentJSON=choice?pretty(choice.output.value):'';
    $('json').textContent=currentJSON;$('json').hidden=!choice||!!choice.output.error;
    $('copy').disabled=!currentJSON||!!choice?.output.error;
    $('output-note').textContent=artifactError||choice?.output.error||(choice?choice.note:artifactLoading||!artifacts?'Loading saved output…':'No provider output was saved for this scan.');
    loadArtifacts();return;
  }
  if(tab==='original')$('output-note').textContent='Formatted backend result.';
  if(tab==='reviews') {
    const review=reviews.find(r=>r.id===$('review-choice').value)||reviews.at(-1);
    if(review) {
      output=review;
      const payment=scan.runs.find(r=>r.id===review.run_id)?.payment;
      $('changes').replaceChildren(...Object.entries(review.values).map(([path,value])=>{
        const row=document.createElement('tr'); const original=valueAt(payment,path);
        for(const [i,item] of [path,original,value].entries()) {const cell=document.createElement('td');cell.textContent=item===null?'null':item;if(item===null)cell.classList.add('null');if(i===2&&original!==value)cell.classList.add('changed');row.append(cell);}return row;
      }));
    } else {output={reviews:[]};$('output-note').textContent=reviewError||'No mobile edits yet.';}
  }
  const updated=pretty(output);
  if(currentJSON!==updated){currentJSON=updated;$('json').textContent=currentJSON;}
}

const stageNames={vision:'Image → LLM',ocr:'OCR',interpretation:'LLM',rules:'Rules',unassigned:'Run output'};
const outputNames={provider_response:'Provider response',ocr_document:'OCR text + layout',llm_input:'Text sent to LLM'};
const outputNotes={provider_response:'Saved provider response, before backend field mapping.',ocr_document:'Text and layout extracted from the OCR response.',llm_input:'The saved OCR text and layout passed to the LLM.'};
async function loadArtifacts() {
  if(!scan||tab!=='provider'||artifactLoading||artifactStamp===scan.updated_at)return;
  const id=selected,revision=artifactRevision,stamp=scan.updated_at;
  artifactLoading=true;artifactError='';
  try {
    const data=await api(`/v1/admin/scans/${encodeURIComponent(id)}/artifacts`);
    if(revision!==artifactRevision)return;
    artifacts=data;artifactStamp=stamp;
    const prior=$('provider-choice').value;
    outputChoices=data.runs.flatMap(run=>run.stages.flatMap((stage,stageIndex)=>(stage.outputs.length?stage.outputs:stage.execution==='external'?[{kind:'provider_response',error:'No response was saved for this stage.'}]:[]).map((output,index)=>({
      key:`${run.run_id}/${stage.stage_id||'run'}/${index}`,output,note:outputNotes[output.kind],
      label:`${data.runs.length>1?run.profile_id+' · ':''}${stageIndex+1}. ${stageNames[stage.method]||stage.method}${stage.provider?' · '+stage.provider:''} · ${outputNames[output.kind]}${output.kind==='provider_response'&&stage.outputs.filter(o=>o.kind==='provider_response').length>1?' '+(index+1):''}`
    }))));
    $('provider-choice').replaceChildren(...outputChoices.map(choice=>{const option=element('option',choice.label);option.value=choice.key;return option;}));
    if(outputChoices.some(choice=>choice.key===prior))$('provider-choice').value=prior;
  }catch(e){if(revision===artifactRevision){artifactError=e.message+' Use Refresh to try again.';artifactStamp=stamp;}}
  finally{if(revision===artifactRevision){artifactLoading=false;renderOutput();}}
}
async function loadImage() {
  if(!scan||selectedSource!=='mobile'||imageURL||imageLoading||imageError)return;
  const id=selected,revision=artifactRevision;imageLoading=true;
  try {
    const response=await request(`/v1/admin/scans/${encodeURIComponent(id)}/image`);
    const blob=await response.blob();
    if(revision!==artifactRevision)return;
    imageURL=URL.createObjectURL(blob);$('uploaded-image').src=imageURL;
  }catch(e){if(revision===artifactRevision)imageError=e.message+' Use Refresh to try again.';}
  finally{if(revision===artifactRevision){imageLoading=false;renderOutput();}}
}

async function loadDetail(id,version) {
  const [original, mobile]=await Promise.allSettled([api(`/v1/scans/${encodeURIComponent(id)}`),api(`/v1/scans/${encodeURIComponent(id)}/reviews`)]);
  if(version!==epoch||selected!==id)return;
  if(original.status==='rejected')throw original.reason;
  scan=original.value; reviews=mobile.status==='fulfilled'?mobile.value.reviews:[];
  reviewError=mobile.status==='rejected'?'Mobile edits could not be loaded. Try Refresh.':'';
  const prior=$('review-choice').value;
  $('review-choice').replaceChildren(...reviews.map(r=>{const o=document.createElement('option');o.value=r.id;o.textContent=`${date(r.received_at)} · ${r.id.slice(0,8)}`;return o;}));
  $('review-choice').value=reviews.some(r=>r.id===prior)?prior:(reviews.at(-1)?.id||'');
  $('kind').textContent=scan.execution_kind==='synthetic_fixture'?'Synthetic fixture':'Extraction';
  $('scan-title').textContent=id;$('scan-meta').textContent=`${scan.state} · ${date(scan.created_at)}`;
  $('empty').hidden=true;$('selected').hidden=false;renderOutput();renderScanMethod();renderInvoiceContext(scan);
}
function renderList(items) {
  const nextSignature=pretty([items,selected]);if(signature===nextSignature)return;signature=nextSignature;
  $('scans').replaceChildren(...items.map(item=>{
    const b=document.createElement('button');b.className='scan';b.setAttribute('aria-current',item.scan_id===selected);
    const title=document.createElement('strong');title.textContent=item.scan_id.slice(0,17);
    const source=document.createElement('span');source.className='source';source.textContent=item.source==='mobile'?'Mobile':'Automated';
    const profile=document.createElement('small');profile.textContent=item.profiles.join(' · ');
    const status=document.createElement('span');status.className='state';status.textContent=item.outcomes.filter(Boolean).join(' / ')||item.state;
    const time=document.createElement('time');time.textContent=date(item.created_at);time.dateTime=item.created_at;
    b.append(title,source,profile,status,time);b.addEventListener('click',()=>{
      beginSelection(item.scan_id,item.source);
      document.querySelectorAll('.scan').forEach(x=>x.setAttribute('aria-current',x===b));
      loadDetail(selected,epoch).catch(e=>error(e.message));
    });return b;
  }));
  if(!items.length)$('scans').textContent='No matching scans.';
}
async function refresh() {
  if(!token||busy)return;busy=true;const version=epoch,source=$('source').value;
  loadMethods().catch(()=>{});loadNetwork();
  try {
    const pages=[];for(let offset=0;offset<limit;offset+=50){const result=await api(`/v1/admin/scans?limit=50&offset=${offset}${source?'&source='+encodeURIComponent(source):''}`);pages.push(...result.scans);next=result.next_offset;if(next===null)break;}
    if(version!==epoch)return;
    if(!pages.some(item=>item.scan_id===selected))clearSelection();
    if(!selected&&pages.length)beginSelection(pages[0].scan_id,pages[0].source);
    renderList(pages); $('scan-count').textContent=pages.length;$('more').hidden=next===null;
    if(selected)await loadDetail(selected,version);
    if(version===epoch){$('connection').textContent='Connected';error('');}
  }catch(e){if(version===epoch){error(e.message);$('connection').textContent='Connection interrupted';}}
  finally{busy=false;if(version!==epoch&&token)refresh();}
}
$('login-form').addEventListener('submit',async e=>{e.preventDefault();token=$('token').value.trim();epoch++;clearSelection();await refresh();if(scan||!$('error').textContent){$('login').hidden=true;$('workspace').hidden=false;$('disconnect').hidden=false;$('token').value='';}});
$('disconnect').addEventListener('click',disconnect);$('refresh').addEventListener('click',()=>{artifactStamp='';artifactError='';imageError='';loadMethods(true).catch(()=>{});refresh();});$('more').addEventListener('click',()=>{limit+=50;refresh();});
$('method-form').addEventListener('submit',saveMethod);
$('extraction-method').addEventListener('change',()=>{selectionDirty=true;$('methods-error').textContent='';populateProfiles(profileData?.default_extract_profile_id);});
$('extraction-profile').addEventListener('change',()=>{selectionDirty=true;$('methods-error').textContent='';updateMethodChoice();});
$('source').addEventListener('change',()=>{epoch++;limit=50;clearSelection();refresh();});
for(const name of ['original','provider','image','reviews'])$(name+'-tab').addEventListener('click',()=>{tab=name;renderOutput();});
for(const id of ['review-choice','provider-choice'])$(id).addEventListener('change',renderOutput);
$('copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(currentJSON);$('copy').textContent='Copied';setTimeout(()=>$('copy').textContent='Copy JSON',1500);}catch{error('Clipboard is unavailable. Select the JSON text to copy it.');}});
$('theme').value=adminThemePreference;
$('theme').addEventListener('change',()=>{
  applyAdminTheme($('theme').value);
  try {localStorage.setItem('scanpay-admin-theme',adminThemePreference);} catch { /* Theme remains usable for this visit. */ }
});
setInterval(()=>{if(!document.hidden&&token)refresh();},2500);
