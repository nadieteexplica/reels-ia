import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';

const STYLE=window.STYLE||'A';
const LABEL={A:'MUESTRA A · PIXAR SUAVE',B:'MUESTRA B · CARICATURA',C:'MUESTRA C · PLASTILINA'}[STYLE];
const W=1080,H=1920,DUR=5.1;
const WORDS=(await (await fetch('../ep1-helado/words.json')).json()).filter(w=>w.s<DUR-0.05);

// ---------- utilidades ----------
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)),lerp=(a,b,t)=>a+(b-a)*t;
const ss=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t);};
const E={lin:t=>t,io:t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,o:t=>1-Math.pow(1-t,3),i:t=>t*t*t,
  back:t=>{const c1=2.2,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2);},
  el:t=>t<=0?0:t>=1?1:Math.pow(2,-9*t)*Math.sin((t*9-0.75)*(2*Math.PI)/3)+1};
function tr(keys){return t=>{if(t<=keys[0][0])return keys[0][1];for(let i=1;i<keys.length;i++){if(t<=keys[i][0]){const[t0,v0]=keys[i-1],[t1,v1,e='io']=keys[i];const u=E[e](clamp((t-t0)/(t1-t0)));return Array.isArray(v0)?v0.map((a,j)=>lerp(a,v1[j],u)):lerp(v0,v1,u);}}return keys[keys.length-1][1];};}
function mul(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}}
const V3=(x,y,z)=>new THREE.Vector3(x,y,z);
function canvasTex(w,h,draw,srgb=true){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);const t=new THREE.CanvasTexture(c);if(srgb)t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;}
const SOFT=canvasTex(128,128,(g)=>{const gr=g.createRadialGradient(64,64,0,64,64,64);gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(0.35,'rgba(255,255,255,.55)');gr.addColorStop(1,'rgba(255,255,255,0)');g.fillStyle=gr;g.fillRect(0,0,128,128);});

// ---------- renderer ----------
const canvas=document.getElementById('gl');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(1);renderer.setSize(W,H,false);canvas.style.width=W+'px';canvas.style.height=H+'px';
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;
if(STYLE==='B')renderer.toneMapping=THREE.NoToneMapping;else{renderer.toneMapping=THREE.NeutralToneMapping;renderer.toneMappingExposure=1.0;}
const scene=new THREE.Scene();
const gradTex=(stops)=>canvasTex(16,1024,(g,w,h)=>{const gr=g.createLinearGradient(0,0,0,h);stops.forEach(([o,c])=>gr.addColorStop(o,c));g.fillStyle=gr;g.fillRect(0,0,w,h);});
scene.background=gradTex(STYLE==='B'?[[0,'#29a9f0'],[0.55,'#7fd3ff'],[1,'#c4efff']]:STYLE==='C'?[[0,'#6cc2f0'],[0.6,'#b5e3f7'],[1,'#f2f0e4']]:[[0,'#3aa6ec'],[0.55,'#93d8ff'],[1,'#dff6ff']]);
scene.fog=new THREE.Fog(STYLE==='C'?'#d9eef3':'#c9ecff',13,46);
if(STYLE!=='B'){const pm=new THREE.PMREMGenerator(renderer);scene.environment=pm.fromScene(new RoomEnvironment(),0.04).texture;scene.environmentIntensity=STYLE==='C'?0.18:0.3;}

// ---------- materiales por estilo ----------
const grad3=new THREE.DataTexture(new Uint8Array([95,95,95,255,175,175,175,255,255,255,255,255]),3,1);grad3.minFilter=grad3.magFilter=THREE.NearestFilter;grad3.generateMipmaps=false;grad3.needsUpdate=true;
let clayBump=null;
if(STYLE==='C'){const r=mul(9);clayBump=canvasTex(512,512,(g,w,h)=>{g.fillStyle='#808080';g.fillRect(0,0,w,h);
  for(let i=0;i<2600;i++){const x=r()*w,y=r()*h,s=1+r()*5;g.fillStyle=`rgba(${r()<.5?255:0},${r()<.5?255:0},${r()<.5?255:0},${0.05+r()*0.08})`;g.beginPath();g.arc(x,y,s,0,7);g.fill();}
  g.lineWidth=1.6;for(let k=0;k<14;k++){const cx=r()*w,cy=r()*h,a0=r()*6;for(let j=0;j<9;j++){g.strokeStyle=`rgba(${j%2?255:40},${j%2?255:40},${j%2?255:40},0.13)`;g.beginPath();g.ellipse(cx,cy,10+j*5,7+j*4,a0,0.2,2.6);g.stroke();}}},false);
  clayBump.wrapS=clayBump.wrapT=THREE.RepeatWrapping;clayBump.repeat.set(2,2);}
function mat(color,o={}){let m;const c=new THREE.Color(color);
  if(STYLE==='B')m=new THREE.MeshToonMaterial({color:c,gradientMap:grad3});
  else if(STYLE==='C')m=new THREE.MeshStandardMaterial({color:c,roughness:o.gloss?0.32:0.8,metalness:0,bumpMap:o.noBump?null:clayBump,bumpScale:o.noBump?0:2.6});
  else m=new THREE.MeshPhysicalMaterial({color:c,roughness:o.gloss?0.1:(o.rough??0.5),clearcoat:o.gloss?1:(o.cc??0.1),clearcoatRoughness:0.3,sheen:o.sheen?0.8:0,sheenColor:new THREE.Color(o.sheenColor||'#ffcdb8'),sheenRoughness:0.45});
  if(o.map)m.map=o.map;if(o.transparent){m.transparent=true;m.depthWrite=false;}
  if(o.emissive){m.emissive=new THREE.Color(o.emissive);m.emissiveIntensity=o.ei??1;}
  if(o.fog===false)m.fog=false;return m;}
function outline(mesh,th=0.016){if(STYLE!=='B')return mesh;
  const m=new THREE.MeshBasicMaterial({color:0x1d1633,side:THREE.BackSide});
  m.onBeforeCompile=s=>{s.uniforms.uT={value:th};s.vertexShader=s.vertexShader.replace('void main() {','uniform float uT;\nvoid main() {').replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed += normalize(normal)*uT;');};
  const o=new THREE.Mesh(mesh.geometry,m);o.castShadow=false;mesh.add(o);mesh.userData.outline=o;return mesh;}
function lumpy(geo,amt=0.012,f=7,seed=1){if(STYLE!=='C')return geo;amt*=1.8;const p=geo.attributes.position,n=geo.attributes.normal;
  for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i);const d=amt*(Math.sin(x*f+seed)*Math.sin(y*f*1.3+seed*2)+0.6*Math.sin(z*f*1.7+x*3+seed)*Math.cos(y*f*0.7));
    p.setXYZ(i,x+n.getX(i)*d,y+n.getY(i)*d,z+n.getZ(i)*d);}geo.computeVertexNormals();return geo;}
