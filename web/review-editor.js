/* One pinned local proofreading batch. No credentials or network writes. */
(() => {
  const KEY='franko-review-session-v1', LIMIT=32768, MAX=25;
  const sha=/^[0-9a-f]{40}$/, uid=/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/, pathPattern=/^pilot\/vol[1-5]_scan[0-9]{5}_(single_reading|exposed_reading|independent_image_reading_b|alternate_reading_0[12])\.json$/;
  let session, data, stored, serial=0, imageReady=false, storageFailed=false;
  const el=id=>document.getElementById(id);
  const tr=s=>translateUI(s);
  const status=s=>uiText(el('reviewStatus'),s);
  const fail=s=>{throw Error(s);};
  const bytes=s=>new TextEncoder().encode(s);
  const uuid=()=>crypto.randomUUID();
  const json=()=>JSON.stringify({schema_version:'franko-review-bundle-v1',bundle_id:session.id,source_commit:session.commit,events:session.events});
  const entries=()=>data.reading.regions.flatMap(region=>region.lines.map(line=>({region,line})));
  const entry=()=>entries().find(e=>e.line.id===session.selected);
  const event=()=>session.events.find(e=>e.target.line_id===session.selected);
  const dirty=()=>session.working!==(event()?.decision==='correct'?event().replacement:entry().line.text)||session.note!==(event()?.note??'');
  const literal=(s,max)=>typeof s==='string'&&s.trim()&&[...s].length<=max&&![...s].some(c=>{let n=c.codePointAt(0);return /[\r\n\u0085\u2028\u2029⟦⟧]/u.test(c)||!(n===9||n>=32&&n<=0xd7ff||n>=0xe000&&n<=0xfffd||n>=0x10000&&n<=0x10ffff);});
  function persist(){
    if(localStorage.getItem(KEY)!==stored)fail('Local draft changed in another tab. Reopen without overwriting.');
    const next=JSON.stringify(session);
    try{localStorage.setItem(KEY,next);}catch(e){storageFailed=true;throw Error('Local storage failed. Copy your current edit before closing.');}stored=next;
  }
  async function hash(raw){
    const prefix=bytes('blob '+raw.byteLength+'\0'),all=new Uint8Array(prefix.length+raw.byteLength);
    all.set(prefix);all.set(new Uint8Array(raw),prefix.length);
    return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-1',all)),n=>n.toString(16).padStart(2,'0')).join('');
  }
  function target(e){
    return {candidate_path:session.path,candidate_blob:session.blob,asset_commit:data.asset_commit,image_sha256:data.source_image_sha256,reader_id:data.reading.reader_id,region_id:e.region.id,line_id:e.line.id,original:e.line.text};
  }
  function valid(e){
    const x=entries().find(x=>x.line.id===e?.target?.line_id);
    return x&&Object.keys(e).sort().join(',')==='decision,event_id,note,replacement,target'&&JSON.stringify(e.target)===JSON.stringify(target(x))&&uid.test(e.event_id)&&['confirm','correct','defer'].includes(e.decision)&&(e.note===null||literal(e.note,2048))&&(e.decision==='correct'?literal(e.replacement,4096)&&e.replacement!==x.line.text&&!x.line.unreadable_suffix:e.replacement===null);
  }
  function controls(){
    const s=session,x=entry(),changed=s.working!==x.line.text,locked=s.locked||storageFailed;
    uiText(el('reviewSave'),changed?'Save & next':'Confirm & next');
    el('reviewSave').disabled=locked||!imageReady||!literal(s.working,4096)||changed&&!!x.line.unreadable_suffix||s.note!==''&&!literal(s.note,2048);
    el('reviewDefer').disabled=locked||s.note!==''&&!literal(s.note,2048);
    el('reviewUndo').disabled=locked||!event();
    el('reviewSave').title=tr(changed?'Save correction':'Confirm unchanged');
    el('reviewDefer').title=tr('Defer');
    el('reviewPrepare').disabled=locked||!s.events.length||dirty()||bytes(json()).length>LIMIT;
    el('reviewEdit').readOnly=locked;el('reviewNote').readOnly=locked;
    const index=entries().findIndex(e=>e.line.id===s.selected);
    el('reviewLine').disabled=storageFailed;el('reviewPrevious').disabled=storageFailed||index<=0;el('reviewNext').disabled=storageFailed||index>=entries().length-1;
    for(const b of el('reviewCharacters').querySelectorAll('button'))b.disabled=locked;
    el('reviewProgress').textContent=s.events.length+' / '+MAX+' · '+bytes(json()).length+' / '+LIMIT+' B · '+tr(event()?.decision==='confirm'?'Confirmed locally':event()?.decision==='correct'?'Corrected locally':event()?.decision==='defer'?'Deferred locally':'No decision yet');
    el('reviewExport').hidden=!s.locked||storageFailed;el('reviewBundle').value=s.locked&&!storageFailed?json():'';el('reviewDiscard').disabled=storageFailed||s.locked;
  }
  function paint(){
    const x=entry(),line=x.line;
    el('reviewLine').value=session.selected;el('reviewOriginal').textContent=line.text;
    el('reviewEdit').value=session.working;el('reviewNote').value=session.note;
    el('reviewReasons').replaceChildren();
    for(const note of data.reading.uncertainty_notes??[])if(note.line_id===line.id){const p=document.createElement('p');p.textContent=note.reading+' — '+note.reason;el('reviewReasons').append(p);}
    el('reviewUncertainty').hidden=!el('reviewReasons').childElementCount;
    const img=el('reviewImage'),w=img.naturalWidth,h=img.naturalHeight,b=line.bbox_xywh;
    if(imageReady&&validBox(b,w,h)){
      const top=Math.max(0,b[1]-b[3]),bottom=Math.min(h,b[1]+2*b[3]);
      el('reviewCrop').style.aspectRatio=w+'/'+(bottom-top);img.style.top=(-100*top/(bottom-top))+'%';el('reviewCrop').hidden=false;
    }else el('reviewCrop').hidden=true;
    controls();
  }
  function select(id,force=false){
    if(!force&&dirty()&&!confirm(tr('Discard the unrecorded edit for this line?'))){el('reviewLine').value=session.selected;return;}
    const x=entries().find(x=>x.line.id===id);if(!x)return;
    const e=session.events.find(e=>e.target.line_id===id);
    session.selected=id;session.working=e?.decision==='correct'?e.replacement:x.line.text;session.note=e?.note??'';persist();paint();
  }
  function run(fn){if(storageFailed)return;try{fn();}catch(e){status(e.message);try{if(localStorage.getItem(KEY)!==stored)storageFailed=true;}catch(_){storageFailed=true;}if(storageFailed)controls();}}
  function record(decision){
    if(session.locked||decision!=='defer'&&!imageReady)fail('Cannot record this decision.');
    if(decision==='defer'&&dirty()&&session.working!==entry().line.text&&!confirm(tr('Discard the unrecorded edit for this line?')))return;
    const e={event_id:uuid(),target:target(entry()),decision,replacement:decision==='correct'?session.working:null,note:session.note||null};
    if(!valid(e))fail('Invalid line decision.');
    const prior=session.events,next=prior.filter(x=>x.target.line_id!==session.selected).concat(e);
    session.events=next;
    if(next.length>MAX||bytes(json()).length>LIMIT){session.events=prior;fail('Batch limit reached. Prepare existing decisions.');}
    session.working=e.replacement??entry().line.text;persist();paint();status('Draft saved locally.');
    const list=entries(),i=list.findIndex(x=>x.line.id===session.selected);if(list[i+1])select(list[i+1].line.id,true);
  }
  async function open(){
    const id=++serial,active=candidates[Number(el('choice').value)],ref=el('ref').value.trim(),selected=renderedLines.find(r=>r.btn.getAttribute('aria-pressed')==='true')?.line.id;
    el('reviewBody').hidden=true;imageReady=false;storageFailed=false;el('reviewCrop').hidden=true;
    el('reviewDialog').showModal();status('Loading pinned reading…');
    try{
      stored=localStorage.getItem(KEY);let s=stored?JSON.parse(stored):null,commit,path;
      if(s){commit=s.commit;path=s.path;if(!uid.test(s.id)||!sha.test(s.blob)||!Array.isArray(s.events)||s.events.length>MAX||typeof s.working!=='string'||typeof s.note!=='string'||typeof s.locked!=='boolean')fail('Invalid local draft; preserved.');}
      else{
        if(!active)fail('No reading is available.');
        commit=ref==='main'?(await(await get('https://api.github.com/repos/alexsosn/franko-tei/commits/main')).json()).sha:ref;
        path='pilot/vol'+active.data.volume+'_scan'+pad(active.data.scan_page)+'_'+active.suffix+'.json';
      }
      if(!sha.test(commit)||!pathPattern.test(path))fail('Review requires main or an exact commit SHA.');
      const raw=await(await get(readURL(commit,path),undefined,false,'force-cache')).arrayBuffer(),blob=await hash(raw),d=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw));
      const v=d.volume,n=d.scan_page;
      if(!/^[1-5]$/.test(v)||!Number.isInteger(n)||!path.startsWith('pilot/vol'+v+'_scan'+pad(n)+'_'))fail('Source identity mismatch.');
      const manifest=manifests.get(v)??await(await get(asset('vol'+v+'/manifest.json'))).json(),p=manifest.pages.find(p=>p.scan_page===n),image=p?.artifacts.find(a=>a.role==='page_image');
      if(id!==serial||!el('reviewDialog').open)return;
      if(!image||image.path!=='vol'+v+'/page-'+pad(n)+'.jpg')fail('Source image is missing.');checkDraft(d,v,n,image);
      if(s&&s.blob!==blob)fail('Pinned local source changed; draft preserved.');
      if(!s&&JSON.stringify(active.data)!==JSON.stringify(d))fail('Main changed during loading. Reload before review.');
      data=d;const list=entries();
      if(!list.length||list.some(x=>typeof x.region.id!=='string'||typeof x.line.id!=='string')||new Set(list.map(x=>x.line.id)).size!==list.length)fail('Invalid source line identities.');
      if(!s){const x=list.find(x=>x.line.id===selected)??list[0];s={id:uuid(),commit,path,blob,selected:x.line.id,working:x.line.text,note:'',events:[],locked:false};}
      session=s;
      if(!entry()||s.locked&&dirty()||!s.events.every(valid)||new Set(s.events.map(e=>e.target.line_id)).size!==s.events.length||new Set(s.events.map(e=>e.event_id)).size!==s.events.length||bytes(json()).length>LIMIT)fail('Invalid local events; draft preserved.');
      persist();
      el('reviewSource').textContent='Volume '+v+' · scan '+n+' · '+d.reading.reader_id+' · '+commit.slice(0,12);
      el('reviewLine').replaceChildren(...list.map(({line,region},i)=>new Option((i+1)+' · '+region.kind+' · '+line.text.slice(0,32),line.id)));
      const img=el('reviewImage');el('reviewFullImage').href=asset(image.path);
      const ready=()=>{if(id!==serial||!el('reviewDialog').open)return;imageReady=img.naturalWidth===p.width&&img.naturalHeight===p.height&&img.naturalWidth>0;uiText(el('reviewImageStatus'),imageReady?'Scan available; line geometry is approximate.':'Image unavailable; confirmation and correction disabled.');paint();};
      img.onload=ready;img.onerror=ready;img.src=asset(image.path);
      el('reviewBody').hidden=false;paint();if(img.complete)ready();
      status(s.locked?'Prepared locally; not submitted.':'Draft saved locally.');
    }catch(e){if(id===serial)status(e.message);}
  }
  el('reviewOpen').onclick=open;
  el('reviewClose').onclick=()=>el('reviewDialog').close();
  el('reviewDialog').addEventListener('close',()=>serial++);
  el('reviewLine').onchange=()=>run(()=>select(el('reviewLine').value));
  const move=n=>run(()=>{const list=entries(),i=list.findIndex(x=>x.line.id===session.selected)+n;if(list[i])select(list[i].line.id);});
  el('reviewPrevious').onclick=()=>move(-1);el('reviewNext').onclick=()=>move(1);
  for(const field of ['reviewEdit','reviewNote'])el(field).oninput=()=>run(()=>{session.working=el('reviewEdit').value;session.note=el('reviewNote').value;persist();controls();status('Draft saved locally.');});
  for(const char of ['ѣ','ѧ','ѫ','ꙗ','ꙑ','ѿ','ѡ','҃','҇','́','̀','̓','̔']){const b=document.createElement('button');b.type='button';b.textContent=/\p{M}/u.test(char)?'◌'+char:char;b.title='U+'+char.codePointAt(0).toString(16).toUpperCase();b.onclick=()=>{const input=el('reviewEdit');input.setRangeText(char,input.selectionStart,input.selectionEnd,'end');input.focus();input.dispatchEvent(new Event('input'));};el('reviewCharacters').append(b);}
  el('reviewSave').onclick=()=>run(()=>record(session.working===entry().line.text?'confirm':'correct'));
  el('reviewDefer').onclick=()=>run(()=>record('defer'));
  el('reviewUndo').onclick=()=>run(()=>{if(dirty()&&!confirm(tr('Discard the unrecorded edit for this line?')))return;session.events=session.events.filter(e=>e.target.line_id!==session.selected);session.working=entry().line.text;session.note='';persist();paint();});
  el('reviewPrepare').onclick=()=>run(()=>{if(el('reviewPrepare').disabled)return;session.locked=true;persist();controls();status('Prepared locally; not submitted.');el('reviewBundle').focus();el('reviewBundle').select();});
  el('reviewCopy').onclick=async()=>{try{await navigator.clipboard.writeText(el('reviewBundle').value);status('Copied.');}catch(e){el('reviewBundle').focus();el('reviewBundle').select();status('Select and copy the JSON manually.');}};
  function clearDraft(question){run(()=>{if(!confirm(tr(question)))return;if(localStorage.getItem(KEY)!==stored)fail('Local draft changed in another tab.');localStorage.removeItem(KEY);el('reviewDialog').close();});}
  el('reviewReset').onclick=()=>clearDraft('Have you saved or submitted this bundle? Remove the local batch?');
  el('reviewDiscard').onclick=()=>clearDraft('Discard this local draft and all its decisions?');
})();
