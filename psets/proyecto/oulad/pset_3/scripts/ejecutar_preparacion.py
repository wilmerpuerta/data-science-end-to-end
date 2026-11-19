"""Compatibilidad de entrega: kernel pset3-entrega, conserva cierre ya verificado."""
from ejecutar_notebooks_entrega import main
if __name__=='__main__':main(names=['01_eda.ipynb', '02_features.ipynb'],reuse_verified=True)
