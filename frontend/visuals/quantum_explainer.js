// Inserted into the scene's script scope by the Streamlit viewer.
const trace = pair.state_trace || {};
const basis = ['00', '01', '10', '11'];
function labelSprite(text, color = '#d9faff') {
  const canvas = document.createElement('canvas'); canvas.width = 512; canvas.height = 96;
  const ctx = canvas.getContext('2d'); ctx.fillStyle = 'rgba(5,12,20,.86)';
  ctx.fillRect(0, 0, 512, 96); ctx.fillStyle = color; ctx.textAlign = 'center';
  ctx.font = '600 38px system-ui'; ctx.fillText(text, 256, 61);
  const texture = new THREE.CanvasTexture(canvas); texture.encoding = THREE.sRGBEncoding;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({map:texture, depthTest:false}));
  sprite.scale.set(2.2, .42, 1); scene.add(sprite); return sprite;
}
const label0 = labelSprite('q0 · Alice', '#70f1ff');
const label1 = labelSprite('q1 · Bob', '#9ebaff');
const measuredLabel=labelSprite(firstReceived?`Bob sample: ${firstReceived}`:'No measured sample','#95ffd5');measuredLabel.position.set(6.1,2,.15);
const eveLabel=labelSprite('EVE · measurement probe','#ff8f9f');eveLabel.position.set(0,2.7,1);eveLabel.visible=attacked;
const tapAssembly=new THREE.Group();scene.add(tapAssembly);tapAssembly.visible=attacked;
const jaws=[-1,1].map(side=>addBox(tapAssembly,[.14,.38,.42],[side*.65,.7,.04],mat(0x586773,.8,.25)));
const tapSleeves=[-1,1].map(side=>{const mesh=addCylinder(tapAssembly,.16,.16,.32,[side*.8,.69,.02],mat(0x9a273c,.6,.3),24);mesh.rotation.z=Math.PI/2;return mesh;});
const scanningArc=new THREE.Mesh(new THREE.TorusGeometry(.52,.025,8,64,Math.PI*1.4),new THREE.MeshBasicMaterial({color:0xff4667,transparent:true,opacity:.8}));scanningArc.position.set(0,.69,.02);scanningArc.rotation.y=Math.PI/2;scene.add(scanningArc);
const attackParticles=[];
for(let i=0;i<12;i++){const particle=new THREE.Mesh(new THREE.SphereGeometry(.045,8,6),new THREE.MeshBasicMaterial({color:0xff617e}));scene.add(particle);attackParticles.push(particle);}
const diagnosticCanvas=document.createElement('canvas');diagnosticCanvas.width=512;diagnosticCanvas.height=256;
const diagnosticTexture=new THREE.CanvasTexture(diagnosticCanvas);diagnosticTexture.encoding=THREE.sRGBEncoding;
const diagnosticScreen=new THREE.Mesh(new THREE.PlaneGeometry(1.4,.7),new THREE.MeshBasicMaterial({map:diagnosticTexture,side:THREE.DoubleSide}));diagnosticScreen.position.set(0,1.8,1.05);scene.add(diagnosticScreen);
let lastDiagnosticFrame=-1;
function animateEve(time,stage,progress){
  const connected=stage===2&&progress>=.4&&progress<.85;
  const measuring=stage===2&&progress>=.5&&progress<.72;
  const approach=stage===2?Math.min(1,progress/.4):stage>2?1:0;
  tapAssembly.visible=scanningArc.visible=diagnosticScreen.visible=attacked;
  jaws.forEach((jaw,i)=>{jaw.position.x=(i===0?-1:1)*(.65-.49*approach);});
  tapSleeves.forEach((sleeve,i)=>{sleeve.position.x=(i===0?-1:1)*(.8-.4*approach);});
  scanningArc.rotation.x=time*.004;scanningArc.scale.setScalar(measuring?1.1+.15*Math.sin(time*.025):.8);
  scanningArc.material.opacity=measuring?.95:connected?.5:.12;
  attackParticles.forEach((particle,i)=>{particle.visible=attacked&&connected;const t=(time*.0008+i/12)%1;particle.position.copy(branchCurve.getPoint(t));particle.scale.setScalar(.8+.6*Math.sin(t*Math.PI));});
  operator.rotation.x=attacked&&stage===2?-.08-.03*Math.sin(time*.006):0;
  if(attacked&&Math.floor(time/90)!==lastDiagnosticFrame){lastDiagnosticFrame=Math.floor(time/90);const ctx=diagnosticCanvas.getContext('2d');ctx.fillStyle='#07101a';ctx.fillRect(0,0,512,256);ctx.strokeStyle=measuring?'#ff5579':'#596e88';ctx.lineWidth=3;ctx.beginPath();for(let x=0;x<512;x++){const y=140+Math.sin(x*.045-time*.008)*(measuring?42:8);x?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();ctx.fillStyle='#ff99ae';ctx.font='22px monospace';ctx.fillText(stage===5&&rejected?'CHANNEL REJECTED':measuring?'Z-BASIS MEASUREMENT':stage===2?'OPTICAL TAP ENGAGING':'PROBE STANDBY',18,35);ctx.fillStyle='#b2c2d8';ctx.font='18px monospace';ctx.fillText('Disturbance monitor · schematic',18,230);diagnosticTexture.needsUpdate=true;}
}
const aliceLabel = labelSprite('ALICE · sender'); aliceLabel.position.set(-7.5,2,-1);
const bobLabel = labelSprite('BOB · receiver'); bobLabel.position.set(7.5,2,-1);
const entanglementGeometry = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]);
const entanglement = new THREE.Line(entanglementGeometry,new THREE.LineDashedMaterial({color:0xdca7ff,dashSize:.24,gapSize:.13,transparent:true,opacity:.85}));
scene.add(entanglement);
const stateArrow = new THREE.ArrowHelper(new THREE.Vector3(0,1,0),new THREE.Vector3(),.72,0xffd783,.15,.08);
scene.add(stateArrow);
const blochFrame = new THREE.Mesh(new THREE.SphereGeometry(.92,20,12),new THREE.MeshBasicMaterial({color:0xffd783,wireframe:true,transparent:true,opacity:.15}));scene.add(blochFrame);
const stateLabel = labelSprite('|0⟩', '#ffde9a');let lastStateLabel=-1;
const stepPicker=document.getElementById('stepPicker');
stepPicker.addEventListener('change',()=>{
  const index=Number(stepPicker.value),stage=index<3?0:index-2;
  const now=performance.now();replayStart=now-(index<3?(index+.15)*stepDuration/3:(stage+.1)*stepDuration);
  pausedAt=now;pinnedStage=stage;previousStage=-1;document.getElementById('playButton').textContent='Resume';
});
const statePanel = document.getElementById('quantumPanel');
const probabilityRows = document.getElementById('probabilityRows');
const coherenceGrid = document.getElementById('coherenceGrid');
document.getElementById('theoryButton').addEventListener('click',event=>{
  statePanel.hidden=!statePanel.hidden;event.currentTarget.setAttribute('aria-expanded',String(!statePanel.hidden));
});
let lastSnapshot = '';
const reducedQuantumMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
// Rings represent coherence, not literal spin. Once entangled, both markers
// share a phase: neither sphere is being depicted as an independent pure state.
function quantumRingState(stage, preparation, progress, elapsed) {
  const channelApplied = stage > 2 || (stage === 2 && progress >= .5);
  const eveMeasured = attacked && channelApplied;
  const joint = (stage === 0 && preparation === 2) || stage === 1 || stage === 2;
  const single = stage === 0 && preparation === 1;
  const freezeAt = (attacked ? 2.5 : 3) * stepDuration;
  const seconds = Math.max(0, (Math.min(elapsed, freezeAt) - stepDuration / 3) / 1000);
  const state = trace[channelApplied ? 'channel' : 'encoded'];
  // Normalize off-diagonal magnitude to the ideal Bell coherence of 0.5.
  let strength = 1;
  if (channelApplied && state?.coherences) {
    strength = Math.min(1, Math.max(0, ...state.coherences.flatMap((row, i) => row.map((v, j) => i === j ? 0 : Number(v) * 2))));
  }
  if (eveMeasured) strength = 0;
  return {single, joint, eveMeasured, channelApplied, strength,
    angle: reducedQuantumMotion.matches ? 0 : seconds * 2.8};
}
function animateQuantumRings(stage, preparation, progress, time) {
  const elapsed = ((currentElapsed(time) % replayDuration) + replayDuration) % replayDuration;
  const motion = quantumRingState(stage, preparation, progress, elapsed);
  const q0Rings = photons[0].rings;
  const q1Rings = [q1Halo, q1RingB, q1RingC];
  [q0Rings, q1Rings].forEach((rings, qubit) => {
    const prepared = motion.single && qubit === 0 || motion.joint || stage >= 3;
    const phase = prepared ? motion.angle : 0;
    rings.forEach((ring, i) => {
      // Set all axes explicitly so pause, replay and backwards seeking are deterministic.
      const base = i === 0 ? [0, 0, 0] : i === 1 ? [Math.PI / 2, 0, 0] : [0, Math.PI / 2, 0];
      ring.rotation.set(base[0] + phase * .24, base[1] + phase * (i === 1 ? -.55 : .4), base[2] + phase * (i % 2 ? -1 : 1));
      ring.material.color.setHex(motion.eveMeasured ? 0xff7089 : motion.joint ? 0xdca7ff : qubit === 0 ? 0x70f1ff : 0x9bc5ff);
      ring.material.opacity = motion.eveMeasured ? .2 : motion.single && qubit === 0 ? .95 : motion.joint ? .35 + .55 * motion.strength : .28;
    });
  });
  return motion;
}
function updateQuantumStory(stage, phase, transmitProgress, time) {
  animateEve(time,stage,transmitProgress);
  const preparation = Math.min(2,Math.floor(phase*3));
  const ringMotion = animateQuantumRings(stage, preparation, transmitProgress, time);
  stepPicker.value=String(stage===0?preparation:stage+2);
  const name = stage===0?['initial','superposition','entangled'][preparation]:stage===1?'encoded':stage===2?(transmitProgress>=.5?'channel':'encoded'):'decoded';
  const snapshot = trace[name];
  const correlated = ringMotion.joint && !ringMotion.eveMeasured &&
    (!ringMotion.channelApplied || Number(CONFIG.noiseProbability || 0) < .5);
  const distribution=stage===0?(preparation<2?0:Math.min(1,(phase-2/3)*3)):1;
  q1Group.position.set(-4.25+11.05*distribution,1.87,.15);
  q1Group.visible=stage<4;photons[0].group.visible=stage<4;
  label0.visible=label1.visible=stage<4;measuredLabel.visible=stage>=4&&!preview;
  const q0=photons[0].group.position, q1=q1Group.position;
  // During preparation q1 is already allocated to Bob; spatial separation is a schematic layout.
  label0.position.copy(q0).add(new THREE.Vector3(-.45,1.05,0));
  label1.position.copy(q1).add(new THREE.Vector3(.45,1.05,0));
  entanglement.visible=correlated;
  entanglement.geometry.attributes.position.setXYZ(0,q0.x,q0.y+.2,q0.z);
  entanglement.geometry.attributes.position.setXYZ(1,q1.x,q1.y+.2,q1.z);
  entanglement.geometry.attributes.position.needsUpdate=true;
  entanglement.computeLineDistances();
  entanglement.material.opacity=.2 + .75 * ringMotion.strength;
  // An entangled qubit's reduced state is mixed; it must not have a pure-state arrow.
  stateArrow.visible=stage===0&&preparation<2;blochFrame.visible=stateArrow.visible;stateLabel.visible=stateArrow.visible;
  stateArrow.position.copy(q0);
  blochFrame.position.copy(q0);stateLabel.position.copy(q0).add(new THREE.Vector3(0,-1.25,0));
  if(stateArrow.visible&&lastStateLabel!==preparation){lastStateLabel=preparation;stateLabel.material.map.dispose();const canvas=document.createElement('canvas');canvas.width=512;canvas.height=96;const ctx=canvas.getContext('2d');ctx.fillStyle='#ffde9a';ctx.font='36px system-ui';ctx.textAlign='center';ctx.fillText(preparation===1?'|+⟩ : 50% 0 / 50% 1':'|0⟩ : 100% 0',256,61);stateLabel.material.map=new THREE.CanvasTexture(canvas);}
  if(stateArrow.visible)stateArrow.setDirection(new THREE.Vector3(preparation===1?1:0,preparation===0?1:0,0));
  const captions = {
    initial:['Prepare','Start with two qubits: q0 and q1.'],
    superposition:['Prepare · superposition','Hadamard puts q0 in superposition, shown by rotating cyan rings.'],
    entangled:['Prepare · entanglement','Coordinated violet rings and the dashed link represent one shared Bell state.'],
    encoded:['Encode',firstBits?`Alice encodes ${firstBits} on q0 using ${operation}.`:'Alice encodes two classical bits on q0.'],
    channel:[attacked?'Transmit · disturbance':'Transmit',attacked?'Eve measures q0: the rings stop and the fibre vibrates to illustrate disturbance.':'q0 reaches Bob. Any fibre vibration represents modeled channel noise.'],
    decoded:['Decode','Bob uses both qubits to recover the two encoded bits.']
  };
  let [title,description]=captions[name];
  if(stage===2&&name==='encoded'){title='Transmit';description='Alice sends q0; Bob already holds q1.';}
  if(stage===4){title='Check disturbance';description=preview?'Run an experiment to load a measured result.':'Independent test probes check whether channel disturbance is within the configured limit.';}
  let outcome='';
  if(stage===5){
    if(preview){title='Preview complete';description='Run an experiment for a measured decision.';}
    else if(rejected){title='Rejected';outcome='rejected';description='Disturbance exceeds the limit. The controller stops the remaining transmission.';}
    else if(CONFIG.backendStatus==='Within limit'){title='Within limit';outcome='within-limit';description='The run completes within the configured disturbance limit.';}
    else if(CONFIG.backendStatus==='Inconclusive'){title='Inconclusive';outcome='inconclusive';description='More test evidence is needed. Candidate output remains withheld.';}
    else{title=CONFIG.backendStatus||'Completed';description='Historical result. Review the saved report for this model’s decision details.';}
  }
  document.getElementById('story').dataset.outcome=outcome;
  if(document.getElementById('storyTitle').textContent!==title)document.getElementById('storyTitle').textContent=title;
  if(document.getElementById('storyDescription').textContent!==description)document.getElementById('storyDescription').textContent=description;
  if(snapshot&&lastSnapshot!==name){
    lastSnapshot=name;
    probabilityRows.replaceChildren();coherenceGrid.replaceChildren();
    basis.forEach((bits,i)=>{
      const row=document.createElement('div');row.className='probability-row';
      const text=document.createElement('span');text.textContent=`|${bits}⟩`;
      const meter=document.createElement('meter');meter.min=0;meter.max=1;meter.value=snapshot.probabilities[i];
      const value=document.createElement('span');value.textContent=`${(snapshot.probabilities[i]*100).toFixed(0)}%`;
      row.append(text,meter,value);probabilityRows.append(row);
      basis.forEach((_,j)=>{const cell=document.createElement('span');const v=snapshot.coherences[i][j];cell.style.background=snapshot.density_real[i][j]<-1e-8?`rgba(255,180,80,${.05+v*.95})`:`rgba(153,123,255,${.05+v*.95})`;cell.textContent=v.toFixed(2);cell.title=`ρ[${bits}, ${basis[j]}] = ${snapshot.density_real[i][j].toFixed(3)} + ${snapshot.density_imag[i][j].toFixed(3)}i`; coherenceGrid.append(cell);});
    });
    document.getElementById('stateNote').textContent=correlated?'Each qubit alone is maximally mixed. The off-diagonal entries show joint coherence.':name==='channel'?(attacked?'Averaged over Eve’s unobserved outcomes: a dephased mixture.':'Ordinary Pauli noise changes the ensemble; an error alone does not identify Eve.'):'These are exact ensemble probabilities before Bob’s final measurement. Basis order: q0q1.';
  }
}
