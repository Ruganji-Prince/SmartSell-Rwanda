"""Reviewable local QC: imports, preservation, links, sizes, paths, secret patterns."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import importlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from src.utilities import ROOT, save_json, sha256
from scripts.publication_files import publication_file

REQUIRED = ['README.md','app.py','requirements.txt','requirements-lock.txt','models/metadata.json',
    'results/forecast_metrics.csv','results/model_comparison.csv','results/decision_metrics.csv',
    'docs/PROJECT_SUMMARY.md','docs/METHODOLOGY.md','docs/DATA_SOURCES.md','docs/MODEL_EVALUATION.md',
    'docs/DECISION_EVALUATION.md','docs/ASSUMPTIONS_AND_LIMITATIONS.md','docs/HACKATHON_JUDGING_ALIGNMENT.md',
    'docs/DEMO_SCRIPT.md','docs/SUBMISSION_CHECKLIST.md','FINAL_STATUS.md','REQUIRED_MANUAL_INPUTS.md',
    'data/processed/history.csv','data/processed/nisr/vegetable_district_context.csv',
    'student_cards/README.md','demo/README.md','docs/PUBLICATION_GUIDE.md']
EXCLUDE = {'.venv','.inspection_tools','__pycache__','.pytest_cache','.git','dist'}


def included(path):
    return publication_file(path.relative_to(ROOT))


def verification_failed(verification):
    """A clean file scan cannot override a recorded failing test or startup check."""
    tests=verification.get('automated_tests',{})
    startup=verification.get('streamlit_startup',{})
    return bool(tests.get('failures',0) or tests.get('errors',0) or any(status!=200 for status in startup.values()))


def main():
    missing=[p for p in REQUIRED if not (ROOT/p).exists()]
    errors=[]
    for module in ['data_loading','preprocessing','feature_engineering','forecasting','decision_engine','nisr_context','utilities','localization']:
        try: importlib.import_module('src.'+module)
        except Exception as exc: errors.append(f'{module}: {exc}')
    broken=[]
    active_md=[p for p in ROOT.rglob('*.md') if included(p) and 'legacy_aisd' not in p.parts]
    for path in active_md:
        content=path.read_text(encoding='utf-8-sig')
        for link in re.findall(r'\]\(([^)]+)\)',content):
            link=link.strip('<>').split('#')[0]
            if not link or re.match(r'^[a-zA-Z]+://',link) or link.startswith('mailto:'):
                continue
            if not (path.parent/unquote(link)).exists():
                broken.append(f'{path.relative_to(ROOT)}: {link}')
    files=[p for p in ROOT.rglob('*') if p.is_file() and included(p)]
    oversized=[dict(file=str(p.relative_to(ROOT)),bytes=p.stat().st_size) for p in files if p.stat().st_size>50*1024**2]
    absolute_paths=[]; secret_hits=[]; machine_metadata=[]
    # Heuristic scan, not an assertion that a comprehensive security audit was performed.
    secret_patterns=[r'AKIA[0-9A-Z]{16}',r'gh[pousr]_[A-Za-z0-9]{30,}',r'sk-[A-Za-z0-9]{32,}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
    for path in files:
        if path.suffix not in ['.py','.md','.json','.toml','.txt','.yml','.yaml','.csv','.ipynb','.tex','.xml']:
            continue
        content=path.read_text(encoding='utf-8-sig',errors='replace')
        if re.search(r'[A-Za-z]:[\\/](?:Users|Python|Program Files)[\\/]',content):
            absolute_paths.append(str(path.relative_to(ROOT)))
        if any(re.search(pattern,content) for pattern in secret_patterns):
            secret_hits.append(str(path.relative_to(ROOT)))
        if path.suffix=='.xml' and re.search(r'hostname="[^"]+"',content):
            machine_metadata.append(str(path.relative_to(ROOT)))
    preserved=[]
    with zipfile.ZipFile(ROOT/'sell-time-estimation-aisd-main.zip') as archive:
        for name in archive.namelist():
            if '/data/raw/' in name and name.endswith('.csv'):
                path=ROOT/'data/raw'/Path(name).name
                preserved.append(dict(file=str(path.relative_to(ROOT)),matches_original_archive=path.read_bytes()==archive.read(name)))
    manifest={str(p.relative_to(ROOT)):sha256(p) for p in files if p.name in ['SAS 2024_Annual Tables.xlsx','sell-time-estimation-aisd-main.zip'] or p.parent==ROOT/'data/raw'}
    previous_path=ROOT/'results/quality_checks.json'
    previous=json.loads(previous_path.read_text()) if previous_path.exists() else {}
    verification=previous.get('verification',{})
    report=ROOT/'results/test_results.xml'
    if report.exists():
        suites=ET.parse(report).getroot()
        suites=list(suites) if suites.tag=='testsuites' else [suites]
        verification['automated_tests']={key:sum(int(s.get(key,0)) for s in suites) for key in ['tests','failures','errors','skipped']}
        verification['test_report']='results/test_results.xml'
    if '--check-server' in sys.argv:
        from urllib.request import urlopen
        verification['streamlit_startup']={}
        for route in ['/_stcore/health','/']:
            with urlopen('http://127.0.0.1:8501'+route,timeout=10) as response:
                verification['streamlit_startup'][route]=response.status
        verification['browser_visual_qa']='Not performed; Streamlit AppTest covers page rendering and interactions'
    verification['python_version']=sys.version.split()[0]
    result=dict(missing_required=missing,import_errors=errors,broken_local_markdown_links=broken,
                files_over_50mb=oversized,active_absolute_path_hits=absolute_paths,heuristic_secret_pattern_hits=secret_hits,
                public_machine_metadata_hits=machine_metadata,
                raw_csv_preservation=preserved,input_sha256=manifest,
                public_payload_file_count=len(files),public_payload_bytes=sum(p.stat().st_size for p in files),
                verification=verification,
                external_link_check='Not automatically probed; source and deployment links require final human verification',
                license_note='No new open-source license added')
    result['passed']=not any([missing,errors,broken,oversized,absolute_paths,secret_hits,machine_metadata]) and all(r['matches_original_archive'] for r in preserved) and not verification_failed(verification)
    save_json(previous_path,result)
    print(json.dumps(result,indent=2))
    if not result['passed']: raise SystemExit(1)


if __name__=='__main__':
    main()
