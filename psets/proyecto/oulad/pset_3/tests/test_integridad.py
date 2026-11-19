"""Pruebas de integridad, aislamiento del hold-out y CV congelada."""
from pathlib import Path
import json,sys,tempfile,unittest
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from src import common
from src.datos import cargar_snapshot,pliegues_congelados

class Integridad(unittest.TestCase):
    def test_holdout_requires_explicit_access(self):
        with self.assertRaisesRegex(ValueError,'Hold-out reservado'):
            cargar_snapshot(particion='test')

    def test_modified_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            local=Path(temp);folder=local/'bundle';folder.mkdir()
            file=folder/'datos.csv';file.write_text('original')
            content={'files':{'datos.csv':{'sha256':common.sha256(file)}}}
            identifier=common.identity(content)
            (folder/'manifest.json').write_text(json.dumps({'id':identifier,'identity':content}))
            (local/'snapshot-current.json').write_text(json.dumps({'directory':'bundle','id':identifier}))
            with patch.object(common,'LOCAL',local):
                common.read_bundle()
                file.write_text('alterado')
                with self.assertRaisesRegex(ValueError,'Artefacto alterado'):common.read_bundle()

    def test_pointer_cannot_escape_local(self):
        with tempfile.TemporaryDirectory() as temp:
            local=Path(temp)
            (local/'snapshot-current.json').write_text(json.dumps({'directory':'../outside','id':'invalid'}))
            with patch.object(common,'LOCAL',local):
                with self.assertRaisesRegex(ValueError,'fuera de .local'):common.read_bundle()

    def test_real_train_and_folds_do_not_overlap(self):
        train,_=cargar_snapshot()
        self.assertEqual(len(train),16331)
        folder,_=common.read_bundle('splits-current.json')
        import pandas as pd
        assignments=pd.read_csv(folder/'assignments.csv')
        hold=assignments.loc[assignments.partition.eq('test')]
        self.assertFalse(set(train.id_student)&set(hold.id_student))
        self.assertFalse(set(train.enrollment_key)&set(hold.enrollment_key))
        seen=[]
        for a,b in pliegues_congelados(train):
            self.assertFalse(set(train.iloc[a].id_student)&set(train.iloc[b].id_student))
            seen.extend(b.tolist())
        self.assertEqual(sorted(seen),list(range(len(train))))

    def test_folds_do_not_regenerate_after_label_changes(self):
        train,_=cargar_snapshot()
        before=[b.tolist() for _,b in pliegues_congelados(train)]
        train['target_class']='etiqueta_modificada_solo_para_prueba'
        after=[b.tolist() for _,b in pliegues_congelados(train)]
        self.assertEqual(before,after)

    def test_all_cutoffs_keep_the_frozen_train_keys(self):
        keys=None
        for cutoff in [14,28,42,56]:
            train,_=cargar_snapshot(cutoff=cutoff)
            current=set(train.enrollment_key)
            if keys is not None:self.assertEqual(current,keys)
            keys=current

if __name__=='__main__':unittest.main(verbosity=2)
