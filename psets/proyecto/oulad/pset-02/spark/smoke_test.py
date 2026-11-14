"""Comprobación local Spark, sin conexión cloud ni transformaciones del pipeline."""
import hashlib,json,os
from pyspark.sql import SparkSession, functions as F
spark=SparkSession.builder.appName('pset02-infra-smoke').getOrCreate()
spark.sparkContext.setLogLevel('ERROR')
try:
    assert os.statvfs('/datasets').f_flag & os.ST_RDONLY, 'El montaje datasets debe ser de solo lectura'
    with open('/datasets/manifest.json') as f: manifest=json.load(f)
    for name,meta in manifest['files'].items():
        digest=hashlib.sha256()
        with open('/datasets/'+name,'rb') as f:
            for block in iter(lambda:f.read(8*1024*1024),b''):digest.update(block)
        assert digest.hexdigest()==meta['sha256'], 'Checksum distinto: '+name
    assert spark.range(10).agg(F.sum('id')).first()[0]==45
    table=spark.read.option('header',True).csv('/datasets/studentInfo.csv')
    rows=table.count()
    assert rows==32593, f'Conteo distinto del manifiesto: {rows}'
    print(json.dumps({'status':'ok','spark_version':spark.version,
                      'range_sum':45,'student_info_rows':rows,
                      'datasets_read_only':True,'verified_input_files':len(manifest['files']),
                      'scope':'Prueba local de motor y lectura; sin conexión Snowflake.'}))
finally:
    spark.stop()