// congelamiento: azul que sube desde la boca (y en coordenadas de la cabeza)
const FZ={lvl:{value:0},lo:{value:-1},amt:{value:0},ice:{value:new THREE.Color(STYLE==='B'?'#8fd6ff':'#a8dcff')}};
function freezeMat(m,py=0){m.onBeforeCompile=(s)=>{s.uniforms.uLvl=FZ.lvl;s.uniforms.uLo=FZ.lo;s.uniforms.uAmt=FZ.amt;s.uniforms.uIce=FZ.ice;s.uniforms.uPy={value:py};
  s.vertexShader=s.vertexShader.replace('void main() {','varying float vFy;\nuniform float uPy;\nvoid main() {').replace('#include <begin_vertex>','#include <begin_vertex>\nvFy=(position.y+uPy+0.6)/1.2;');
  s.fragmentShader=s.fragmentShader.replace('void main() {','varying float vFy;\nuniform float uLvl;\nuniform float uLo;\nuniform float uAmt;\nuniform vec3 uIce;\nvoid main() {').replace('#include <color_fragment>','#include <color_fragment>\n{float kf=smoothstep(uLo-0.12,uLo,vFy)*(1.0-smoothstep(uLvl-0.12,uLvl,vFy))*uAmt;diffuseColor.rgb=mix(diffuseColor.rgb,uIce,kf);}');};return m;}
const sh=m=>{m.castShadow=true;m.receiveShadow=true;return m;};

// ---------- luces ----------
{const hemi=new THREE.HemisphereLight(STYLE==='C'?'#fff1e0':'#e8f6ff',STYLE==='B'?'#a9d98a':'#9ccf72',STYLE==='B'?1.1:1.15);scene.add(hemi);
 const key=new THREE.DirectionalLight(STYLE==='C'?'#ffe4c8':'#fff1de',STYLE==='B'?2.6:2.7);key.position.set(STYLE==='C'?-3:3,5.5,4.5);key.castShadow=true;key.shadow.mapSize.set(2048,2048);
 Object.assign(key.shadow.camera,{left:-2.5,right:2.5,top:3.2,bottom:-1,near:1,far:16});key.shadow.radius=4;key.shadow.bias=-0.0004;key.shadow.normalBias=0.02;key.target.position.set(0,1,0);scene.add(key,key.target);
 const rim=new THREE.DirectionalLight('#d8f2ff',STYLE==='B'?0.9:1.4);rim.position.set(STYLE==='C'?3:-3.5,3,-4);scene.add(rim);}

// ---------- escenario: plaza ----------
{const g=new THREE.Mesh(new THREE.CircleGeometry(70,64),mat(STYLE==='B'?'#79cf4c':STYLE==='C'?'#9ccf6a':'#86d45a',{noBump:false}));g.rotation.x=-Math.PI/2;g.receiveShadow=true;scene.add(g);
 const r=mul(3);
 function tree(x,z,s){const t=new THREE.Group();t.position.set(x,0,z);t.scale.setScalar(s);
   const tr_=outline(sh(new THREE.Mesh(lumpy(new THREE.CylinderGeometry(0.13,0.18,1.3,16),0.01),mat('#9a6237'))),0.03);tr_.position.y=0.65;t.add(tr_);
   const cm=mat(STYLE==='C'?'#5fae4a':'#55b94a');[[0,1.75,0,0.85],[-0.45,1.45,0.1,0.6],[0.5,1.5,-0.05,0.62],[0.05,2.3,0,0.55]].forEach(([a,b,c,rr],i)=>{const m=outline(sh(new THREE.Mesh(lumpy(new THREE.SphereGeometry(rr,32,24),0.03,4,i),cm)),0.035);m.position.set(a,b,c);t.add(m);});scene.add(t);}
 [[-3.4,-6,1.15],[3.8,-7.5,1.3],[-7,-12,1.5],[1.4,-13,1.4],[7.2,-11,1.6],[-2.2,-18,1.8],[5,-20,1.8]].forEach(a=>tree(...a));
 const bm=mat('#4fb045');[[-2.1,-3.2,0.55],[2.6,-3.8,0.6],[-4.5,-4.5,0.7]].forEach(([x,z,rr],i)=>{const m=outline(sh(new THREE.Mesh(lumpy(new THREE.SphereGeometry(rr,32,24),0.03,4,i+5),bm)),0.03);m.position.set(x,rr*0.55,z);m.scale.y=0.8;scene.add(m);});
 const fl=['#ff7aa8','#ffd23f','#ffffff','#b78bff'];for(let i=0;i<40;i++){const a=r()*Math.PI*2,d=2.2+r()*6;const m=new THREE.Mesh(new THREE.SphereGeometry(0.05,10,8),mat(fl[i%4]));m.position.set(Math.cos(a)*d,0.04,-Math.abs(Math.sin(a))*d-1);scene.add(m);}
 const cl=mat('#ffffff',{fog:false});[[-7,9,-34],[6,11,-38],[11,7.5,-32],[-12,12,-40]].forEach(([x,y,z],k)=>{const c=new THREE.Group();c.position.set(x,y,z);[[0,0,0,1.6],[1.5,-0.3,0,1.2],[-1.5,-0.35,0,1.1],[0.6,0.7,0,1.1]].forEach(([a,b,cz,rr])=>{const m=new THREE.Mesh(new THREE.SphereGeometry(rr,24,16),cl);m.position.set(a,b,cz);c.add(m);});c.scale.set(1.3,0.8,0.6);scene.add(c);});}

