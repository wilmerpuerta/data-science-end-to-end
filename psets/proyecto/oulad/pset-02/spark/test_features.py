"""Casos sintéticos de frontera, ausencia de actividad y aislamiento temporal."""
import argparse,json
from pathlib import Path
from datetime import datetime,timezone
from pyspark.sql import SparkSession,functions as F
from features import population,build_features,OUTPUT

p=argparse.ArgumentParser();p.add_argument('--run-id',required=True);args=p.parse_args()
spark=SparkSession.builder.appName('pset02-feature-contract-tests').getOrCreate()
spark.sparkContext.setLogLevel('ERROR')
report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'action':'test-features','run_id':args.run_id,'status':'failed'}
try:
    enroll=spark.createDataFrame([('A',1,'E',-10),('B',2,'E',-1),('C',3,'E',1),('D',4,'E',None),('E',5,'E',-3),('F',6,'E',-2)],'enrollment_key string,id_student long,edition_key string,date_registration long')
    withdrawal=spark.createDataFrame([('A',20),('B',None),('C',None),('D',None),('E',14),('F',None)],'enrollment_key string,date_unregistration long')
    context=spark.createDataFrame([(k,'AAA','2014J','F','region','education',None,'0-35',0,60,'N',True) for k in ['A','B','C','D','E','F']],
        'enrollment_key string,code_module string,code_presentation string,gender string,region string,highest_education string,imd_band string,age_band string,num_of_prev_attempts long,studied_credits long,disability string,is_imd_missing boolean')
    editions=spark.createDataFrame([('E',269)],'edition_key string,module_presentation_length long')
    resources=spark.createDataFrame([('R', 'forumng')],'resource_key string,activity_type string')
    events=spark.createDataFrame([('A','R',1,-1,2),('A','R',1,0,3),('A','R',1,1,5),('A','R',1,14,7),('A','R',1,15,999),('F','R',1,1,4),('F','R',1,20,8)],
        'enrollment_key string,resource_key string,id_site long,activity_day long,click_count long')
    eligible14=population(enroll,withdrawal,14)
    assert {r.enrollment_key for r in eligible14.collect()}=={'A','B','F'}
    result14=build_features(eligible14,events,context,editions,resources,14)
    rows={r.enrollment_key:r.asDict() for r in result14.collect()}
    a,b=rows['A'],rows['B']
    assert (a['clicks_prestart'],a['clicks_day_zero'],a['clicks_since_start'],a['clicks_through_cutoff'],a['clicks_current_14d'])==(2,3,12,17,12)
    assert a['recency_days']==0 and a['clicks_previous_14d'] is None and a['click_change_14d'] is None
    assert b['clicks_through_cutoff']==0 and b['recency_days'] is None and not b['has_recorded_activity'] and not b['log_coverage_known']
    eligible28=population(enroll,withdrawal,28)
    assert {r.enrollment_key for r in eligible28.collect()}=={'B','F'}
    f=build_features(eligible28,events,context,editions,resources,28).filter("enrollment_key='F'").first()
    assert (f.clicks_current_14d,f.clicks_previous_14d,f.click_change_14d,f.click_ratio_14d)==(8,4,4,2.0)
    mutated=events.withColumn('click_count',F.when(F.col('activity_day')>14,F.lit(999999)).otherwise(F.col('click_count')))
    changed=build_features(eligible14,mutated,context,editions,resources,14)
    assert result14.exceptAll(changed).count()==0 and changed.exceptAll(result14).count()==0
    assert result14.columns==OUTPUT and 'final_result' not in OUTPUT and 'date_unregistration' not in OUTPUT
    assert a['imd_band'] is None and a['is_imd_missing']
    report.update(status='ok',cases_passed=7,scope='Casos sintéticos: elegibilidad inclusiva, ventanas, cambio, ausencia de actividad, perturbación futura, columnas e IMD.')
except Exception as e:report.update(error_class=type(e).__name__)
finally:
    spark.stop();Path('/workspace/output',args.run_id+'.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
if report['status']!='ok':raise SystemExit(1)
