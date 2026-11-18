"""Pruebas PSet3 con recursos privados: ejecución explícita documentada con unittest."""
import os
collect_ignore = [] if os.environ.get('PSET3_PYTEST') == '1' else ['tests', 'v2/tests']