// =========================================================
// PERSONAJE
// =========================================================
const SKIN=STYLE==='C'?'#f0bf98':'#f6c5a2',SHIRT=STYLE==='C'?'#f26b5b':'#ff6161',PANTS='#3b5ca8',HAIRC='#4a2c1d';
const kid=new THREE.Group();scene.add(kid);
const skinM=(py)=>freezeMat(mat(SKIN,{sheen:true}),py);
// piernas, shorts, polera
{const lm=mat(SKIN,{sheen:true});[-1,1].forEach(s=>{const l=outline(sh(new THREE.Mesh(new THREE.CapsuleGeometry(0.1,0.24,8,16),lm)));l.position.set(s*0.18,0.26,0);kid.add(l);
   const sho=outline(sh(new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.14,32,20)),mat('#ffffff'))));sho.scale.set(1,0.62,1.45);sho.position.set(s*0.18,0.07,0.07);kid.add(sho);
   const sole=new THREE.Mesh(new THREE.SphereGeometry(0.141,32,10,0,Math.PI*2,Math.PI*0.62,Math.PI*0.38),mat('#ff6161'));sole.scale.copy(sho.scale);sole.position.copy(sho.position);kid.add(sole);});
 const spline=(pts)=>new THREE.SplineCurve(pts.map(p=>new THREE.Vector2(...p))).getPoints(60);
 const pants=outline(sh(new THREE.Mesh(lumpy(new THREE.LatheGeometry(spline([[0.001,0.3],[0.36,0.31],[0.455,0.42],[0.47,0.58],[0.45,0.66],[0.001,0.665]]),64),0.006),mat(PANTS))));kid.add(pants);
 const torso=outline(sh(new THREE.Mesh(lumpy(new THREE.LatheGeometry(spline([[0.001,0.6],[0.445,0.62],[0.455,0.78],[0.41,0.94],[0.32,1.07],[0.18,1.16],[0.001,1.19]]),64),0.006),mat(SHIRT))));kid.add(torso);
 const collar=outline(new THREE.Mesh(new THREE.TorusGeometry(0.16,0.035,12,40),mat('#ffffff')),0.01);collar.rotation.x=Math.PI/2;collar.position.y=1.15;kid.add(collar);
 const st=new THREE.Shape();for(let i=0;i<10;i++){const a=Math.PI/2+i*Math.PI/5,r=i%2?0.045:0.1;i?st.lineTo(Math.cos(a)*r,Math.sin(a)*r):st.moveTo(Math.cos(a)*r,Math.sin(a)*r);}
 const star=outline(new THREE.Mesh(new THREE.ExtrudeGeometry(st,{depth:0.02,bevelEnabled:true,bevelThickness:0.01,bevelSize:0.008,bevelSegments:2}),mat('#ffd23f')),0.008);star.position.set(0.14,0.86,0.415);star.rotation.y=0.3;kid.add(star);
 const neck=new THREE.Mesh(new THREE.CylinderGeometry(0.1,0.115,0.22,20),skinM(-0.62));neck.position.y=1.2;kid.add(neck);}
// cabeza
const headG=new THREE.Group();headG.position.y=1.24;kid.add(headG);
const headS=new THREE.Group();headS.position.y=0.56;headS.scale.set(1.06,0.97,1);headG.add(headS);
const headMesh=outline(sh(new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.6,96,64),0.008,5),skinM(0))),0.016);headS.add(headMesh);
const onHead=(x,y,d=0)=>{const z=Math.sqrt(Math.max(0,0.36-x*x-y*y));const n=V3(x,y,z).normalize();return {p:n.clone().multiplyScalar(0.6+d),n};};
[-1,1].forEach(s=>{const e=outline(sh(new THREE.Mesh(new THREE.SphereGeometry(0.14,24,16),skinM(0))),0.012);e.scale.set(0.45,0.95,0.75);e.position.set(s*0.6,0.0,-0.02);headS.add(e);});
{const {p}=onHead(0,-0.07,0.0);const nose=outline(sh(new THREE.Mesh(new THREE.SphereGeometry(0.075,24,16),freezeMat(mat('#f2a688',{sheen:true}),-0.07))),0.01);nose.position.copy(p);nose.scale.set(1.15,0.9,0.85);headS.add(nose);}
const cheeks=[-1,1].map(s=>{const {n}=onHead(s*0.3,-0.2);const m=new THREE.Mesh(new THREE.SphereGeometry(0.2,32,24),freezeMat(mat('#f7b69a',{sheen:true}),-0.2));m.userData.n=n;outline(m,0.012);headS.add(m);return m;});
// cara pintada (boca, mejillas, ojos cerrados, grietas de hielo) en un lienzo sobre la esfera
const FC=document.createElement('canvas');FC.width=FC.height=1024;const fg=FC.getContext('2d');
const faceTex=new THREE.CanvasTexture(FC);faceTex.colorSpace=THREE.SRGBColorSpace;faceTex.anisotropy=8;
const PH0=Math.PI/2-0.85,PHL=1.7,TH0=Math.PI/2-0.85,THL=1.7;
const decal=new THREE.Mesh(new THREE.SphereGeometry(0.6*1.004,96,96,PH0,PHL,TH0,THL),mat('#ffffff',{map:faceTex,transparent:true,noBump:true}));
Object.assign(decal.material,{polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2});decal.renderOrder=2;headS.add(decal);
const toC=(x,y)=>{const R0=0.6,z=Math.sqrt(Math.max(1e-6,R0*R0-x*x-y*y));const th=Math.acos(clamp(y/R0,-1,1)),ph=Math.atan2(z,-x);return [(ph-PH0)/PHL*1024,(th-TH0)/THL*1024];};
// ojos 3D
const eyes=[-1,1].map(s=>{const {p,n}=onHead(s*0.21,0.07,-0.03);const g=new THREE.Group();g.position.copy(p);g.quaternion.setFromUnitVectors(V3(0,0,1),n);headS.add(g);
  const ball=new THREE.Group();ball.scale.set(0.92,1.15,0.62);g.add(ball);
  const white=outline(new THREE.Mesh(new THREE.SphereGeometry(0.16,48,32),mat('#ffffff',{gloss:true,noBump:true})),0.012);ball.add(white);
  const iris=new THREE.Mesh(new THREE.SphereGeometry(0.098,40,24),mat('#6a3f1c',{gloss:true,noBump:true}));iris.scale.z=0.3;iris.position.z=0.142;ball.add(iris);
  const pupil=new THREE.Mesh(new THREE.SphereGeometry(0.058,32,20),mat('#120a06',{gloss:true,noBump:true}));pupil.scale.z=0.3;pupil.position.z=0.152;ball.add(pupil);
  const hm=new THREE.MeshBasicMaterial({color:0xffffff});const h1=new THREE.Mesh(new THREE.SphereGeometry(0.032,16,12),hm);h1.position.set(0.04,0.05,0.168);ball.add(h1);
  const h2=new THREE.Mesh(new THREE.SphereGeometry(0.015,12,8),hm);h2.position.set(-0.035,-0.035,0.168);ball.add(h2);
  const lid=outline(new THREE.Mesh(new THREE.SphereGeometry(0.168,40,20,0,Math.PI*2,0,Math.PI/2),skinM(0.07)),0.008);ball.add(lid);
  const bg=new THREE.Group();const b=onHead(s*0.21,0.27,0.035);bg.position.copy(b.p);bg.quaternion.setFromUnitVectors(V3(0,0,1),b.n);headS.add(bg);
  const brow=outline(new THREE.Mesh(new THREE.CapsuleGeometry(0.03,0.15,6,12),mat(HAIRC)),0.008);brow.rotation.z=Math.PI/2;const bw=new THREE.Group();bw.add(brow);bg.add(bw);
  return {s,g,ball,iris,pupil,h1,h2,lid,bw};});
