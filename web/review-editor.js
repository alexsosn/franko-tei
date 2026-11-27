/* Pinned local proofreading batches, scoped to the selected source. No credentials or network writes. */
(() => {
  const KEY='franko-review-session-v1', LIMIT=32768, MAX=25;
  const sha=/^[0-9a-f]{40}$/, uid=/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/, pathPattern=/^pilot\/vol[1-5]_scan[0-9]{5}_(single_reading|exposed_reading|independent_image_reading_b|alternate_reading_0[12])\.json$/;
  let session, data, stored, key, serial=0, imageReady=false, storageFailed=false;
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
  const pending=()=>dirty()&&!event();
  const preparedStatus=()=>pending()?'Prepared locally; not submitted. Current edit is saved for the next batch.':'Prepared locally; not submitted.';
  const literal=(s,max)=>typeof s==='string'&&s.trim()&&[...s].length<=max&&![...s].some(c=>{let n=c.codePointAt(0);return /[\r\n\u0085\u2028\u2029⟦⟧]/u.test(c)||!(n===9||n>=32&&n<=0xd7ff||n>=0xe000&&n<=0xfffd||n>=0x10000&&n<=0x10ffff);});
  function persist(){
    if(localStorage.getItem(key)!==stored)fail('Local draft changed in another tab. Reopen without overwriting.');
    const next=JSON.stringify(session);
    try{localStorage.setItem(key,next);}catch(e){storageFailed=true;throw Error('Local storage failed. Copy your current edit before closing.');}stored=next;
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
    el('reviewPrepare').disabled=locked||!s.events.length||dirty()&&!pending()||bytes(json()).length>LIMIT;
    el('reviewEdit').readOnly=locked;el('reviewNote').readOnly=locked;
    const index=entries().findIndex(e=>e.line.id===s.selected);
    const pinnedPending=s.locked&&pending();
    el('reviewLine').disabled=storageFailed||pinnedPending;el('reviewPrevious').disabled=storageFailed||pinnedPending||index<=0;el('reviewNext').disabled=storageFailed||pinnedPending||index>=entries().length-1;
    for(const b of el('reviewCharacters').querySelectorAll('button'))b.disabled=locked;
    el('reviewProgress').textContent=s.events.length+' / '+MAX+' · '+bytes(json()).length+' / '+LIMIT+' B · '+tr(event()?.decision==='confirm'?'Confirmed locally':event()?.decision==='correct'?'Corrected locally':event()?.decision==='defer'?'Deferred locally':'No decision yet');
    el('reviewExport').hidden=!s.locked||storageFailed;el('reviewBundle').value=s.locked&&!storageFailed?json():'';el('reviewDiscard').disabled=storageFailed||s.locked;
  }
  // Source spans are code-point offsets, converted by the shared reader helper.
  // A native textarea cannot style ranges; choose a full historical/Greek
  // face only when every non-whitespace character is covered by that group.
  // Never apply source offsets to the edited value.
  function paintOriginal(line){
    const original=el('reviewOriginal'),ranges=languageRanges(line).sort((a,b)=>a.start-b.start);
    original.replaceChildren();
    let end=0;
    for(const r of ranges){
      original.append(document.createTextNode(line.text.slice(end,r.start)));
      const span=document.createElement('span');span.className='language-span';
      span.dataset.language=r.language;span.dataset.script=String(r.script??'');span.lang=r.language;
      span.textContent=line.text.slice(r.start,r.end);original.append(span);end=r.end;
    }
    original.append(document.createTextNode(line.text.slice(end)));
    el('reviewEdit').dataset.fontMode=sourceFontMode(line,ranges);
  }
  function paint(){
    const x=entry(),line=x.line;
    el('reviewLine').value=session.selected;paintOriginal(line);
    el('reviewEdit').value=session.working;el('reviewNote').value=session.note;
    el('reviewReasons').replaceChildren();
    for(const note of data.reading.uncertainty_notes??[])if(note.line_id===line.id){const p=document.createElement('p');p.textContent=note.reading+' — '+note.reason;el('reviewReasons').append(p);}
    el('reviewUncertainty').hidden=!el('reviewReasons').childElementCount;
    const img=el('reviewImage'),w=img.naturalWidth,h=img.naturalHeight,b=line.bbox_xywh;
    el('reviewCrop').classList.remove('review-full');el('reviewBox').hidden=true;
    if(imageReady&&validBox(b,w,h)){
      const top=Math.max(0,b[1]-b[3]),bottom=Math.min(h,b[1]+2*b[3]);
      el('reviewCrop').style.aspectRatio=w+'/'+(bottom-top);img.style.top=(-100*top/(bottom-top))+'%';el('reviewCrop').hidden=false;
      Object.assign(el('reviewBox').style,{left:100*b[0]/w+'%',width:100*b[2]/w+'%',top:100*(b[1]-top)/(bottom-top)+'%',height:100*b[3]/(bottom-top)+'%'});el('reviewBox').hidden=false;
    }else if(imageReady){el('reviewCrop').classList.add('review-full');el('reviewCrop').style.aspectRatio='auto';img.style.top='0';el('reviewCrop').hidden=false;}
    else el('reviewCrop').hidden=true;
    controls();
  }
  function select(id,force=false){
    if(session.locked&&pending())return;
    if(!force&&dirty()&&!confirm(tr('Discard the unrecorded edit for this line?'))){el('reviewLine').value=session.selected;return;}
    const x=entries().find(x=>x.line.id===id);if(!x)return;
    const e=session.events.find(e=>e.target.line_id===id);
    session.selected=id;session.working=e?.decision==='correct'?e.replacement:x.line.text;session.note=e?.note??'';persist();paint();
  }
  function run(fn){if(storageFailed)return;try{fn();}catch(e){status(e.message);try{if(localStorage.getItem(key)!==stored)storageFailed=true;}catch(_){storageFailed=true;}if(storageFailed)controls();}}
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
    el('reviewBody').hidden=true;el('reviewRecovery').hidden=true;imageReady=false;storageFailed=false;el('reviewCrop').hidden=true;
    const previousImage=el('reviewImage');previousImage.onload=null;previousImage.onerror=null;previousImage.removeAttribute('src');el('reviewFullImage').removeAttribute('href');
    el('reviewDialog').showModal();status('Loading pinned reading…');
    try{
      stored=null;
      if(!active)fail('No reading is available.');
      const path='pilot/vol'+active.data.volume+'_scan'+pad(active.data.scan_page)+'_'+active.suffix+'.json';
      if(!pathPattern.test(path)||ref!=='main'&&!sha.test(ref))fail('Review requires main or an exact commit SHA.');
      // A batch belongs to the selected candidate and reading ref. Keep legacy
      // drafts under their original key: switching pages never overwrites them.
      key=KEY+':'+ref+':'+path;
      stored=localStorage.getItem(key);
      if(stored===null){
        const legacy=localStorage.getItem(KEY);
        if(legacy!==null){
          let previous;
          try{previous=JSON.parse(legacy);}catch(e){key=KEY;stored=legacy;fail('Invalid local draft; preserved.');}
          if(!previous||typeof previous.path!=='string'||typeof previous.commit!=='string'){key=KEY;stored=legacy;fail('Invalid local draft; preserved.');}
          if(previous.path===path&&(ref==='main'||previous.commit===ref)){key=KEY;stored=legacy;}
        }
      }
      let s=stored!==null?JSON.parse(stored):null,commit;
      if(stored!==null){
        if(!s||s.path!==path||ref!=='main'&&s.commit!==ref||!uid.test(s.id)||!sha.test(s.blob)||!Array.isArray(s.events)||s.events.length>MAX||typeof s.working!=='string'||typeof s.note!=='string'||typeof s.locked!=='boolean')fail('Invalid local draft; preserved.');
        commit=s.commit;
      }else commit=ref==='main'?(await(await get('https://api.github.com/repos/alexsosn/franko-tei/commits/main')).json()).sha:ref;
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
      if(!entry()||s.locked&&dirty()&&!pending()||!s.events.every(valid)||new Set(s.events.map(e=>e.target.line_id)).size!==s.events.length||new Set(s.events.map(e=>e.event_id)).size!==s.events.length||bytes(json()).length>LIMIT)fail('Invalid local events; draft preserved.');
      persist();
      el('reviewSource').textContent='Volume '+v+' · scan '+n+' · '+d.reading.reader_id+' · '+commit.slice(0,12);
      el('reviewLine').replaceChildren(...list.map(({line,region},i)=>new Option((i+1)+' · '+region.kind+' · '+line.text.slice(0,32),line.id)));
      const img=el('reviewImage');el('reviewFullImage').href=asset(image.path);
      const ready=()=>{if(id!==serial||!el('reviewDialog').open)return;imageReady=img.complete&&img.currentSrc===el('reviewFullImage').href&&img.naturalWidth===p.width&&img.naturalHeight===p.height&&img.naturalWidth>0;uiText(el('reviewImageStatus'),imageReady?'Scan available; line geometry is approximate.':'Image unavailable; confirmation and correction disabled.');paint();};
      img.onload=ready;img.onerror=ready;img.src=asset(image.path);
      el('reviewBody').hidden=false;paint();if(img.complete)ready();
      status(s.locked?preparedStatus():'Draft saved locally.');
    }catch(e){if(id===serial){status(e.message);el('reviewRecovery').hidden=!stored;}}
  }
  el('reviewOpen').onclick=open;
  el('reviewClose').onclick=()=>el('reviewDialog').close();
  el('reviewDialog').addEventListener('close',()=>{if(!el('reviewDialog').open)serial++;});
  el('reviewLine').onchange=()=>run(()=>select(el('reviewLine').value));
  const move=n=>run(()=>{const list=entries(),i=list.findIndex(x=>x.line.id===session.selected)+n;if(list[i])select(list[i].line.id);});
  el('reviewPrevious').onclick=()=>move(-1);el('reviewNext').onclick=()=>move(1);
  for(const field of ['reviewEdit','reviewNote'])el(field).oninput=()=>run(()=>{session.working=el('reviewEdit').value;session.note=el('reviewNote').value;persist();controls();status('Draft saved locally.');});
  // Unicode TN41 and Slavonic Computing Initiative keyboard; no PUA glyphs.
  // Explicit sequences, not normalization. Dotted circle is preview only.
  const markKeys=[
    ['\u0301','Acute · Оксія'],['\u0300','Grave · Варія'],['\u0311','Inverted breve · Камора'],
    ['\u0486','Soft breathing · Псилі'],['\u0485','Rough breathing · Дасія'],
    ['\u0486\u0301','Breathing + acute · Ісо'],['\u0486\u0300','Breathing + grave · Апостроф'],['\u0486\u0311','Breathing + kamora · Великий апостроф'],
    ['\u0483','Titlo · Титло'],['\u0487','Pokrytie · Покриття'],['\ua66f','Vzmet · Взмет'],
    ['\u033e','Vertical tilde · Єрок'],['\u0303','Tilde · Тильда'],['\ua67d','Payerok · Паєрок'],['\ua67c','Kavyka · Кавика'],
    ['\u0306','Breve · Коротка'],['\u0308','Diaeresis · Кендема'],['\u030f','Double grave · Кендема'],
    ['\u0484','Palatalization · Палаталізація'],['\u0302','Circumflex · Циркумфлекс'],['\u0304','Macron · Макрон'],['\u0310','Candrabindu'],['\u0307','Dot above'],['\u0323','Dot below'],
    ['\u2e2f','Spacing yerok'],['\ua67e','Spacing kavyka'],['\ua67f','Spacing payerok'],['\u0482','Thousands sign']
  ];
  const letterKeys=[...('абвгдеёжѕзийіїјклмнопрстуфхцчшщъыьэюяєѣѧѩѫѭѡѻѽѿѹꙋꙑꙗѯѱѳѵѷꙁꙃꙅꙇꙉꙍꙏꙑꙓꙕꙙꙛꙝꙟꙡꙣꙥꙧꙩ')];
  const letters=[...new Set(letterKeys.flatMap(c=>[c,c.toUpperCase()]))].map(c=>[c,'Cyrillic letter']);
  const superNames='б в г д ж з к л м н о п р с т х ц ч ш щ ѳ ст а е ꙉ ꙋ ѣ ю ꙗ ѧ ѫ ѭ'.split(' ');
  const extraSuperNames='є і ї у ъ ы ь ѡ'.split(' ');
  const superscripts=superNames.map((n,i)=>[String.fromCodePoint(0x2de0+i),'Superscript '+n]).concat(extraSuperNames.map((n,i)=>[String.fromCodePoint(0xa674+i),'Superscript '+n]));
  const greek=[...('αβγδεζηθικλμνξοπρσςτυφχψω')].flatMap(c=>[c,c.toUpperCase()]).filter((c,i,a)=>a.indexOf(c)===i).map(c=>[c,'Greek letter']).concat([['\u0313','Smooth breathing'],['\u0314','Rough breathing'],['\u0342','Perispomeni'],['\u0345','Iota subscript'],['\u0301','Acute'],['\u0300','Grave'],['\u0308','Diaeresis']]);
  const keyGroups={marks:markKeys,letters,superscripts,greek};
  const codepoints=s=>[...s].map(c=>'U+'+c.codePointAt(0).toString(16).toUpperCase().padStart(4,'0')).join(' ');
  const insertLabel=(c,name)=>name+' · '+codepoints(c);
  // Both dialogs share the same raw Unicode keys and insertion behavior.
  // Review locking is scoped to its input, never the search query.
  function bindKeyboard({group,keys,info,input,locked=()=>false}){
    function render(){
      keys.replaceChildren();
      uiText(info,'Choose a character; marks are inserted after the caret.');
      for(const [char,name] of keyGroups[group.value]){
        const b=document.createElement('button');b.type='button';b.dataset.insert=char;
        b.textContent=/^\p{M}/u.test(char)?'◌'+char:char;
        b.title=insertLabel(char,name);b.setAttribute('aria-label',b.title);
        b.disabled=locked();
        // Avoid losing the selection on mouse activation; touch/keyboard use the native selection.
        b.addEventListener('mousedown',e=>e.preventDefault());
        b.onclick=()=>{
          if(input.readOnly||input.disabled||locked())return;
          input.setRangeText(char,input.selectionStart,input.selectionEnd,'end');input.focus();
          input.dispatchEvent(new Event('input',{bubbles:true}));
          info.removeAttribute('data-ui-text');info.textContent=insertLabel(char,name);
        };
        keys.append(b);
      }
    }
    group.addEventListener('change',render);
    render();
  }
  bindKeyboard({group:el('reviewKeyboardGroup'),keys:el('reviewCharacters'),info:el('reviewCharacterInfo'),input:el('reviewEdit'),locked:()=>!!session?.locked||storageFailed});
  bindKeyboard({group:el('searchKeyboardGroup'),keys:el('searchCharacters'),info:el('searchCharacterInfo'),input:el('query')});
  el('reviewSave').onclick=()=>run(()=>record(session.working===entry().line.text?'confirm':'correct'));
  el('reviewDefer').onclick=()=>run(()=>record('defer'));
  el('reviewUndo').onclick=()=>run(()=>{if(dirty()&&!confirm(tr('Discard the unrecorded edit for this line?')))return;session.events=session.events.filter(e=>e.target.line_id!==session.selected);session.working=entry().line.text;session.note='';persist();paint();});
  el('reviewPrepare').onclick=()=>run(()=>{if(el('reviewPrepare').disabled)return;session.locked=true;persist();controls();status(preparedStatus());el('reviewBundle').focus();el('reviewBundle').select();});
  el('reviewCopy').onclick=async()=>{try{await navigator.clipboard.writeText(el('reviewBundle').value);status('Copied.');}catch(e){el('reviewBundle').focus();el('reviewBundle').select();status('Select and copy the JSON manually.');}};
  function clearDraft(question){run(()=>{if(!confirm(tr(question)))return;if(localStorage.getItem(key)!==stored)fail('Local draft changed in another tab.');localStorage.removeItem(key);el('reviewDialog').close();});}
  el('reviewRecover').onclick=()=>{if(!stored)return;const url=URL.createObjectURL(new Blob([stored],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='franko-local-review-recovery.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  el('reviewRecoverDiscard').onclick=()=>{try{if(!confirm(tr('Discard this local draft and all its decisions?')))return;if(localStorage.getItem(key)!==stored)fail('Local draft changed in another tab.');localStorage.removeItem(key);el('reviewDialog').close();}catch(e){status(e.message);}};
  el('reviewReset').onclick=()=>run(()=>{
    if(!session.locked||!confirm(tr('Have you saved or submitted this bundle? Start the next batch?')))return;
    if(localStorage.getItem(key)!==stored)fail('Local draft changed in another tab.');
    const carry=pending(), list=entries(), used=new Set(session.events.map(e=>e.target.line_id));
    const current=entry(), next=carry||!used.has(current.line.id)?current:list.find(e=>!used.has(e.line.id))??current;
    const fresh={id:uuid(),commit:session.commit,path:session.path,blob:session.blob,
      selected:next.line.id,working:carry?session.working:next.line.text,note:carry?session.note:'',events:[],locked:false};
    const previous=session;
    session=fresh;
    try{persist();}catch(e){session=previous;throw e;}
    paint();status('Draft saved locally.');
  });
  el('reviewDiscard').onclick=()=>clearDraft('Discard this local draft and all its decisions?');
})();
