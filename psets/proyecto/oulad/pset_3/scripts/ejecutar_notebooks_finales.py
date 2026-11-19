"""Compatibilidad de entrega: kernel pset3-entrega, conserva cierre ya verificado."""
from ejecutar_notebooks_entrega import main
if __name__=='__main__':main(names=['03_baseline_candidatos.ipynb', '04_tuning.ipynb', '05_seleccion.ipynb', 'anexos/06_anticipacion.ipynb'],reuse_verified=True)
