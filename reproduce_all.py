#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys, time, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from qwcert.experiment import run_benchmark, run_cubic, run_fixed_proposal_ablation, run_bad_proposal, run_exact_cases, write_summaries, stable_hash, environment_info

cfg=json.loads((ROOT/'configs'/'paper_v1.json').read_text())
run_id=stable_hash(cfg)
print({'run_id':run_id,'profile':cfg['profile_name']})
raw=ROOT/'results'/'raw'; raw.mkdir(parents=True,exist_ok=True)
(ROOT/'results'/'tables').mkdir(parents=True,exist_ok=True); (ROOT/'results'/'audits').mkdir(parents=True,exist_ok=True)
start=time.time()
print('[1/5] main benchmark',flush=True); bench=run_benchmark(cfg,raw); print('  rows',len(bench),flush=True)
print('[2/5] cubic study',flush=True); cubic=run_cubic(cfg,raw); print('  rows',len(cubic),flush=True)
print('[3/5] fixed-proposal ablation',flush=True); fixed=run_fixed_proposal_ablation(cfg,raw); print('  rows',len(fixed),flush=True)
print('[4/5] exact bad-proposal stress',flush=True); bad=run_bad_proposal(cfg,raw); print('  rows',len(bad),flush=True)
print('[5/5] selected exact-rational cases',flush=True); exact=run_exact_cases(cfg,raw); print('  rows',len(exact),flush=True)
agg,fam,piv,cubs,audit=write_summaries(raw,bench,cubic,fixed,bad)
import subprocess
subprocess.check_call([sys.executable,str(ROOT/'scripts'/'make_figures.py')])
manifest={"run_id":run_id,"profile":cfg,"environment":environment_info(),"elapsed_seconds":time.time()-start}
(ROOT/'results'/'audits'/'run_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True),encoding='utf-8')
print('\nAggregate summary:\n',agg.to_string(index=False))
print('\nFamily summary:\n',fam.to_string(index=False))
print('\nCubic summary:\n',cubs.to_string(index=False))
print('\nAudit:\n',json.dumps(audit,indent=2,sort_keys=True))
