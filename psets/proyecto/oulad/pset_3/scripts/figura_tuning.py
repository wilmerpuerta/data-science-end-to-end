"""Comparación editorial de tuning desde los run_ids de la decisión congelada."""
import json
import math
from pathlib import Path

NAMES = {'lineal': 'Logística', 'boosting': 'HGB', 'bayes': 'GaussianNB'}


def resumen_tuning(root):
    root = Path(root)
    decision = json.loads((root/'docs/negocio/finalistas.json').read_text())['content']
    defaults = json.loads((root/'docs/modelos/resultados.json').read_text())['candidates']
    trials = json.loads((root/'docs/tuning/resultados.json').read_text())['configurations']
    rows = []
    for change in decision['tuning_improvements']:
        default = next(r for r in defaults if r['run_id'] == change['default_run_id'])
        tuned = next(r for r in trials if r['run_id'] == change['tuned_run_id'])
        delta = tuned['cv_coverage_mean'] - default['cv_coverage_mean']
        assert math.isclose(delta, change['delta_coverage'], abs_tol=1e-12)
        rows.append({'family': change['family'], 'label': NAMES[change['family']],
                     'default_mean': default['cv_coverage_mean'], 'default_sd': default['cv_coverage_std'],
                     'tuned_mean': tuned['cv_coverage_mean'], 'tuned_sd': tuned['cv_coverage_std'],
                     'delta_pp': 100*delta, 'default_run_id': default['run_id'],
                     'tuned_run_id': tuned['run_id']})
    assert len(rows) == 3
    return rows


def limites(rows):
    low = min(100*(r[k+'_mean']-r[k+'_sd']) for r in rows for k in ['default', 'tuned'])
    high = max(100*(r[k+'_mean']+r[k+'_sd']) for r in rows for k in ['default', 'tuned'])
    return math.floor(low), math.ceil(high)


def dibujar_canvas(canvas, rows, x, top, width, height=110):
    """Figura vectorial nativa del memo; los segmentos representan DE, no IC."""
    from reportlab.lib import colors
    teal = colors.HexColor('#087e8b')
    gray = colors.HexColor('#718795')
    ink = colors.HexColor('#233645')
    low, high = limites(rows)
    left, right = x+83, x+width-75
    scale = lambda value: left+(right-left)*(value-low)/(high-low)
    canvas.saveState()
    canvas.setFillColor(ink)
    canvas.setFont('MemoBold', 9.8)
    canvas.drawString(x, top-10, 'Cobertura CV (%): media ± DE')
    canvas.setFont('Memo', 8.7)
    for label, color, offset in [('Default', gray, 337), ('Ajustado', teal, 414)]:
        canvas.setFillColor(color)
        canvas.circle(x+offset, top-7, 2.7, fill=1, stroke=0)
        canvas.setFillColor(ink)
        canvas.drawString(x+offset+7, top-10, label)
    canvas.setFont('Memo', 8)
    canvas.drawRightString(x+width-2, top-23, 'Delta pp')
    for i, row in enumerate(rows):
        y = top-34-i*20
        canvas.setFont('Memo', 9.3)
        canvas.setFillColor(ink)
        canvas.drawRightString(left-9, y-3, row['label'])
        for kind, offset, color in [('default', 3.5, gray), ('tuned', -3.5, teal)]:
            mean, sd = 100*row[kind+'_mean'], 100*row[kind+'_sd']
            yy = y+offset
            canvas.setStrokeColor(color)
            canvas.setLineWidth(1)
            canvas.line(scale(mean-sd), yy, scale(mean+sd), yy)
            for bound in [mean-sd, mean+sd]:
                canvas.line(scale(bound), yy-2, scale(bound), yy+2)
            canvas.setFillColor(color)
            canvas.circle(scale(mean), yy, 2.6, fill=1, stroke=0)
        canvas.setFillColor(ink)
        canvas.drawRightString(x+width-2, y-3, f"{row['delta_pp']:+.3f}")
    axis = top-88
    canvas.setStrokeColor(gray)
    canvas.line(left, axis, right, axis)
    canvas.setFont('Memo', 8.5)
    canvas.setFillColor(ink)
    for value in range(low, high+1):
        xx = scale(value)
        canvas.line(xx, axis, xx, axis-3)
        canvas.drawCentredString(xx, axis-14, f'{value} %')
    canvas.restoreState()
    return {'kind': 'native_tuning_default_vs_adjusted', 'height_pt': height,
            'metric': 'CV Fail coverage at fixed 10% capacity',
            'error_type': 'fold standard deviation, not confidence interval',
            'axis_percent': [low, high], 'rows': rows}


def figura_matplotlib(rows):
    """Misma comparación y datos para el notebook y los archivos de figura."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8.4, 2.9))
    for kind, offset, color, label in [('default', .13, '#718795', 'Default'),
                                        ('tuned', -.13, '#087e8b', 'Ajustado')]:
        ax.errorbar([100*r[kind+'_mean'] for r in rows],
                    [2-i+offset for i in range(len(rows))],
                    xerr=[100*r[kind+'_sd'] for r in rows],
                    fmt='o', color=color, capsize=3, markersize=5, label=label)
    low, high = limites(rows)
    ax.set(xlim=(low, high), ylim=(-.45, 2.65), yticks=[2, 1, 0],
           yticklabels=[r['label'] for r in rows], xticks=range(low, high+1),
           xlabel='Cobertura de Fail en CV (%) - mismo cupo del 10 %',
           title='Default frente a ajustado: media ± DE entre cinco folds (no IC)')
    for i, row in enumerate(rows):
        ax.text(1.02, 2-i, f"Delta {row['delta_pp']:+.3f} pp",
                transform=ax.get_yaxis_transform(), va='center', fontsize=9)
    ax.legend(loc='upper right', ncol=2, frameon=False)
    ax.grid(axis='x', alpha=.2)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    return fig