// pelo
const hairM=mat(HAIRC,{rough:0.55,cc:0.35});
const hairG=new THREE.Group();headS.add(hairG);
{const cap=outline(sh(new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.64,72,36,0,Math.PI*2,0,1.32),0.012,6,3),hairM)),0.016);cap.rotation.x=-0.55;hairG.add(cap);}
const tufts=new THREE.Group();hairG.add(tufts);
{const r=mul(21);[[0,0.62,0.05,0],[0.22,0.58,0.0,-0.5],[-0.22,0.58,0.02,0.5],[0.1,0.56,-0.25,-0.2],[-0.12,0.55,-0.22,0.25],[0.0,0.48,-0.42,0.0]].forEach(([x,y,z,rz],i)=>{
  const t=new THREE.Group();t.position.set(x,y,z);t.rotation.set(-0.25+z*0.6,0,rz);tufts.add(t);
  const m=outline(sh(new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.11,24,16),0.008),hairM)),0.014);m.scale.set(0.85,1.9,0.85);m.position.y=0.12;t.add(m);});
 const sw=outline(sh(new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.16,32,20),0.008),hairM)),0.014);sw.scale.set(2.0,0.75,1.1);sw.position.set(0.16,0.47,0.33);sw.rotation.set(0.5,0.3,-0.35);hairG.add(sw);}
// cristales de hielo pegados a la cabeza
const iceM=mat('#dff6ff',{gloss:true,noBump:true,emissive:'#7fd6ff',ei:0.35});
const NS=12;const stuck=new THREE.InstancedMesh(new THREE.OctahedronGeometry(1,0),iceM,NS);headS.add(stuck);
const stuckD=[...Array(NS)].map((_,i)=>{const r=mul(40+i);const a=-1.2+r()*2.4,b=0.25+r()*0.9;const n=V3(Math.sin(a)*Math.cos(b),Math.sin(b),Math.cos(a)*Math.cos(b)*0.8).normalize();return {n,s:0.05+r()*0.04,d:r()*0.12,r:r()*6};});
// brazos (goma, curvos) y manos
const armSkin=mat(SKIN,{sheen:true}),sleeveM=mat(SHIRT);
function makeArm(side){const a={side};a.tube=outline(sh(new THREE.Mesh(new THREE.BufferGeometry(),armSkin)),0.013);a.sleeve=outline(sh(new THREE.Mesh(new THREE.BufferGeometry(),sleeveM)),0.013);kid.add(a.tube,a.sleeve);
  a.hand=new THREE.Group();kid.add(a.hand);const hm=outline(sh(new THREE.Mesh(new THREE.SphereGeometry(0.108,32,24),armSkin)),0.013);hm.scale.set(1,1.05,0.9);a.hand.add(hm);
  const th=outline(sh(new THREE.Mesh(new THREE.CapsuleGeometry(0.04,0.06,6,12),armSkin)),0.01);th.position.set(-side*0.07,0.05,0.06);th.rotation.z=side*0.8;a.hand.add(th);
  a.S=V3(side*0.34,1.03,0.02);return a;}
const armR=makeArm(1),armL=makeArm(-1);
function setArm(a,Hd,bend=1,up=0){const S=a.S,mid=S.clone().add(Hd).multiplyScalar(0.5);const C=mid.add(V3(a.side*lerp(0.22*bend,0.5,up),lerp(-0.2*bend,0.02,up),lerp(-0.06,0.22,up)));
  const curve=new THREE.QuadraticBezierCurve3(S,C,Hd);const g=new THREE.TubeGeometry(curve,28,0.07,14,false);
  const sc=new THREE.CatmullRomCurve3([0,0.12,0.24,0.34].map(u=>curve.getPoint(u)));const sg=new THREE.TubeGeometry(sc,10,0.1,14,false);
  a.tube.geometry.dispose();a.sleeve.geometry.dispose();a.tube.geometry=g;a.sleeve.geometry=sg;if(a.tube.userData.outline){a.tube.userData.outline.geometry=g;a.sleeve.userData.outline.geometry=sg;}
  a.hand.position.copy(Hd);}
[armR,armL].forEach(a=>{const j=outline(sh(new THREE.Mesh(new THREE.SphereGeometry(0.1,24,16),sleeveM)),0.013);j.position.copy(a.S);kid.add(j);});
// helado
const cone=new THREE.Group();kid.add(cone);
const scoopTop=new THREE.Group(),scoopBot=new THREE.Group();
{const waffle=canvasTex(256,256,(g,w,h)=>{g.fillStyle='#e0a35a';g.fillRect(0,0,w,h);g.strokeStyle='#b27236';g.lineWidth=8;for(let i=-w;i<w*2;i+=36){g.beginPath();g.moveTo(i,0);g.lineTo(i+h,h);g.stroke();g.beginPath();g.moveTo(i,h);g.lineTo(i+h,0);g.stroke();}});
 waffle.wrapS=waffle.wrapT=THREE.RepeatWrapping;waffle.repeat.set(3,1.5);
 const wm=mat('#ffffff',{map:waffle});wm.side=THREE.DoubleSide;
 const c=outline(sh(new THREE.Mesh(new THREE.ConeGeometry(0.15,0.44,40,1,true),wm)),0.012);c.rotation.x=Math.PI;cone.add(c);
 const rim=outline(sh(new THREE.Mesh(new THREE.TorusGeometry(0.15,0.028,12,40),mat('#e8ad62'))),0.01);rim.rotation.x=Math.PI/2;rim.position.y=0.22;cone.add(rim);
 cone.add(scoopBot,scoopTop);scoopBot.position.y=0.31;scoopTop.position.y=0.54;
 const pink=mat('#ff8fb1',{rough:0.6}),mint=mat('#8be3c4',{rough:0.6});
 const s1=outline(sh(new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.185,40,30),0.01,9),pink)),0.013);scoopBot.add(s1);
 for(let i=0;i<7;i++){const a=i*0.9+0.3;const d=outline(sh(new THREE.Mesh(new THREE.SphereGeometry(0.045,16,12),pink)),0.008);d.position.set(Math.cos(a)*0.165,-0.08-(i%3)*0.035,Math.sin(a)*0.165);d.scale.y=1.7;scoopBot.add(d);}
 const s2=outline(sh(new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.165,40,30),0.01,9,2),mint)),0.013);scoopTop.add(s2);
 const r=mul(13),cols=['#ff4d6d','#ffd23f','#4dabf7','#ffffff','#b197fc'];
 const sp=new THREE.InstancedMesh(new THREE.CapsuleGeometry(0.009,0.03,4,6),mat('#ffffff',{noBump:true}),40);const mm=new THREE.Matrix4(),q=new THREE.Quaternion();
 for(let i=0;i<40;i++){const a=r()*Math.PI*2,b=r()*1.2+0.1;const n=V3(Math.cos(a)*Math.cos(b),Math.sin(b),Math.sin(a)*Math.cos(b));q.setFromEuler(new THREE.Euler(r()*6,r()*6,r()*6));mm.compose(n.multiplyScalar(0.165),q,V3(1,1,1));sp.setMatrixAt(i,mm);sp.setColorAt(i,new THREE.Color(cols[i%5]));}
 scoopTop.add(sp);
 const cherry=outline(sh(new THREE.Mesh(new THREE.SphereGeometry(0.055,24,16),mat('#e8193c',{gloss:true}))),0.01);cherry.position.y=0.2;scoopTop.add(cherry);scoopTop.userData.cherry=cherry;
 const stem=new THREE.Mesh(new THREE.CylinderGeometry(0.006,0.006,0.09,6),mat('#5a8a2a'));stem.position.set(0.01,0.27,0);stem.rotation.z=-0.3;scoopTop.add(stem);scoopTop.userData.stem=stem;}
