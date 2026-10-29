"""Verify explanatory economics while protecting the accepted benchmark exactly."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ast
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from src.utilities import ROOT,save_json,sha256
from src.decision_engine import evaluate_options,waiting_break_even,storage_loss_sensitivity


def main():
    baseline=json.loads((ROOT/'results/enhancement/frozen_baseline.json').read_text())
    comparisons={path:sha256(ROOT/path)==digest for path,digest in baseline['sha256'].items()}
    assert all(comparisons.values()), 'Frozen benchmark/data/code changed; stop for human review.'
    function=next(n for n in ast.parse((ROOT/'src/decision_engine.py').read_text()).body
                  if isinstance(n,ast.FunctionDef) and n.name=='evaluate_options')
    unchanged=hashlib.sha256(ast.dump(function).encode()).hexdigest()==baseline['evaluate_options_ast_sha256']
    assert unchanged,'Validated decision rule changed; stop for human review.'
    options,recommendation=evaluate_options(500,{1:500,2:500,3:500},100,1,100)
    thresholds=waiting_break_even(options)
    expected=[(50000+100*h)/(100*.99**h) for h in [1,2,3]]
    assert all(math.isclose(actual,value,rel_tol=1e-12) for actual,value in zip(thresholds.break_even_price,expected))
    assert recommendation['action']=='SELL NOW' and recommendation['expected_gain_rwf']==0
    sensitivity=storage_loss_sensitivity(500,100,[0.,1.,2.,5.],100)
    assert all(g.break_even_price.is_monotonic_increasing for _,g in sensitivity.groupby('horizon'))
    assert storage_loss_sensitivity(500,100,[100.],100).break_even_price.isna().all()
    suites=ET.parse(ROOT/'results/test_results.xml').getroot()
    suites=list(suites) if suites.tag=='testsuites' else [suites]
    tests={key:sum(int(s.get(key,0)) for s in suites) for key in ['tests','failures','errors','skipped']}
    assert not tests['failures'] and not tests['errors']
    report=dict(frozen_artifact_checks=comparisons,all_frozen_artifacts_unchanged=True,
                validated_decision_function_unchanged=unchanged,tests=tests,
                demo_break_even_prices=thresholds.to_dict('records'),
                historical_demo_action=recommendation['action'],historical_demo_expected_gain_rwf=0,
                interpretation='Equality thresholds, not profitable minimum quotes; price must strictly exceed them. Loss scenarios are user assumptions, not NISR daily measurements.',
                optional_market_comparison='Inspected: three markets per crop on latest 14 October date; omitted because observations are stale, no current market or travel recommendation.',
                historical_results='Persistence; test MAE 41.245223 RWF/kg; 314 examples; 20 complete windows; 8.0321285% coverage; all scenarios SELL NOW; zero simulated gain. Unchanged.',
                publication_status='READY FOR HUMAN-REVIEWED PUBLICATION as a historical prototype',
                push_performed=False,deployment_performed=False,video_created=False,passed=True)
    save_json(ROOT/'results/enhancement/verification.json',report)
    quality_path=ROOT/'results/quality_checks.json'
    quality=json.loads(quality_path.read_text())
    quality['verification']['economic_value_enhancement']={key:report[key] for key in
                ['all_frozen_artifacts_unchanged','validated_decision_function_unchanged','tests','publication_status','push_performed','deployment_performed']}
    save_json(quality_path,quality)
    print(f"PASS: {len(comparisons)} frozen artifacts and decision function unchanged; {tests['tests']} tests passed.")
    print(thresholds.to_string(index=False))


if __name__=='__main__': main()
