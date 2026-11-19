"""Transformaciones Spark deterministas, sin red ni resultados finales."""
from pyspark.sql import functions as F

CUTOFFS=(14,28,42,56)
KEYS=['enrollment_key','cutoff_day']
STATIC=['id_student','edition_key','code_module','code_presentation','gender','region',
        'highest_education','imd_band','age_band','num_of_prev_attempts','studied_credits',
        'disability','is_imd_missing','module_presentation_length','registration_days_before_start']
ZERO_FEATURES=['clicks_through_cutoff','clicks_since_start','clicks_prestart','clicks_day_zero',
               'active_days_through_cutoff','resources_through_cutoff','activity_types_through_cutoff',
               'clicks_current_14d','active_days_current_14d','clicks_forum_current_14d',
               'clicks_oucontent_current_14d']
ACTIVITY=ZERO_FEATURES+['clicks_previous_14d','click_change_14d','click_ratio_14d',
                       'last_activity_day','recency_days','has_recorded_activity','log_coverage_known']
OUTPUT=KEYS+STATIC+ACTIVITY

def population(enrollments,withdrawals,cutoff):
    """Elegibilidad primero, sin consultar resultados finales."""
    assert cutoff in CUTOFFS
    return (enrollments.filter(F.col('date_registration')<=0)
            .join(withdrawals.select('enrollment_key','date_unregistration'),'enrollment_key','inner')
            .filter(F.col('date_unregistration').isNull() | (F.col('date_unregistration')>cutoff))
            .select('enrollment_key','id_student','edition_key',
                    (-F.col('date_registration')).cast('long').alias('registration_days_before_start')))

def build_features(eligible,activity,context,editions,resources,cutoff):
    """Filtra de nuevo por corte aunque la extracción ya limite al día 56."""
    assert cutoff in CUTOFFS
    observed=(activity.filter(F.col('activity_day')<=cutoff)
              .join(F.broadcast(eligible.select('enrollment_key')),'enrollment_key','inner')
              .join(F.broadcast(resources.select('resource_key','activity_type')),'resource_key','inner'))
    day=F.col('activity_day');click=F.col('click_count')
    current=day.between(cutoff-13,cutoff);previous=day.between(cutoff-27,cutoff-14)
    def clicks_when(condition):return F.sum(F.when(condition,click).otherwise(F.lit(0))).cast('long')
    aggregated=observed.groupBy('enrollment_key').agg(
        F.sum('click_count').cast('long').alias('clicks_through_cutoff'),
        clicks_when(day>=1).alias('clicks_since_start'),
        clicks_when(day<0).alias('clicks_prestart'),
        clicks_when(day==0).alias('clicks_day_zero'),
        F.countDistinct('activity_day').cast('long').alias('active_days_through_cutoff'),
        F.countDistinct('id_site').cast('long').alias('resources_through_cutoff'),
        F.countDistinct('activity_type').cast('long').alias('activity_types_through_cutoff'),
        clicks_when(current).alias('clicks_current_14d'),
        F.countDistinct(F.when(current,day)).cast('long').alias('active_days_current_14d'),
        clicks_when(current & (F.col('activity_type')=='forumng')).alias('clicks_forum_current_14d'),
        clicks_when(current & (F.col('activity_type')=='oucontent')).alias('clicks_oucontent_current_14d'),
        clicks_when(previous).alias('_previous'),
        F.max('activity_day').cast('long').alias('last_activity_day'))
    attributes=context.select('enrollment_key','code_module','code_presentation','gender','region',
        'highest_education','imd_band','age_band','num_of_prev_attempts','studied_credits','disability','is_imd_missing')
    result=(eligible.join(F.broadcast(attributes),'enrollment_key','left')
            .join(F.broadcast(editions.select('edition_key','module_presentation_length')),'edition_key','left')
            .join(aggregated,'enrollment_key','left').fillna(0,subset=ZERO_FEATURES)
            .withColumn('cutoff_day',F.lit(cutoff).cast('long'))
            .withColumn('clicks_previous_14d',F.coalesce(F.col('_previous'),F.lit(0)).cast('long') if cutoff>=28 else F.lit(None).cast('long')))
    return (result.withColumn('click_change_14d',F.col('clicks_current_14d')-F.col('clicks_previous_14d'))
            .withColumn('click_ratio_14d',F.when(F.col('clicks_previous_14d')>0,
                        F.col('clicks_current_14d')/F.col('clicks_previous_14d')).cast('double'))
            .withColumn('recency_days',(F.lit(cutoff)-F.col('last_activity_day')).cast('long'))
            .withColumn('has_recorded_activity',F.col('last_activity_day').isNotNull())
            .withColumn('log_coverage_known',F.lit(False))
            .select(*OUTPUT))