// migas de helado, cristales que saltan, destellos, estrella de impacto
const crumbs=new THREE.InstancedMesh(new THREE.SphereGeometry(1,12,8),mat('#ffffff',{noBump:true}),36);scene.add(crumbs);
{const cc=['#8be3c4','#ff8fb1','#e0a35a'];for(let i=0;i<36;i++)crumbs.setColorAt(i,new THREE.Color(cc[i%3]));}
const crumbD=[...Array(36)].map((_,i)=>{const r=mul(100+i);return {b:Math.floor(i/12),v:V3((r()-0.5)*1.6,0.4+r()*1.2,0.4+r()*0.9),s:0.018+r()*0.022};});
const NC=26;const flying=new THREE.InstancedMesh(new THREE.OctahedronGeometry(1,0),iceM,NC);scene.add(flying);
const flyD=[...Array(NC)].map((_,i)=>{const r=mul(300+i);const a=r()*Math.PI*2,e=0.15+r()*1.2;return {dir:V3(Math.cos(a)*Math.cos(e),Math.sin(e),Math.sin(a)*Math.cos(e)*0.7+0.35).normalize(),sp:1.4+r()*1.8,s:0.035+r()*0.04,rs:r()*8};});
const sparks=[...Array(22)].map((_,i)=>{const r=mul(500+i);const s=new THREE.Sprite(new THREE.SpriteMaterial({map:SOFT,color:0xe6fbff,transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending}));
  const a=r()*Math.PI*2,b=0.1+r()*1.3;s.userData={p:V3(Math.cos(a)*Math.cos(b)*0.9,Math.sin(b)*0.85,Math.sin(a)*Math.cos(b)*0.6+0.2),ph:r()*6,f:3+r()*4,sz:0.07+r()*0.08};headS.add(s);return s;});
const throbGlow=new THREE.Sprite(new THREE.SpriteMaterial({map:SOFT,color:0xbfefff,transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending}));throbGlow.position.set(0,0.4,0.62);throbGlow.scale.set(0.5,0.3,1);headS.add(throbGlow);
const burst=new THREE.Group();scene.add(burst);
{const mk=(ro,ri,c,z)=>{const s=new THREE.Shape();const N=16;for(let i=0;i<N*2;i++){const a=i/(N*2)*Math.PI*2,r=i%2?ri:ro*(0.85+0.15*Math.sin(i*2.7));i?s.lineTo(Math.cos(a)*r,Math.sin(a)*r):s.moveTo(Math.cos(a)*r,Math.sin(a)*r);}
   const m=new THREE.Mesh(new THREE.ShapeGeometry(s),new THREE.MeshBasicMaterial({color:c,fog:false,toneMapped:false}));m.position.z=z;burst.add(m);};
 if(STYLE==='B')mk(1.06,0.68,'#1d1633',-0.02);mk(1.0,0.62,'#ffe14d',0);mk(0.62,0.4,'#fff6c2',0.01);}

