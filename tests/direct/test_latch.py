import hashlib
import json
import re
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
RULES=json.loads((ROOT/'config/resources.json').read_text())
DECISIONS={'combined':['USED','USED','UNUSED'],'database':['USED','UNUSED','UNUSED'],'identity':['UNUSED','UNUSED','USED'],'read-only':['UNUSED']*3,'ambiguous':['UNUSED','UNCERTAIN','UNUSED']}
DOCS={name:(ROOT/'fixtures'/f'{name}.md').read_text() for name in DECISIONS}

def source(name):
    return f"https://raw.githubusercontent.com/example/scope-latch/{'a'*40}/fixtures/{name}.md", hashlib.sha256(DOCS[name].encode()).hexdigest()

def answer(name,decisions=None):
    return {'resources':[{'id':row['id'],'decision':decision,'quote':DOCS[name].strip() if decision!='UNUSED' else ''} for row,decision in zip(RULES,decisions or DECISIONS[name])]}

def mock(vm,name,independent=None,anchors=None,changed=None,report=None):
    vm.clear_mocks()
    vm.mock_web(re.escape(source(name)[0]),{'status':200,'body':changed if changed is not None else DOCS[name]})
    vm.mock_llm(r'.*SCOPELATCH-LEADER.*',json.dumps(report or answer(name)))
    vm.mock_llm(r'.*SCOPELATCH-VALIDATOR.*',json.dumps(answer(name,independent)))
    vm.mock_llm(r'.*SCOPELATCH-ANCHORS.*',json.dumps({'valid':anchors if anchors is not None else [True]*3}))

@pytest.fixture
def latch(direct_deploy,direct_vm,direct_alice,direct_bob):
    contract=direct_deploy(str(ROOT/'contracts/scope_latch.py'),json.dumps(RULES),json.dumps(['0x'+direct_alice.hex(),'0x'+direct_bob.hex()]))
    direct_vm.sender=direct_alice
    return contract

def request(latch,vm,name):
    mock(vm,name)
    latch.request(*source(name))

def statuses(latch):
    return [row['status'] for row in latch.get_state()['requests']]

def test_atomic_footprints_and_fifo(latch,direct_vm):
    for name in ['combined','database','identity']: request(latch,direct_vm,name)
    assert statuses(latch)==['ACTIVE','WAITING','WAITING']
    assert latch.get_state()['locks']==[0,0,-1]

def test_release_grants_compatible_waiters(latch,direct_vm):
    for name in ['combined','database','identity']: request(latch,direct_vm,name)
    latch.release(0)
    assert statuses(latch)==['RELEASED','ACTIVE','ACTIVE']
    assert latch.get_state()['locks']==[1,-1,2]

def test_cancel_barrier_grants_unrelated_waiter(latch,direct_vm):
    for name in ['combined','database','identity']: request(latch,direct_vm,name)
    latch.cancel(1)
    assert statuses(latch)==['ACTIVE','CANCELLED','ACTIVE']
    assert latch.get_state()['locks']==[0,0,2]

def test_only_creator_can_release_or_cancel(latch,direct_vm,direct_bob):
    request(latch,direct_vm,'combined'); request(latch,direct_vm,'database')
    direct_vm.sender=direct_bob
    with direct_vm.expect_revert('Only request creator'): latch.release(0)
    with direct_vm.expect_revert('Only request creator'): latch.cancel(1)
    assert latch.get_state()['locks']==[0,0,-1]

def test_unadmitted_client(latch,direct_vm,direct_charlie):
    direct_vm.sender=direct_charlie
    with direct_vm.expect_revert('Client not admitted'): latch.request(*source('combined'))
    assert latch.get_state()['requests']==[]

def test_review_and_read_only_do_not_occupy_or_block(latch,direct_vm):
    request(latch,direct_vm,'ambiguous'); request(latch,direct_vm,'read-only')
    assert statuses(latch)==['REVIEW','NO_LOCKS']
    assert latch.get_state()['locks']==[-1]*3
    request(latch,direct_vm,'combined')
    assert latch.get_state()['locks']==[2,2,-1]

def test_resource_reuse(latch,direct_vm):
    request(latch,direct_vm,'combined'); latch.release(0)
    request(latch,direct_vm,'combined')
    assert statuses(latch)==['RELEASED','ACTIVE']
    assert latch.get_state()['locks']==[1,1,-1]

def test_wrong_status_operations(latch,direct_vm):
    request(latch,direct_vm,'combined'); request(latch,direct_vm,'database')
    with direct_vm.expect_revert('Wrong request status'): latch.cancel(0)
    with direct_vm.expect_revert('Wrong request status'): latch.release(1)
    latch.release(0)
    with direct_vm.expect_revert('Wrong request status'): latch.release(0)

def test_changed_bytes_roll_back(latch,direct_vm):
    mock(direct_vm,'combined',changed=DOCS['combined']+'changed')
    with direct_vm.expect_revert('hash or size mismatch'): latch.request(*source('combined'))
    assert latch.get_state()['requests']==[]

def test_forged_quote_rolls_back(latch,direct_vm):
    report=answer('combined'); report['resources'][0]['quote']='Fabricated database mutation statement.'
    mock(direct_vm,'combined',report=report)
    with direct_vm.expect_revert('Unsupported source anchor'): latch.request(*source('combined'))
    assert latch.get_state()['locks']==[-1]*3

def test_validator_agreement(latch,direct_vm):
    request(latch,direct_vm,'combined')
    assert direct_vm.run_validator() is True

def test_validator_rejects_omitted_resource(latch,direct_vm):
    request(latch,direct_vm,'combined')
    mock(direct_vm,'combined',independent=['USED','UNUSED','UNUSED'])
    assert direct_vm.run_validator() is False

@pytest.mark.parametrize('decision',['UNUSED','UNCERTAIN'])
def test_validator_rejects_false_empty_or_uncertain(latch,direct_vm,decision):
    mock(direct_vm,'combined',report=answer('combined',[decision]*3))
    latch.request(*source('combined'))
    assert direct_vm.run_validator() is False

def test_validator_anchor_relevance(latch,direct_vm):
    request(latch,direct_vm,'combined')
    mock(direct_vm,'combined',anchors=[True,False,True])
    assert direct_vm.run_validator() is False

def test_validator_refetches_plan(latch,direct_vm):
    request(latch,direct_vm,'combined')
    mock(direct_vm,'combined',changed=DOCS['combined']+'changed')
    assert direct_vm.run_validator() is False

@pytest.mark.parametrize('url',['https://example.com/plan.md',f"https://raw.githubusercontent.com/example/scope-latch/{'a'*40}/../main/plan.md"])
def test_source_locator(latch,direct_vm,url):
    with direct_vm.expect_revert('commit-pinned'): latch.request(url,'a'*64)
