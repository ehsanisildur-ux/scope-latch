const fs = require('node:fs');
const path = require('node:path');

module.exports = async function deployScopeLatch(client) {
  const resources = JSON.parse(fs.readFileSync(path.join(__dirname,'../config/resources.json'),'utf8'));
  const members = [process.env.SCOPELATCH_DEPLOYER_ADDRESS];
  const code = fs.readFileSync(path.join(__dirname, '../contracts/scope_latch.py'), 'utf8');
  const hash = process.env.SCOPELATCH_RESUME_HASH || await client.deployContract({ code, args: [JSON.stringify(resources), JSON.stringify(members)], leaderOnly: false });
  console.log('Deployment Transaction Hash:', hash);
  const receipt = await client.waitForTransactionReceipt({ hash, retries: 300, interval: 3000, status: 'FINALIZED' });
  const execution = receipt.consensus_data?.leader_receipt?.[0]?.execution_result ?? receipt.txExecutionResultName;
  if ((receipt.status_name || receipt.statusName || receipt.status) !== 'FINALIZED' || !['SUCCESS', 'FINISHED_WITH_RETURN'].includes(execution)) throw Error('Deployment failed: ' + execution);
  const address = receipt.data?.contract_address ?? receipt.txDataDecoded?.contractAddress;
  if (!/^0x[0-9a-f]{40}$/i.test(address || '')) throw Error('Deployment address missing.');
  console.log('Result:', { 'Transaction Hash': hash, 'Contract Address': address });
};