// ---------- estado de animación ----------
const BITES=[0.3,0.88,1.43],CH=BITES.map(b=>b+0.2),CUT2=2.89,ZAS=2.93,CUT3=3.47;
function state(t){
  const s={mouth:'smile',mo:0.45,eyes2d:null,lid:-1.35,eyeS:1,pupil:1,lookX:0,lookY:0,browY:0.02,browAng:-0.05,hp:0,hr:0.04*Math.sin(t*2.3),lunge:0,
    hsy:1,bsy:1+0.012*Math.sin(t*5.2),biteB:0,biteIdx:0,cheek:0,frost:0,hairUp:0,shiver:0,throb:0,lhB:0,rhPain:0,top:1,bot:1,cherry:1};
  // tres mordiscos rápidos
  for(let i=0;i<3;i++){const b=BITES[i];if(t>b-0.06&&t<b+0.52){
    if(t<b+0.2){s.mouth='open';s.mo=tr([[b-0.04,0.35],[b+0.13,1,'o'],[b+0.2,0.05,'i']])(t);}else s.mouth='chew';
    s.hp=tr([[b,0],[b+0.13,-0.17,'o'],[b+0.2,0.1,'i'],[b+0.45,0,'o']])(t);s.lunge=tr([[b+0.12,0],[b+0.2,0.08,'i'],[b+0.45,0,'o']])(t);
    s.hsy=tr([[b,1],[b+0.13,1.07,'o'],[b+0.2,0.87,'i'],[b+0.31,1.05,'o'],[b+0.46,1,'io']])(t);
    s.biteB=tr([[b-0.06,0],[b+0.16,1,'io'],[b+0.24,1],[b+0.5,0,'back']])(t);s.biteIdx=i;if(t>b+0.1&&t<b+0.36)s.eyes2d='happy';}}
  s.top=t<CH[0]?1:t<CH[1]?0.72:t<CH[2]?0.42:0.0;s.bot=t<CH[2]?1:0.8;s.cherry=t<CH[0]?1:0;
  const pop=(c)=>t>c&&t<c+0.15?1+0.15*Math.sin((t-c)/0.15*Math.PI):1;s.topPop=pop(CH[0])*pop(CH[1]);s.botPop=pop(CH[2]);
  s.cheek=tr([[CH[0],0],[CH[0]+0.08,0.9,'back'],[BITES[1]+0.1,0.45],[CH[1],0.55],[CH[1]+0.08,1,'back'],[BITES[2]+0.1,0.55],[CH[2],0.65],[CH[2]+0.08,1.05,'back'],[2.55,0.85],[2.85,0.2,'io'],[2.93,0]])(t);
  if(t>=1.95&&t<2.6){s.mouth='chew';s.eyes2d='happy';s.hr=0.09*Math.sin(t*12);s.hsy=1+0.035*Math.sin(t*22);}
  if(t>=CH[0]&&t<2.75)s.cheek+=0.08*Math.sin(t*25);
  if(t>=2.6&&t<CUT2){s.lid=tr([[2.6,-0.15],[2.82,-1.45,'io']])(t);s.pupil=tr([[2.6,1],[2.85,0.55,'io']])(t);s.browY=0.06;s.browAng=0.28;s.mouth=t<2.74?'chew':'o';s.mo=0.2;s.bsy=tr([[2.76,1],[2.9,0.93,'io']])(t);s.hr=0;}
  // ¡ZAS!
  if(t>=CUT2&&t<CUT3){s.bsy=tr([[2.89,0.93],[ZAS,0.9],[2.99,1.17,'o'],[3.42,1,'el']])(t);s.eyeS=tr([[ZAS,1],[3.02,1.48,'back']])(t);s.pupil=0.42;s.lid=-1.55;
    s.mouth=t<ZAS?'o':'grimace';s.mo=tr([[ZAS,0.3],[3.0,1,'back']])(t);s.hairUp=tr([[ZAS,0],[3.03,1,'back']])(t);s.browY=tr([[ZAS,0.06],[3.0,0.12,'back']])(t);s.browAng=0;
    s.frost=ss(ZAS,3.1,t);s.shiver=t>3.0?0.5:0;s.hr=0;s.hp=-0.04;}
  // me duele la frente
  if(t>=CUT3){s.lhB=tr([[CUT3,0],[3.62,1,'back']])(t);s.rhPain=tr([[CUT3,0],[3.65,1,'o']])(t);s.eyes2d=t>3.52?'shut':null;s.eyeS=1.3;s.pupil=0.42;s.lid=-1.55;
    s.browY=0.0;s.browAng=0.38;s.mouth='grimace';s.mo=0.85;s.hairUp=tr([[CUT3,1],[4.1,0.35,'io']])(t);s.frost=1-0.7*ss(3.75,4.45,t);s.shiver=0.55;s.hp=0.07;s.hr=0.1*Math.sin(t*6.5);
    const ph=Math.max(0,t-3.66);s.throb=t>3.66?Math.pow(0.5+0.5*Math.sin(ph*2*Math.PI*3.1-Math.PI/2),2)*(1+0.6*ss(4.15,4.3,t)):0;s.bsy=1+0.012*Math.sin(t*5.2);}
  return s;}
function freezeAt(t){FZ.amt.value=t>=ZAS?1:0;FZ.lvl.value=tr([[ZAS,0],[3.13,1.2,'o']])(t);FZ.lo.value=tr([[3.75,-0.3],[4.45,0.64,'io']])(t);}

// ---------- cara 2D ----------
const crackR=mul(77);const cracks=[];
for(let k=0;k<9;k++){const sx=(crackR()-0.5)*0.5,sy=-0.3+crackR()*0.1;let x=sx,y=sy,a=-Math.PI/2+(crackR()-0.5)*1.4;const pts=[[x,y]];for(let j=0;j<9;j++){a+=(crackR()-0.5)*0.9;x+=Math.cos(a)*0.06;y+=-Math.abs(Math.sin(a))*0.065;pts.push([x,y]);}cracks.push(pts);}
const specks=[...Array(70)].map(()=>[(crackR()-0.5)*0.8,-0.35+crackR()*0.75,1+crackR()*4]);
function drawFace(s,t){const g=fg;g.clearRect(0,0,1024,1024);g.lineCap='round';g.lineJoin='round';const ink='#3d1218';
  for(const sd of[-1,1]){const[x,y]=toC(sd*0.34,-0.13);const gr=g.createRadialGradient(x,y,0,x,y,90);const a=0.5*(1-0.8*FZ.amt.value*(1-FZ.lo.value>0.5?1:0));gr.addColorStop(0,`rgba(255,105,125,${a})`);gr.addColorStop(1,'rgba(255,105,125,0)');g.fillStyle=gr;g.beginPath();g.ellipse(x,y,100,72,0,0,7);g.fill();}
  if(s.eyes2d){g.strokeStyle=ink;g.lineWidth=20;for(const sd of[-1,1]){const[x,y]=toC(sd*0.21,0.07);g.beginPath();
    if(s.eyes2d==='happy'){g.moveTo(x-58,y+18);g.quadraticCurveTo(x,y-58,x+58,y+18);}
    else{const k=sd<0?1:-1;g.moveTo(x-k*48,y-40);g.lineTo(x+k*40,y);g.lineTo(x-k*48,y+40);}g.stroke();}}
  const[mx,my]=toC(0,-0.26);g.strokeStyle=ink;
  const tongueTeeth=(clipPath,topY,botY,w)=>{g.save();clipPath();g.clip();g.fillStyle='#ff6f88';g.beginPath();g.ellipse(mx,botY,w*0.6,(botY-topY)*0.45,0,0,7);g.fill();g.fillStyle='#ffffff';g.fillRect(mx-w,topY-40,w*2,40+Math.min(30,(botY-topY)*0.18));g.restore();};
  if(s.mouth==='smile'){const w=92,d=50+100*s.mo,top=my-20;const P=()=>{g.beginPath();g.moveTo(mx-w,top);g.quadraticCurveTo(mx,top-14,mx+w,top);g.quadraticCurveTo(mx,top+d*1.55,mx-w,top);g.closePath();};
    P();g.fillStyle='#5c1622';g.fill();tongueTeeth(P,top,top+d*0.78,w);P();g.lineWidth=11;g.stroke();}
  else if(s.mouth==='open'){const rx=62+34*s.mo,ry=26+96*s.mo;const P=()=>{g.beginPath();g.ellipse(mx,my+8,rx,ry,0,0,7);};P();g.fillStyle='#5c1622';g.fill();tongueTeeth(P,my+8-ry,my+8+ry*0.8,rx);P();g.lineWidth=11;g.stroke();}
  else if(s.mouth==='chew'){g.lineWidth=15;g.beginPath();for(let k=0;k<=10;k++){const x=mx-58+k*11.6,y=my+5+8*Math.sin(k*1.2+t*24);k?g.lineTo(x,y):g.moveTo(x,y);}g.stroke();}
  else if(s.mouth==='o'){g.beginPath();g.ellipse(mx,my+10,24+10*s.mo,30+14*s.mo,0,0,7);g.fillStyle='#5c1622';g.fill();g.lineWidth=10;g.stroke();}
  else if(s.mouth==='grimace'){const w=118*Math.max(0.3,s.mo),h=86*Math.max(0.3,s.mo),x0=mx-w,y0=my-h/2+6;
    g.beginPath();g.roundRect(x0,y0,w*2,h,30);g.fillStyle='#ffffff';g.fill();g.save();g.clip();g.strokeStyle='#9fb6c4';g.lineWidth=6;
    const ch=4*Math.sin(t*95);g.beginPath();g.moveTo(x0,my+6+ch);for(let k=1;k<=12;k++)g.lineTo(x0+k*w/6,my+6+ch+(k%2?5:-5));g.stroke();
    for(let k=1;k<6;k++){g.beginPath();g.moveTo(x0+k*w/3,y0);g.lineTo(x0+k*w/3,y0+h);g.stroke();}g.restore();
    g.beginPath();g.roundRect(x0,y0,w*2,h,30);g.strokeStyle=ink;g.lineWidth=11;g.stroke();}
  if(s.frost>0.01){const f=s.frost;g.globalAlpha=Math.min(1,f*1.2);
    for(const c of cracks){const n=Math.max(1,Math.floor(c.length*f));g.beginPath();c.slice(0,n+1).forEach(([x,y],i)=>{const[px,py]=toC(x,y);i?g.lineTo(px,py):g.moveTo(px,py);});
      g.strokeStyle='rgba(255,255,255,0.95)';g.lineWidth=7;g.stroke();g.strokeStyle='rgba(120,200,255,0.9)';g.lineWidth=2.5;g.stroke();}
    g.fillStyle='rgba(255,255,255,0.85)';for(const[x,y,r]of specks){if((y+0.35)/0.75>f)continue;const[px,py]=toC(x,y);g.beginPath();g.arc(px,py,r,0,7);g.fill();}g.globalAlpha=1;}
  faceTex.needsUpdate=true;}

