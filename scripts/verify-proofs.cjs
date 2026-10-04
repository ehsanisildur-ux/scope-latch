const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const canonical=value=>JSON.stringify(value,(_,item)=>item && !Array.isArray(item) && typeof item==='object' ? Object.fromEntries(Object.keys(item).sort().map(key=>[key,item[key]])) : item).replace(/[^\x00-\x7f]/g,char=>'\\u'+char.charCodeAt(0).toString(16).padStart(4,'0'));
const read=name=>JSON.parse(fs.readFileSync(path.join(root,'proofs',name+'.json')));
const deployment=read('deployment');
assert.equal(deployment.chain_id,61999);
assert.equal(deployment.source_sha256,digest(fs.readFileSync(path.join(root,'contracts/scope_latch.py'))));
assert.equal(deployment.exact_source_match,true);
for(const tx of deployment.transactions){
 const receipt=read(tx.label+'-receipt');
 assert.equal(receipt.hash,tx.hash);
 assert.equal(receipt.status_name||receipt.statusName,'FINALIZED');
 assert.equal(receipt.result_name,'MAJORITY_AGREE');
 assert(['SUCCESS','FINISHED_WITH_RETURN'].includes(receipt.txExecutionResultName||receipt.consensus_data.leader_receipt[0].execution_result));
 assert(Object.values(receipt.consensus_data.votes).filter(vote=>vote==='agree').length>=3);
 if(tx.action==='deploy') continue;
 const proof=read(tx.label),state=proof.state;
 assert.equal(proof.contract_address,deployment.contract_address);
 assert.equal(proof.source_sha256,deployment.source_sha256);
 assert.equal(receipt.to_address.toLowerCase(),deployment.contract_address.toLowerCase());
 for(const row of state.requests){
   assert.deepEqual(row.footprint,row.report.resources.flatMap((item,index)=>item.decision==='USED'?[index]:[]));
   const initial={...row};delete initial.plan_root;
   initial.status=row.report.resources.some(item=>item.decision==='UNCERTAIN')?'REVIEW':row.footprint.length?'WAITING':'NO_LOCKS';
   assert.equal(row.plan_root,digest(canonical({catalogue:state.catalogue,request:initial})));
   const file=new URL(row.url).pathname.split('/').pop();
   const body=fs.readFileSync(path.join(root,'fixtures',file));
   assert.equal(row.sha256,digest(body));
   for(const item of row.report.resources) if(item.quote) assert(body.toString().includes(item.quote));
   if(row.status==='ACTIVE') for(const resource of row.footprint) assert.equal(state.locks[resource],row.index);
   else assert(!state.locks.includes(row.index));
 }
 for(let resource=0;resource<state.locks.length;resource++){
   const holder=state.locks[resource];
   if(holder!==-1){assert.equal(state.requests[holder].status,'ACTIVE');assert(state.requests[holder].footprint.includes(resource));}
 }
 console.log('VERIFIED',tx.label,JSON.stringify(state.locks));
}
assert.equal(deployment.transactions.length,11);
assert.deepEqual(read('release-identity').state.locks,[-1,-1,-1]);
console.log('Verified 11 finalized receipts, source commitments and every lock invariant.');
