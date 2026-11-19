"""Auditoría descriptiva OULAD. No modifica originales ni entrena modelos."""
from pathlib import Path
import argparse, hashlib, json, datetime
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
KEY = ['code_module','code_presentation','id_student']
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data-dir',type=Path,default=ROOT/'datasets'); args=ap.parse_args()
    data=args.data_dir.resolve(); out=ROOT/'pset-01/docs'; out.mkdir(parents=True,exist_ok=True)
    names=['studentInfo','studentRegistration','courses','vle','studentVle']
    missing=[n+'.csv' for n in names if not (data/(n+'.csv')).exists()]
    if missing: raise SystemExit('Faltan: '+', '.join(missing))
    tables={n:pd.read_csv(data/(n+'.csv')) for n in names[:-1]}
    manifest={'dataset':'OULAD','source':'https://research.stem.open.ac.uk/ouanalyse/dataset/','publication_doi':'https://doi.org/10.1038/sdata.2017.171','published_archive_reference':'https://doi.org/10.6084/m9.figshare.5081998.v1','license':'CC BY 4.0','release':'histórico 2013–2014, publicación 2017; versión de descarga no aportada','audited_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{}}
    for n in names:
        p=data/(n+'.csv'); h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
        manifest['files'][p.name]={'sha256':h.hexdigest(),'bytes':p.stat().st_size,'local_mtime_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),'original_download_date':'no proporcionada'}
    info=tables['studentInfo']; reg=tables['studentRegistration']; courses=tables['courses']; vle=tables['vle']
    checks={}; nulls={}
    for n,t in tables.items():
        k=KEY if n.startswith('student') else ['code_module','code_presentation']+(['id_site'] if n=='vle' else [])
        checks[n]={'rows':len(t),'duplicate_keys':int(t.duplicated(k).sum()),'missing_key_values':int(t[k].isna().any(axis=1).sum())}
        nulls[n]={c:int(v) for c,v in t.isna().sum().items()}
        manifest['files'][n+'.csv']['rows']=len(t)
        assert checks[n]['duplicate_keys']==0, (n,'claves duplicadas: revisar antes de unir')
    joined=info.merge(reg,on=KEY,how='left',validate='one_to_one',indicator=True)
    checks['info_registration']={'rows_after':len(joined),'unmatched':int((joined['_merge']!='both').sum()),'registration_without_info':len(reg.merge(info[KEY],on=KEY,how='left',indicator=True).query('_merge == "left_only"'))}
    assert checks['info_registration']['unmatched']==0
    original_keys=set(map(tuple,info[KEY].to_numpy())); site_keys=set(map(tuple,vle[['code_module','code_presentation','id_site']].to_numpy()))
    active={d:set() for d in [14,28,42,56]}; total=orphan=badsite=negclick=dup_chunk=0; min_day=10**9; max_day=-10**9; activity_ed={}
    nulls['studentVle']={}
    for chunk in pd.read_csv(data/'studentVle.csv',chunksize=300000):
        total+=len(chunk)
        for c,v in chunk.isna().sum().items(): nulls['studentVle'][c]=nulls['studentVle'].get(c,0)+int(v)
        keys=list(map(tuple,chunk[KEY].to_numpy())); sites=list(map(tuple,chunk[['code_module','code_presentation','id_site']].to_numpy()))
        orphan+=sum(k not in original_keys for k in keys); badsite+=sum(k not in site_keys for k in sites)
        negclick+=int((chunk.sum_click<0).sum()); dup_chunk+=int(chunk.duplicated(KEY+['id_site','date']).sum())
        min_day=min(min_day,int(chunk.date.min())); max_day=max(max_day,int(chunk.date.max()))
        for d in active: active[d].update(map(tuple,chunk.loc[chunk.date<=d,KEY].to_numpy()))
        for k,v in chunk.groupby(['code_module','code_presentation']).size().items(): activity_ed[k]=activity_ed.get(k,0)+int(v)
    checks['studentVle']={'rows':total,'orphan_enrollment_rows':orphan,'orphan_resource_rows':badsite,'negative_click_rows':negclick,'date_min':min_day,'date_max':max_day,'duplicate_keys_within_chunks':dup_chunk,'global_daily_duplicate_check':'pendiente: conteo por chunks no demuestra unicidad global'}
    manifest['files']['studentVle.csv']['rows']=total
    checks['courses_relation']={'info_without_course':sum(tuple(k) not in set(map(tuple,courses[['code_module','code_presentation']].to_numpy())) for k in info[['code_module','code_presentation']].to_numpy())}
    initial=joined.loc[joined.date_registration.notna() & (joined.date_registration<=0)].copy()
    def counts(t):
        return {'N':len(t),'Fail':int((t.final_result=='Fail').sum()),'Withdrawn':int((t.final_result=='Withdrawn').sum()),'Approved':int(t.final_result.isin(['Pass','Distinction']).sum())}
    results={'original':counts(info),'initial':counts(initial),'unique_students':int(info.id_student.nunique()),'late_registration':int((joined.date_registration>0).sum()),'missing_registration_date':int(joined.date_registration.isna().sum()),'cuts':{}}
    rows=[]
    for label,t in [('original',joined),('initial',initial)]:
        for k,g in t.groupby(['code_module','code_presentation']): rows.append({'population':label,'module':k[0],'presentation':k[1],**counts(g),'K':None,'no_recorded_activity':None})
    for d in active:
        eligible=initial.loc[initial.date_unregistration.isna() | (initial.date_unregistration>d)]
        c=counts(eligible); c['K_sum_by_edition']=sum(len(g)//10 for _,g in eligible.groupby(['code_module','code_presentation'])); c['without_recorded_activity']=sum(tuple(k) not in active[d] for k in eligible[KEY].to_numpy()); c['withdrawn_by_cut']=len(initial)-len(eligible); results['cuts'][str(d)]=c
        for k,g in eligible.groupby(['code_module','code_presentation']): rows.append({'population':f'day_{d}','module':k[0],'presentation':k[1],**counts(g),'K':len(g)//10,'no_recorded_activity':sum(tuple(x) not in active[d] for x in g[KEY].to_numpy())})
    report={'manifest':manifest,'checks':checks,'missing_values':nulls,'populations':results,'activity_rows_by_edition':{'/'.join(k):v for k,v in activity_ed.items()}}
    (out/'auditoria-resultados.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'datasets/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    pd.DataFrame(rows).to_csv(out/'poblaciones-por-edicion.csv',index=False)
    print(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
