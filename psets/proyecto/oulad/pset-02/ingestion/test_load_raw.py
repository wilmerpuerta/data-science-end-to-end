"""Pruebas de invariantes de publicación, sin Snowflake ni secretos."""
from pathlib import Path
import csv,hashlib,json,tempfile,unittest
from unittest.mock import MagicMock,patch
import load_raw as loader

class RawInvariants(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.data=Path(self.tmp.name)
        content=b'code_module,code_presentation\n"AAA","2013J"\n"AAA","2013J"\n"BBB",""\n'
        (self.data/'courses.csv').write_bytes(content)
        self.meta={'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content),'rows':3}
        (self.data/'manifest.json').write_text(json.dumps({'files':{'courses.csv':self.meta}}))
        self.columns=['code_module','code_presentation']
        self.patch=patch.object(loader,'DATA',self.data);self.patch.start();self.addCleanup(self.patch.stop)

    def test_source_duplicates_and_empty_values_preserved(self):
        result=loader.verified_files('courses.csv')
        self.assertEqual(result[0][1]['rows'],3)
        with (self.data/'courses.csv').open() as f:rows=list(csv.DictReader(f))
        self.assertEqual(rows[0],rows[1]);self.assertEqual(rows[2]['code_presentation'],'')
        (self.data/'courses.csv').write_text('changed')
        with self.assertRaisesRegex(RuntimeError,'input_checksum_mismatch'):loader.verified_files('courses.csv')

    def cursor(self,fail_publish=False):
        conn=MagicMock();cur=conn.cursor.return_value.__enter__.return_value
        history=[]
        def execute(sql,params=None):
            history.append(sql)
            if sql.startswith('DESC TABLE'):
                cur.fetchall.return_value=[(c,) for c in ['CODE_MODULE','CODE_PRESENTATION','SOURCE_SHA256','SOURCE_ROW_NUMBER','LOAD_RUN_ID','LOADED_AT']]
            if sql.startswith('PUT '):cur.fetchall.return_value=[('a','b',1,1,'GZIP','GZIP','UPLOADED','')]
            if fail_publish and sql.startswith('INSERT INTO COURSES SELECT'):raise RuntimeError('simulated_publish_error')
            return cur
        cur.execute.side_effect=execute
        return conn,history

    def test_reconciled_version_is_noop(self):
        conn,history=self.cursor()
        with patch.object(loader,'ensure_managed'),patch.object(loader,'target_counts',return_value={'rows':3,'unique_source_rows':3,'other_checksums':0}):
            result=loader.load_file(conn,'courses.csv',self.meta,self.columns,'run1','attempt1')
        self.assertEqual(result['status'],'NOOP')
        self.assertFalse(any(s.startswith(('PUT ','DELETE FROM COURSES')) for s in history))

    def test_bad_temporary_count_does_not_delete_target(self):
        conn,history=self.cursor()
        with patch.object(loader,'ensure_managed'),patch.object(loader,'target_counts',side_effect=[{'rows':0,'unique_source_rows':0,'other_checksums':0},{'rows':2,'unique_source_rows':2,'other_checksums':0}]):
            with self.assertRaisesRegex(RuntimeError,'copy_reconciliation_failed'):
                loader.load_file(conn,'courses.csv',self.meta,self.columns,'run2','attempt2')
        self.assertNotIn('BEGIN',history);self.assertFalse(any(s.startswith('DELETE FROM COURSES') for s in history))

    def test_publish_error_rolls_back(self):
        conn,history=self.cursor(fail_publish=True)
        with patch.object(loader,'ensure_managed'),patch.object(loader,'target_counts',side_effect=[{'rows':0,'unique_source_rows':0,'other_checksums':0},{'rows':3,'unique_source_rows':3,'other_checksums':0}]):
            with self.assertRaisesRegex(RuntimeError,'simulated_publish_error'):
                loader.load_file(conn,'courses.csv',self.meta,self.columns,'run3','attempt3')
        self.assertIn('ROLLBACK',history);self.assertNotIn('COMMIT',history)

if __name__=='__main__':unittest.main()
