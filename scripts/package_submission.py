"""Package reviewed source; retain original inputs and exclude private/runtime files."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import zipfile
import csv
from src.utilities import ROOT, save_json, sha256
from scripts.publication_files import publication_file


def main():
    out=ROOT/'dist/SmartSell_Rwanda_submission.zip'
    out.parent.mkdir(exist_ok=True)
    paths=[]
    for p in sorted(ROOT.rglob('*')):
        relative=p.relative_to(ROOT)
        if not p.is_file() or not publication_file(relative): continue
        paths.append(p)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for p in paths: archive.write(p,arcname=p.relative_to(ROOT).as_posix())
    save_json(ROOT/'dist/package_manifest.json',dict(file=out.name,bytes=out.stat().st_size,
               sha256=sha256(out),files=[p.relative_to(ROOT).as_posix() for p in paths],
               excluded='Virtual environment, inspection packages, caches, secrets and student IDs'))
    with (ROOT/'dist/publication_file_inventory.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=['path','bytes','sha256'])
        writer.writeheader()
        writer.writerows(dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha256(p)) for p in paths)
    print(f'Packaged {len(paths)} files, {out.stat().st_size:,} bytes: dist/{out.name}')


if __name__=='__main__': main()
