from pathlib import Path
import sys,os
ROOT=Path(__file__).resolve().parents[1];os.environ['PSET3_V2_ROOT']=str(ROOT);sys.path.insert(0,str(ROOT))
from src.seleccion import main
if __name__=='__main__':main()
