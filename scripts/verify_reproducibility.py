"""Reproduce in a temporary checkout using the invoking (ideally clean) environment.

Use the separately installed audit environment to verify dependency isolation.
Original datasets and headline artifacts are read only. No publishing is performed.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import shutil
import subprocess
import tempfile
import socket
import time
import xml.etree.ElementTree as ET
from urllib.request import urlopen
import pandas as pd
from src.utilities import ROOT,save_json,sha256
from scripts.publication_files import publication_file


def main():
    headline=['results/model_comparison.csv','results/forecast_metrics.csv','results/decision_metrics.csv']
    expected={p:pd.read_csv(ROOT/p) for p in headline}
    hashes={p:sha256(ROOT/p) for p in headline}
    report={'python':sys.version.split()[0],'commands':[],'headline_comparison':{},'source_modified':False}
    with tempfile.TemporaryDirectory(prefix='smartsell_reproduce_') as temp:
        checkout=Path(temp)/'project'
        checkout.mkdir()
        for source in ROOT.rglob('*'):
            relative=source.relative_to(ROOT)
            if source.is_file() and publication_file(relative):
                destination=checkout/relative
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(source,destination)
        for command in [['-m','pip','check'],['scripts/prepare_data.py'],['scripts/train_models.py'],
                        ['scripts/evaluate_models.py'],['scripts/build_submission_assets.py'],
                        ['-m','pytest','-q','--junitxml=results/test_results.xml'],['scripts/quality_check.py']]:
            result=subprocess.run([sys.executable,*command],cwd=checkout,capture_output=True,text=True)
            report['commands'].append({'command':'python '+' '.join(command),'returncode':result.returncode})
            print('python '+' '.join(command),result.returncode,flush=True)
            if result.returncode:
                report['failure_output']=(result.stdout+result.stderr)[-5000:]
                save_json(ROOT/'results/audit/reproducibility.json',report)
                raise SystemExit(result.returncode)
            if 'pytest' in command:
                junit=checkout/'results/test_results.xml'
                tree=ET.parse(junit)
                suites=tree.getroot()
                suites=list(suites) if suites.tag=='testsuites' else [suites]
                report['tests']={key:sum(int(s.get(key,0)) for s in suites) for key in ['tests','failures','errors','skipped']}
                for element in tree.iter(): element.attrib.pop('hostname',None)
                tree.write(junit,encoding='utf-8',xml_declaration=True)
        for p,frame in expected.items():
            actual=pd.read_csv(checkout/p)
            pd.testing.assert_frame_equal(frame,actual,check_exact=False,rtol=1e-12,atol=1e-12)
            report['headline_comparison'][p]={'numeric_values_match':True,'reproduced_sha256':sha256(checkout/p),
                                             'original_sha256':hashes[p],'byte_identical':sha256(checkout/p)==hashes[p]}
        report['fresh_environment_freeze']=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines()
        # Startup runs from the isolated checkout under the fresh dependency environment.
        with socket.socket() as candidate:
            candidate.bind(('127.0.0.1',0))
            port=candidate.getsockname()[1]
        server=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.headless=true',
                                 '--server.address=127.0.0.1',f'--server.port={port}'],cwd=checkout,
                                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        try:
            deadline=time.monotonic()+45
            while True:
                try:
                    with urlopen(f'http://127.0.0.1:{port}/_stcore/health',timeout=2) as response:
                        if response.status==200: break
                except OSError:
                    if server.poll() is not None or time.monotonic()>=deadline:
                        raise RuntimeError('Streamlit failed to start in the clean reproduction environment')
                    time.sleep(.25)
            with urlopen(f'http://127.0.0.1:{port}/',timeout=5) as response:
                report['streamlit_startup']={'health_http_status':200,'page_http_status':response.status,
                                             'scope':'Clean dependency environment and isolated checkout; all four pages exercised by AppTest'}
        finally:
            server.terminate()
            server.wait(timeout=10)
        assert all(sha256(ROOT/p)==value for p,value in hashes.items())
        report['passed']=True
        save_json(ROOT/'results/audit/reproducibility.json',report)
        print('All headline tables reproduced; originals unchanged.',flush=True)


if __name__=='__main__': main()
