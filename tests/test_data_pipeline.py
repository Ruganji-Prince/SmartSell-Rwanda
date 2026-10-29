import pandas as pd
from src.preprocessing import clean_prices
from src.feature_engineering import build_history,make_examples,temporal_split
from src.forecasting import availability
from src.utilities import ROOT


def sample():
    return pd.DataFrame(dict(product=['Tomato']*4,market_id=['Huye | A']*4,
         observed_date=pd.to_datetime(['2026-01-01','2026-01-02','2026-01-12','2026-01-13']),
         price=[100.,110.,120.,125.]))


def test_stale_lags_and_exact_targets():
    h=build_history(sample())
    assert pd.isna(h.iloc[2].lag_1_price)
    assert h.iloc[2].lag_1_age_days==10
    assert h.iloc[2].lag_1_stale==1
    assert pd.isna(h.iloc[2].previous_relative_change)
    assert set(make_examples(h).horizon)=={1}
    assert len(make_examples(h))==2


def test_features_do_not_see_future():
    a=build_history(sample())
    b=sample(); b.loc[3,'price']=999999
    b=build_history(b)
    pd.testing.assert_frame_equal(a.iloc[:3],b.iloc[:3])


def test_missing_stale_and_unsupported():
    h=build_history(sample()); keys={('Tomato','Huye | A',i) for i in [1,2,3]}
    assert availability(h,'Tomato','unknown','2026-01-13',keys)[1].startswith('Unsupported')
    assert availability(h,'Potato','Huye | A','2026-01-13',keys)[1].startswith('Unsupported')
    assert 'No observation' in availability(h,'Tomato','Huye | A','2025-01-01',keys)[1]
    assert 'days old' in availability(h,'Tomato','Huye | A','2026-02-01',keys)[1]
    assert 'No price observed' in availability(h,'Tomato','Huye | A','2026-01-14',keys)[1]
    assert availability(h,'Tomato','Huye | A','2026-01-13',keys)[1] is None
    assert 'Insufficient' in availability(h,'Tomato','Huye | A','2026-01-13',set())[1]


def test_purge_boundaries():
    f=pd.DataFrame({'observed_date':pd.date_range('2026-01-01',periods=100)})
    f['target_date']=f.observed_date+pd.Timedelta(days=3)
    train,val,test,bounds=temporal_split(f)
    assert train.target_date.max()<val.observed_date.min()
    assert val.target_date.max()<test.observed_date.min()


def test_conflicts_are_quarantined_and_equal_duplicates_collapsed():
    raw=pd.read_csv(ROOT/'data/raw/tangabid_market_prices.csv').head(1)
    equal=pd.concat([raw,raw],ignore_index=True)
    clean,_,conflict,_=clean_prices(equal)
    assert len(clean)==1 and conflict.empty
    different=raw.copy(); different['price']=12345
    clean,_,conflict,_=clean_prices(pd.concat([raw,different],ignore_index=True))
    assert clean.empty and len(conflict)==2


def test_official_context_has_expected_district_coverage_and_provenance():
    f=pd.read_csv(ROOT/'data/processed/nisr/vegetable_district_context.csv')
    assert set(f.crop_group)=={'Vegetables'}
    assert f.district.nunique()==30
    assert len(f)==30*3*3
    assert not f[['district','season','indicator']].duplicated().any()
    assert f.source_cell.str.match(r'^[A-Z]+\d+$').all()
    use=pd.read_csv(ROOT/'data/processed/nisr/production_use.csv')
    assert use.percent.dropna().between(0,100).all()
