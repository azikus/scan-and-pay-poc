/* Same motion settings as the dedicated-team deck. All content remains local. */
const review=new URLSearchParams(location.search).has('review');
const audience=document.documentElement.dataset.audience==='true';
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
if(review)document.body.classList.add('review-mode');
const sections=[...document.querySelectorAll('.slides>section')];
document.querySelectorAll('[data-enter]').forEach(n=>{n.classList.add('enter');n.style.setProperty('--delay',n.dataset.enter+'ms')});
document.querySelectorAll('[data-step]').forEach(n=>{n.classList.add('fragment');n.dataset.fragmentIndex=n.dataset.step});
sections.forEach(s=>s.querySelectorAll('main > .sub,main > .eyebrow,thead').forEach(n=>{n.classList.add('enter');n.style.setProperty('--delay','170ms')}));
const counterFrames=new WeakMap();let slideTimer;
function countUp(node){cancelAnimationFrame(counterFrames.get(node));const final=Number(node.dataset.count),duration=reduced||review?0:1450,start=performance.now();node.textContent=duration?'0':final.toLocaleString('en-US');function tick(now){const t=duration?Math.min((now-start)/duration,1):1;node.textContent=Math.round(final*(1-Math.pow(1-t,3))).toLocaleString('en-US');if(t<1)counterFrames.set(node,requestAnimationFrame(tick))}counterFrames.set(node,requestAnimationFrame(tick))}
function enterSlide(slide){sections.forEach(s=>{if(s!==slide){s.classList.remove('is-entered');s.querySelectorAll('[data-count]').forEach(n=>cancelAnimationFrame(counterFrames.get(n)));s.querySelectorAll('svg').forEach(svg=>svg.pauseAnimations?.())}});clearTimeout(slideTimer);slideTimer=setTimeout(()=>{slide.classList.add('is-entered');slide.querySelectorAll('[data-count]').forEach(countUp)},review?0:60);if(review)slide.querySelectorAll('.fragment').forEach(n=>n.classList.add('visible'));slide.querySelectorAll('svg').forEach(svg=>review||reduced?svg.pauseAnimations?.():svg.unpauseAnimations?.());updateSculpture(slide)}
Reveal.initialize({width:1600,height:900,margin:0,minScale:.12,maxScale:2.5,center:false,hash:true,respondToHashChanges:true,controls:false,progress:true,slideNumber:false,transition:reduced||review?'none':'fade',transitionSpeed:'default',backgroundTransition:'fade',keyboard:true,overview:true,view:'slide',scrollActivationWidth:null,touch:true,help:true,autoAnimate:false,plugins:audience?[]:[RevealNotes],pdfSeparateFragments:false,showNotes:false,postMessage:true}).then(()=>enterSlide(Reveal.getCurrentSlide()));
Reveal.on('slidechanged',e=>enterSlide(e.currentSlide));
document.getElementById('prev').onclick=()=>Reveal.prev();document.getElementById('next').onclick=()=>Reveal.next();document.getElementById('notes').onclick=()=>Reveal.getPlugin('notes')?.open();document.getElementById('full').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen?.();

