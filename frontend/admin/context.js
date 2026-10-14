'use strict';
let contextSignature = '';
const contextStatus = {observed:'Recorded as printed',inferred:'Suggested',derived:'Derived',unknown:'Unknown',ambiguous:'Needs review'};
const routeNames = {iban:'IBAN transfer',uk_domestic:'UK domestic transfer',biller_reference:'Biller reference',unresolved:'Route needs review'};
function contextBlock(title, hint, flag=false) {
  const block=element('div',undefined,'context-block');
  block.append(element('h3',title));
  const heading=element('p',undefined,'context-value');
  if(flag&&/^[A-Z]{2}$/.test(hint?.value||'')) {
    const symbol=element('span',String.fromCodePoint(...[...hint.value].map(c=>127397+c.charCodeAt(0))),'country-flag');
    symbol.setAttribute('aria-hidden','true');heading.append(symbol);
  }
  heading.append(element('strong',hint?.label||'Unknown'),element('span',contextStatus[hint?.status]||'Unknown','context-status'));
  block.append(heading,element('p',hint?.reason||'No context guidance was supplied by this server.','muted'));
  if(hint?.excerpts?.length) {
    const details=element('details',undefined,'context-evidence');
    details.append(element('summary','Supporting text · extractor claims'));
    for(const excerpt of hint.excerpts)details.append(element('blockquote',excerpt));
    block.append(details);
  }
  return block;
}
function renderInvoiceContext(scan) {
  const next=JSON.stringify([scan?.scan_id,scan?.runs?.map(r=>[r.id,r.payment,r.review_guidance])]);
  if(next===contextSignature)return;
  contextSignature=next;
  const panel=$('invoice-context');panel.replaceChildren();
  for(const run of scan?.runs||[]) {
    if(!run.payment)continue;
    const section=element('section',undefined,'context-run'),g=run.review_guidance;
    section.append(element('h2',scan.runs.length>1?`Invoice context · ${run.profile_id}`:'Invoice context'));
    if(!g) {
      section.append(element('p','Context guidance is unavailable for this server. Original readings remain in the JSON.','muted'));
      panel.append(section);continue;
    }
    const grid=element('div',undefined,'context-grid');
    grid.append(contextBlock('Issuer country',g.issuer_country,true),contextBlock('Document language',g.language));
    section.append(grid);
    if(g.review_summary)section.append(element('p',g.review_summary,'completeness'));
    for(const [index,candidate] of g.candidates.entries()) {
      const option=element('div',undefined,'context-option');
      option.append(element('h3',`Option ${index+1} · ${routeNames[candidate.route]||candidate.route}`));
      const printed=run.payment.candidates?.find(c=>c.id===candidate.candidate_id);
      for(const [key,label] of [['option_label','Payment option'],['due_date','Due'],['payment_condition','When to use']]) {
        if(printed?.[key]?.value)option.append(element('p',`${label}: ${printed[key].value}`));
      }
      option.append(contextBlock('Account country',candidate.account_country,true));
      const requirements=Object.entries(candidate.fields);
      const missing=requirements.filter(([path,rule])=>{
        const obs=path.split('/').slice(1).reduce((o,k)=>o?.[k],run.payment);
        return rule.requirement==='required'&&!(obs?.value!=null&&obs.state==='observed'&&obs.origin==='document'&&!obs.normalization?.some(n=>n.startsWith('draft_beneficiary_from_')));
      });
      option.append(element('p',missing.length?`${missing.length} required ${missing.length===1?'detail needs':'details need'} input.`:'No required details are missing.','completeness'));
      if(candidate.payment_channels?.length)option.append(element('p',`Payment service: ${candidate.payment_channels.join(', ')}`));
      if(candidate.payment_note)option.append(element('p',candidate.payment_note,'muted'));
      if(candidate.route==='unresolved'||(candidate.route==='biller_reference'&&!candidate.supported_draft))option.append(element('p','Payment route needs review. Field completeness does not resolve the destination.','muted'));
      for(const warning of candidate.warnings||[]) {
        option.append(element('p',`${warning.path.split('/').slice(3).join(' / ').replaceAll('_',' ')}: ${warning.message}`,'context-warning'));
      }
      const rules=element('details',undefined,'field-guidance');rules.append(element('summary','Field requirements'));
      const list=element('dl');
      for(const [path,rule] of requirements) {
        const name=path.split('/').slice(3).join(' / ').replaceAll('_',' ');
        list.append(element('dt',`${name} · ${rule.requirement.replaceAll('_',' ')}`),element('dd',rule.reason));
      }
      rules.append(list);option.append(rules);section.append(option);
    }
    section.append(element('p','Issuer country, document language and account country are separate. All payment drafts require review.','muted'));
    panel.append(section);
  }
}