// ---------- cámara ----------
const cam=new THREE.PerspectiveCamera(38,W/H,0.05,200);
function camAt(t){let p,l,fov=38,roll=0;
  if(t<CUT2){const u=E.io(t/CUT2);p=V3(lerp(1.0,0.55,u),lerp(1.62,1.68,u),lerp(5.9,5.15,u));l=V3(0,lerp(1.6,1.66,u),0);}
  else if(t<CUT3){const u=(t-CUT2)/(CUT3-CUT2);p=V3(lerp(0.12,0.05,u),1.85,lerp(5.3,5.0,u));l=V3(0,1.5,0);fov=tr([[ZAS,38],[3.0,33.5,'o'],[CUT3,32.5,'lin']])(t);
    const a=t>ZAS?0.05*Math.exp(-(t-ZAS)*7):0;p.x+=a*Math.sin(t*97);p.y+=a*Math.cos(t*83);roll=a*0.6*Math.sin(t*71);}
  else{const u=E.io((t-CUT3)/(DUR-CUT3));p=V3(lerp(-0.95,-0.6,u),lerp(1.78,1.85,u),lerp(5.2,4.55,u));l=V3(0,lerp(1.6,1.68,u),0);roll=0.05;}
  cam.fov=fov;cam.updateProjectionMatrix();cam.position.copy(p);cam.up.set(0,1,0);cam.lookAt(l);cam.rotateZ(roll);}

// ---------- overlays ----------
const capEl=document.getElementById('cap'),svg=document.getElementById('svg'),flash=document.getElementById('flash');document.getElementById('label').textContent=LABEL;
const groups=[];{let g=[];WORDS.forEach((w,i)=>{g.push(i);if(/[.,:!?…]$/.test(w.w)||g.length===3){groups.push(g);g=[];}});if(g.length)groups.push(g);}
const clean=w=>w.replace(/\.\.\.|…/g,'').replace(/[¡!¿?.,:;]/g,'');
function captions(t){const gi=groups.findIndex(g=>t>=WORDS[g[0]].s-0.05&&t<=WORDS[g[g.length-1]].e+0.18);if(gi<0){capEl.innerHTML='';return;}
  capEl.innerHTML=groups[gi].map(i=>{const w=WORDS[i];const on=t>=w.s-0.05&&t<w.e+0.03;const k=on?1+0.12*Math.max(0,1-(t-w.s)/0.12):1;return `<span class="${on?'on':''}" style="transform:scale(${k.toFixed(3)})">${clean(w.w)}</span>`;}).join('');}
const proj=v=>{const p=v.clone().project(cam);return[(p.x+1)/2*W,(1-p.y)/2*H];};
function painMarks(s,t){if(s.throb<=0.001&&t<3.66){svg.innerHTML='';return;}
  const c=proj(headS.localToWorld(V3(0,0.1,0))),top=proj(headS.localToWorld(V3(0,0.62,0)));const R=Math.hypot(top[0]-c[0],top[1]-c[1]);
  const k=0.85+0.35*s.throb,op=clamp((t-3.66)/0.1);let out='';
  [-62,-28,28,62].forEach((deg,i)=>{const a=(deg-90)*Math.PI/180;const r0=R*1.08,r1=R*(1.08+0.32*k);const nx=Math.cos(a),ny=Math.sin(a),px=-ny,py=nx;let d='';
    for(let j=0;j<=4;j++){const r=lerp(r0,r1,j/4),o=(j%2?1:-1)*14*k;d+=(j?'L':'M')+(c[0]+nx*r+px*o).toFixed(1)+' '+(c[1]+ny*r+py*o).toFixed(1);}
    out+=`<path d="${d}" fill="none" stroke="#24101a" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/><path d="${d}" fill="none" stroke="${i%2?'#ff3b5c':'#ff6b3b'}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>`;});
  svg.innerHTML=`<g opacity="${op}">${out}</g>`;}

