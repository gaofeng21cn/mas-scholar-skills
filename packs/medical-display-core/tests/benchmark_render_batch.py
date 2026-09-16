#!/usr/bin/env python3
"""Compare the real single and batch render entrypoints; retain output evidence."""
from __future__ import annotations
import argparse
import copy
import json
import math
import os
import platform
import statistics
import subprocess
import tempfile
import time
import tomllib
from pathlib import Path
from render_registry_gallery_templates import PACK_ROOT, load_cases, prepare_batch_job


def run(command, *, env=None):
    start = time.monotonic()
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    return result, time.monotonic() - start


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--samples', type=int, default=3)
    args = parser.parse_args()
    if args.samples < 1: raise ValueError('samples must be positive')
    root = args.output_dir or Path(tempfile.mkdtemp(prefix='scholar-render-benchmark-'))
    root.mkdir(parents=True, exist_ok=True)
    profile = json.loads((PACK_ROOT/'renderer_dependency_profile.json').read_text())
    profiles = {p['profile_id']: p for p in profile['profiles']}
    base = profiles['r_ggplot2_evidence_subprocess_v1']
    assert {p['name'] for p in base['language_packages']['r']} == {'jsonlite','ggplot2','ggsci','grid'}
    for manifest in (PACK_ROOT/'templates').glob('*/template.toml'):
        descriptor = tomllib.loads(manifest.read_text())
        assert set(descriptor['requirement_profile_ids']) <= profiles.keys()
        if descriptor['renderer_family'] == 'r_ggplot2': assert descriptor['requirement_profile_ids']
    jobs = []
    cases = load_cases()
    for repeat in range(2):
        for tid, case in cases.items():
            job, _ = prepare_batch_job(f'{tid}-{repeat}',tid,copy.deepcopy(case['payload']),root/f'{tid}-{repeat}')
            jobs.append(job)
    batch_path = root/'batch.json'
    batch_path.write_text(json.dumps({'jobs':jobs}))
    env = dict(os.environ, OPL_ENV_EXECUTION_ID='benchmark-execution', OPL_ENV_MANIFEST_REF='benchmark://prepared-environment')
    renderer = ['Rscript','--vanilla',str(PACK_ROOT/'render.R')]
    single_times, batch_times = [], []
    for sample in range(args.samples):
        total = 0
        for job in jobs:
            result, elapsed = run(renderer+['--request',job['request_path'],'--template',job['template_id'],'--mode',job['render_mode']],env=env)
            assert result.returncode == 0, result.stderr
            total += elapsed
        single_times.append(total)
        before = {}
        for job in jobs:
            request = json.loads(Path(job['request_path']).read_text())
            before[job['case_id']] = (Path(request['output_png_path']).read_bytes(), json.loads(Path(request['layout_sidecar_path']).read_text()))
        result, elapsed = run(renderer+['--batch',str(batch_path)],env=env)
        assert result.returncode == 0, result.stderr
        batch_times.append(elapsed)
        payload = json.loads(result.stdout)
        assert len(payload['results']) == 10 and all(x['ok'] for x in payload['results'])
        for job in jobs:
            request = json.loads(Path(job['request_path']).read_text())
            image, layout = before[job['case_id']]
            assert image == Path(request['output_png_path']).read_bytes()
            assert layout == json.loads(Path(request['layout_sidecar_path']).read_text())
            record = json.loads(Path(job['request_path']+'.execution.json').read_text())
            assert record['execution_id'] == 'benchmark-execution' and record['environment_manifest_ref'] == 'benchmark://prepared-environment'
    # Reject conflicting outputs before any render starts.
    batch_path.write_text(json.dumps({'jobs':[jobs[0], dict(jobs[0],case_id='duplicate-output')]}))
    result, _ = run(renderer+['--batch',str(batch_path)],env=env)
    assert result.returncode != 0 and 'output paths conflict' in result.stderr
    # A failing independent request must not prevent the following good request.
    bad_job, _ = prepare_batch_job('invalid','availability_bar_panel',{'template_id':'availability_bar_panel'},root/'invalid')
    batch_path.write_text(json.dumps({'jobs':[bad_job,jobs[0]]}))
    result, _ = run(renderer+['--batch',str(batch_path)],env=env)
    assert result.returncode == 1
    results = json.loads(result.stdout)['results']
    assert len(results) == 2 and not results[0]['ok'] and results[1]['ok']
    # Interruption leaves already completed per-item results on disk.
    batch_path.write_text(json.dumps({'jobs':jobs}))
    progress_path = Path(str(batch_path)+'.results.json')
    progress_path.unlink(missing_ok=True)
    process = subprocess.Popen(renderer+['--batch',str(batch_path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
    deadline = time.monotonic()+60
    progress = None
    while time.monotonic() < deadline and process.poll() is None:
        if progress_path.exists():
            progress = json.loads(progress_path.read_text())
            if progress['results']: break
        time.sleep(.03)
    process.terminate()
    process.communicate(timeout=10)
    assert progress and progress['results'] and not progress['complete']
    retained = json.loads(progress_path.read_text())
    assert retained['results'][0]['ok']
    summary = {'machine':platform.platform(),'r_version':subprocess.check_output(['Rscript','--version'],text=True,stderr=subprocess.STDOUT).strip(),
      'samples':args.samples,'figures_per_sample':10,'warm_dependencies':True,
      'single_seconds':single_times,'batch_seconds':batch_times,
      'single_p50':statistics.median(single_times),'batch_p50':statistics.median(batch_times),
      'single_p95':sorted(single_times)[math.ceil(.95*len(single_times))-1],
      'batch_p95':sorted(batch_times)[math.ceil(.95*len(batch_times))-1],
      'improvement':1-statistics.median(batch_times)/statistics.median(single_times),
      'exact_png_pixels_and_layout_equal':True,'output_conflict_rejected':True,
      'failure_isolated':True,'cancelled_progress_retained':True,'execution_binding_verified':True}
    (root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(summary,output_root=str(root)),indent=2))
    return 0 if summary['improvement'] >= .20 else 1

if __name__=='__main__': raise SystemExit(main())