/* Equal-mass elastic collisions on the slide plane, rendered as shaded spheres. */
const ballScene=document.querySelector('.bouncing-scene');
const ballNodes=ballScene?[...ballScene.querySelectorAll('.brand-ball')]:[];
let ballFrame=0,ballLast=0,ballAccumulator=0,ballTime=0,wallContacts=0,ballContacts=0;
let balls=[];
function resetBalls(){
 balls=[{x:1040,y:230,r:112,vx:283.8375,vy:234.9},{x:1330,y:650,r:112,vx:-195.75,vy:-303.4125}];
 balls.forEach(b=>{b.impactAge=1;b.impactStrength=0;b.nx=1;b.ny=0});
 ballLast=0;ballAccumulator=0;ballTime=0;wallContacts=0;ballContacts=0;
}
function squeezeBall(b,nx,ny,speed){
 b.impactAge=0;b.impactStrength=Math.min(.055,.025+speed/14000);b.nx=nx;b.ny=ny;
}
function advanceBalls(dt){
 ballTime+=dt;
 for(const b of balls){
  b.impactAge+=dt;
  b.x+=b.vx*dt;b.y+=b.vy*dt;
  if(b.x<b.r){squeezeBall(b,-1,0,Math.abs(b.vx));b.x=2*b.r-b.x;b.vx=Math.abs(b.vx);wallContacts++}
  if(b.x>1600-b.r){squeezeBall(b,1,0,Math.abs(b.vx));b.x=2*(1600-b.r)-b.x;b.vx=-Math.abs(b.vx);wallContacts++}
  if(b.y<b.r){squeezeBall(b,0,-1,Math.abs(b.vy));b.y=2*b.r-b.y;b.vy=Math.abs(b.vy);wallContacts++}
  if(b.y>900-b.r){squeezeBall(b,0,1,Math.abs(b.vy));b.y=2*(900-b.r)-b.y;b.vy=-Math.abs(b.vy);wallContacts++}
 }
 const [a,b]=balls,dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy),limit=a.r+b.r;
 if(d<limit&&d>0){
  const nx=dx/d,ny=dy/d,overlap=(limit-d)/2+.01;
  a.x-=nx*overlap;a.y-=ny*overlap;b.x+=nx*overlap;b.y+=ny*overlap;
  const relative=(b.vx-a.vx)*nx+(b.vy-a.vy)*ny;
  if(relative<0){squeezeBall(a,nx,ny,-relative);squeezeBall(b,-nx,-ny,-relative);a.vx+=relative*nx;a.vy+=relative*ny;b.vx-=relative*nx;b.vy-=relative*ny;ballContacts++}
 }
 // Keep any separation correction within the physical screen bounds.
 for(const b of balls){b.x=Math.max(b.r,Math.min(1600-b.r,b.x));b.y=Math.max(b.r,Math.min(900-b.r,b.y))}
}
function paintBalls(){
 balls.forEach((b,i)=>{
  // Slight compression along the impact normal; smooth recovery without overshoot.
  const t=b.impactAge,release=Math.min(t/.18,1);
  const q=b.impactStrength*(1-release)*(1-release);
  const along=1-q,across=1/Math.sqrt(along),nx=b.nx,ny=b.ny;
  const xx=along*nx*nx+across*ny*ny,xy=(along-across)*nx*ny,yy=along*ny*ny+across*nx*nx;
  const ex=b.r*(Math.abs(xx)+Math.abs(xy)),ey=b.r*(Math.abs(xy)+Math.abs(yy));
  const x=Math.max(ex,Math.min(1600-ex,b.x+nx*b.r*q));
  const y=Math.max(ey,Math.min(900-ey,b.y+ny*b.r*q));
  ballNodes[i].style.setProperty('--ball-x',(x-b.r).toFixed(2)+'px');
  ballNodes[i].style.setProperty('--ball-y',(y-b.r).toFixed(2)+'px');
  ballNodes[i].style.setProperty('--ball-matrix',[xx,xy,xy,yy,0,0].map(v=>v.toFixed(5)).join(','));
  ballNodes[i].dataset.squeeze=q.toFixed(4);
  ballNodes[i].style.setProperty('--logo-spin',(Math.sin(ballTime*.3+i)*7).toFixed(2)+'deg');
 });
 ballScene.dataset.wallCollisions=String(wallContacts);ballScene.dataset.ballCollisions=String(ballContacts);
}
function updateSculpture(slide){
 cancelAnimationFrame(ballFrame);
 if(!ballScene||!slide.classList.contains('partnership-close'))return;
 resetBalls();paintBalls();
 if(reduced||review||document.hidden)return;
 function animate(now){
  if(document.hidden||!slide.classList.contains('present'))return;
  if(ballLast)ballAccumulator+=Math.min((now-ballLast)/1000,.06);
  ballLast=now;
  while(ballAccumulator>=1/120){advanceBalls(1/120);ballAccumulator-=1/120}
  paintBalls();ballFrame=requestAnimationFrame(animate);
 }
 ballFrame=requestAnimationFrame(animate);
}
addEventListener('visibilitychange',()=>{cancelAnimationFrame(ballFrame);if(!document.hidden)updateSculpture(Reveal.getCurrentSlide())});
