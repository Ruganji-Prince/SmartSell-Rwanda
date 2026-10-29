"""One explicit publication boundary shared by packaging and inventory checks."""
from pathlib import PurePosixPath

ROOT_FILES={'.gitignore','README.md','app.py','requirements.txt','requirements-lock.txt','pytest.ini',
            'REQUIRED_MANUAL_INPUTS.md','FINAL_STATUS.md','SAS 2024_Annual Tables.xlsx',
            '2026 NISR Hackathon Webinar.pdf','2026 NISR Hackathon Webinar 2.pdf',
            'ddi-documentation-english-113.pdf','sell-time-estimation-aisd-main.zip'}
ROOT_DIRECTORIES={'src','scripts','tests','data','models','results','figures','docs','demo','student_cards','.streamlit'}
PRIVATE_DIRECTORIES={'.venv','venv','.inspection_tools','__pycache__','.pytest_cache','.ipynb_checkpoints',
                     '.git','dist','node_modules','.aws','.ssh','.codex','.agents','.idea','.vscode'}


def publication_file(relative):
    parts=PurePosixPath(relative.as_posix()).parts
    if not parts or any(part in PRIVATE_DIRECTORIES for part in parts): return False
    name=parts[-1]
    if name.startswith('.env') or name in {'secrets.toml','credentials','credentials.json','id_rsa','id_ed25519'}: return False
    if relative.suffix.lower() in {'.log','.pyc','.pyo','.pem','.key','.p12','.pfx','.aux','.out','.toc'}: return False
    if parts[0]=='student_cards': return relative.as_posix()=='student_cards/README.md'
    if len(parts)==1: return name in ROOT_FILES
    return parts[0] in ROOT_DIRECTORIES
