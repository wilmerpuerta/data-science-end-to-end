import os
collect_ignore = [] if os.environ.get('PSET3_PYTEST') == '1' else ['tests']