// ---------- render ----------
const mm=new THREE.Matrix4(),qq=new THREE.Quaternion(),vs=new THREE.Vector3(),eu=new THREE.Euler(),tmp=new THREE.Vector3();
const toKid=v=>{kid.updateMatrixWorld(true);return kid.worldToLocal(v);};
window.renderAt=function(tReal){
  const t=STYLE==='C'?Math.floor(tReal*12+1e-6)/12:tReal;
  const s=state(t);freezeAt(t);camAt(t);
  // cuerpo
  kid.rotation.y=Math.atan2(cam.position.x,cam.position.z)*0.55;
  const bs=s.bsy;kid.scale.set(1/Math.sqrt(bs),bs,1/Math.sqrt(bs));
  kid.position.set(s.shiver*0.012*Math.sin(t*2*Math.PI*21),0,0);
  if(STYLE==='C'){const r=mul(Math.floor(t*12)+1);kid.position.x+=(r()-0.5)*0.006;kid.position.y+=(r()-0.5)*0.004;}
  // cabeza
  headG.rotation.set(s.hp,0,s.hr+s.shiver*0.02*Math.sin(t*2*Math.PI*17));headG.position.set(0,1.24,s.lunge);
  const hs=s.hsy*(1+0.035*s.throb);headG.scale.set(1/Math.sqrt(hs)*(1+0.02*s.throb),hs,1/Math.sqrt(hs));
  eyes.forEach(e=>{e.g.visible=!s.eyes2d;e.ball.scale.set(0.92*s.eyeS,1.15*s.eyeS,0.62*s.eyeS);e.lid.rotation.x=s.lid;
    const ps=s.pupil;e.iris.scale.set(0.75+0.25*ps,0.75+0.25*ps,0.3);e.pupil.scale.set(ps,ps,0.3);e.iris.position.x=e.pupil.position.x=s.lookX*0.03;
    e.bw.position.y=s.browY;e.bw.rotation.z=-e.s*s.browAng;});
  cheeks.forEach(c=>{const p=clamp(s.cheek,0,1.2);c.position.copy(c.userData.n).multiplyScalar(0.38+0.1*p);c.scale.setScalar(0.85+0.22*p);});
  tufts.scale.set(1,1+0.3*s.hairUp,1);tufts.position.y=0.04*s.hairUp;tufts.children.forEach((c,i)=>{c.rotation.x=-0.25+(c.position.z)*0.6-0.25*s.hairUp*Math.sign(c.position.z+0.01);});
  stuckD.forEach((d,i)=>{const k=clamp((t-ZAS-d.d)/0.12);const grow=E.back(k)*(1-ss(3.9,4.4,t));const sc=d.s*grow;const p=d.n.clone().multiplyScalar(0.62);qq.setFromUnitVectors(V3(0,1,0),d.n);vs.set(sc*0.55,sc*1.4,sc*0.55);mm.compose(p,qq,vs);stuck.setMatrixAt(i,mm);});stuck.instanceMatrix.needsUpdate=true;
  sparks.forEach(sp=>{const u=sp.userData;const on=t>ZAS?(1-ss(4.0,4.6,t)):0;sp.material.opacity=on*Math.max(0,Math.sin(t*u.f+u.ph));sp.position.copy(u.p);sp.scale.setScalar(u.sz*(0.6+0.4*Math.sin(t*u.f*0.7+u.ph)));});
  throbGlow.material.opacity=0.65*s.throb;throbGlow.scale.set(0.55+0.2*s.throb,0.32+0.1*s.throb,1);
  kid.updateMatrixWorld(true);
  // brazos y helado
  const mouthK=toKid(headS.localToWorld(V3(0,-0.25,0.62)));
  const tilt=lerp(-0.12,-0.62,s.biteB);const topY=s.biteIdx<2?0.59:0.36;
  const off=V3(0,topY,0).applyAxisAngle(V3(1,0,0),tilt);const want=mouthK.clone().add(V3(0,0.01,s.biteIdx<2?0.12:0.16));const biteHand=want.sub(off);
  let rh=V3(0.46,1.16+0.02*Math.sin(t*5.2),0.42);rh.lerp(V3(0.62,0.92,0.38),s.rhPain);rh.lerp(biteHand,s.biteB);
  if(s.rhPain>0){rh.x+=0.012*Math.sin(t*2*Math.PI*19);rh.y+=0.01*Math.cos(t*2*Math.PI*23);}
  setArm(armR,rh,1-0.5*s.biteB);
  const foreK=toKid(headS.localToWorld(onHead(-0.25,0.27,0.1).p));let lh=V3(-0.52,0.64+0.015*Math.sin(t*5.2+1),0.14);lh.lerp(foreK,s.lhB);setArm(armL,lh,1,clamp(s.lhB));
  cone.position.copy(rh).add(V3(0,0.05,0.0));cone.rotation.set(tilt,0,-0.08+(s.rhPain?0.25*s.rhPain:0));
  scoopTop.scale.setScalar(Math.max(0.0001,s.top*s.topPop));scoopTop.visible=s.top>0.01;scoopBot.scale.setScalar(s.bot*s.botPop);scoopTop.userData.cherry.visible=scoopTop.userData.stem.visible=s.cherry>0;
  // migas
  crumbD.forEach((d,i)=>{const dt=t-CH[d.b];let sc=0;if(dt>0&&dt<0.7){sc=d.s*(1-ss(0.45,0.7,dt));}
    const p0=toKid(headS.localToWorld(V3(0,-0.28,0.7)));kid.localToWorld(p0);tmp.copy(d.v).applyAxisAngle(V3(0,1,0),kid.rotation.y);
    const p=p0.add(tmp.multiplyScalar(Math.max(0,dt))).add(V3(0,-4.5*dt*dt,0));qq.identity();vs.setScalar(Math.max(1e-4,sc));mm.compose(p,qq,vs);crumbs.setMatrixAt(i,mm);});crumbs.instanceMatrix.needsUpdate=true;
  // cristales que vuelan
  const hc=headS.localToWorld(V3(0,0.1,0));
  flyD.forEach((d,i)=>{const dt=t-ZAS-0.02;let sc=0;const p=hc.clone();if(dt>0&&dt<1.6){sc=d.s*E.back(clamp(dt/0.08))*(1-ss(1.0,1.6,dt));p.add(d.dir.clone().multiplyScalar(0.5+d.sp*dt*Math.exp(-dt*1.2)*1.3)).add(V3(0,-1.8*dt*dt,0));}
    eu.set(d.rs+t*4,d.rs*2+t*3,0);qq.setFromEuler(eu);vs.set(sc*0.6,sc*1.3,sc*0.6);mm.compose(p,qq,vs);flying.setMatrixAt(i,mm);});flying.instanceMatrix.needsUpdate=true;
  // estrella de impacto detrás de la cabeza
  burst.visible=t>=ZAS&&t<CUT3;if(burst.visible){const k=tr([[ZAS,0.01],[3.0,1.25,'back'],[CUT3,1.4,'lin']])(t);burst.position.copy(headS.localToWorld(V3(0,0.05,-0.9)));burst.lookAt(cam.position);burst.rotateZ(t*0.6);burst.scale.setScalar(k*1.25);}
  drawFace(s,t);
  renderer.render(scene,cam);
  captions(tReal);painMarks(s,t);
  flash.style.opacity=(tReal>=ZAS&&tReal<ZAS+0.1)?0.8*(1-(tReal-ZAS)/0.1):0;
  return true;};
await document.fonts.ready;window.renderAt(0);window.READY=true;
