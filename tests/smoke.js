// Shift Ready smoke test for the installable app at the repository root.
// Usage (from the repo root):
//   python3 -m http.server 8765 &      # serve the app
//   node tests/smoke.js                # needs the `playwright` package and Chromium
// Checks: service worker + offline, feed, Upload & Learn from text and from a photo (on-device reader),
// Create with a saved video that survives a reload, backup export and import, and the update prompt.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');const os=require('os');
const ROOT=path.resolve(__dirname,'..');const FX=path.join(__dirname,'fixtures');const URL=process.env.APP_URL||'http://localhost:8765/';
(async()=>{
  const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:400,height:820},acceptDownloads:true});const p=await ctx.newPage();
  const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>m.type()==='error'&&!/fonts\.g/.test(m.text())&&errs.push(m.text()));
  const r={};const ok=(k,v)=>{r[k]=v};
  await p.goto(URL);await p.waitForTimeout(1500);
  ok('serviceWorker',await p.evaluate(async()=>!!(await navigator.serviceWorker.ready).active));
  ok('feedClips',await p.$$eval('#feed .clip',a=>a.length));
  await p.reload();await p.waitForTimeout(800);
  await ctx.setOffline(true);await p.reload();await p.waitForTimeout(1000);
  ok('offlineFeed',await p.$$eval('#feed .clip',a=>a.length)>0);
  await ctx.setOffline(false);
  // Upload & Learn: text
  await p.click('nav [data-view=learn]');await p.click('#ulNew');
  await p.fill('#ulText',"Simplex\tTransmit or receive, one at a time\nDuplex\tTransmit and receive at the same time\nMultiplex\tVoice and data at once\nRepeater\tRebroadcasts a weak signal at higher power");
  await p.click('#ulNext1');await p.click('#ulNext2');await p.waitForTimeout(300);
  await p.fill('#ulName','Radio types');await p.click('#ulCreate');await p.waitForTimeout(300);
  ok('textUploadClips',await p.evaluate(()=>document.querySelector('.scrim .sub')?.textContent||''));
  await p.click('.scrim [data-close]');
  // Upload & Learn: photo read on device
  await p.click('#ulNew');await p.click('#ulMode [data-m=photo]');
  await p.setInputFiles('#ulPhotos',path.join(FX,'ocrtest.png'));await p.waitForSelector('.ph img');
  await p.click('#ulNext1');
  await p.waitForFunction(()=>{const t=document.querySelector('[data-ocr]');return t&&!t.disabled&&t.value.length>10},null,{timeout:120000});
  ok('photoText',await p.$eval('[data-ocr]',t=>t.value));
  await p.click('#ulBack2');await p.click('#ulCancel');
  // Create with a video, then reload
  await p.click('nav [data-view=create]');await p.waitForTimeout(200);
  if(await p.$('#cSeg [data-m=cards]'))await p.click('#cSeg [data-m=cards]');
  await p.click('#genBtn');await p.waitForTimeout(300);
  await p.setInputFiles('#upFile',path.join(FX,'test.mp4'));await p.waitForTimeout(400);
  await p.click('#postScript');await p.waitForTimeout(800);
  await p.reload();await p.waitForTimeout(1500);
  ok('videoKeptAfterReload',await p.evaluate(()=>!!document.querySelector('#feed .clip.has-video')));
  // backup export + import on a fresh "device"
  await p.click('nav [data-view=learn]');await p.waitForTimeout(200);
  const [dl]=await Promise.all([p.waitForEvent('download',{timeout:5000}),p.click('#ulExportAll')]);
  const file=path.join(os.tmpdir(),'shift-ready-backup-test.json');await dl.saveAs(file);
  const ctx2=await b.newContext({viewport:{width:400,height:820}});const p2=await ctx2.newPage();p2.on('pageerror',e=>errs.push('device2: '+e.message));
  await p2.goto(URL);await p2.waitForTimeout(1000);await p2.click('nav [data-view=learn]');
  await p2.setInputFiles('#ulImportFile',file);await p2.waitForTimeout(600);
  ok('importedSets',await p2.$$eval('.ulset',a=>a.length));
  // update prompt: pretend a new build was deployed
  const vf=path.join(ROOT,'version.json');const keep=fs.readFileSync(vf,'utf8');
  try{fs.writeFileSync(vf,JSON.stringify({build:'99999999999999'}));await p.evaluate(()=>document.dispatchEvent(new Event('visibilitychange')));await p.waitForTimeout(1000);ok('updatePrompt',await p.isVisible('#updateBar'))}
  finally{fs.writeFileSync(vf,keep)}
  console.log(JSON.stringify(r,null,1));console.log('errors:',JSON.stringify(errs));
  await b.close();process.exit(errs.length?1:0);
})().catch(e=>{console.error(e);process.exit(1)});
