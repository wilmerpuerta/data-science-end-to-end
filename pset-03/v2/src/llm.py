"""Sexto candidato: LLM generativo por prompting, con ejemplos solo del train-fold."""
from pathlib import Path
import hashlib,json
import numpy as np
from sklearn.base import BaseEstimator,ClassifierMixin
from sklearn.utils.validation import check_is_fitted
from .openai_api import ResponsesClient,MODEL

class OpenAIPromptClassifier(ClassifierMixin,BaseEstimator):
 def __init__(self,examples_per_class=6,prompt_style='reference',score_temperature=1.,batch_size=32,random_state=42):
  self.examples_per_class=examples_per_class;self.prompt_style=prompt_style;self.score_temperature=score_temperature;self.batch_size=batch_size;self.random_state=random_state
 def fit(self,X,y):
  a=np.asarray(X,dtype=float);labels=np.asarray(y)
  if a.ndim!=2 or not np.isfinite(a).all():raise ValueError('Preparación debe producir matriz finita')
  self.classes_=np.asarray(sorted(set(labels)));assert list(self.classes_)==['Approved','Fail','Withdrawn']
  self.feature_names_=[str(c) for c in X.columns] if hasattr(X,'columns') else [f'feature_{i}' for i in range(a.shape[1])]
  self.n_features_in_=a.shape[1];self.prior_=[float(np.mean(labels==c)) for c in self.classes_];self.examples_=[]
  rng=np.random.default_rng(self.random_state)
  for c in self.classes_:
   positions=np.flatnonzero(labels==c);chosen=rng.choice(positions,size=min(len(positions),int(self.examples_per_class)),replace=False)
   self.examples_ += [{'x':self.encode(a[i]),'class':str(c)} for i in chosen]
  self.training_rows_=len(a);self.context_rows_=len(self.examples_);self.model_id_=MODEL;self.prediction_cache_={}
  return self
 @staticmethod
 def encode(row):return [[int(i),float(f'{v:.6g}')] for i,v in enumerate(row) if v!=0]
 def predict_proba(self,X):
  check_is_fitted(self,'classes_');a=np.asarray(X,dtype=float)
  if a.ndim!=2 or a.shape[1]!=self.n_features_in_ or not np.isfinite(a).all():raise ValueError('Entrada inválida')
  encoded=[self.encode(row) for row in a];keys=[hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest() for x in encoded]
  missing=list(dict.fromkeys(k for k in keys if k not in self.prediction_cache_));lookup=dict(zip(keys,encoded));client=None
  for start in range(0,len(missing),int(self.batch_size)):
   batch=missing[start:start+int(self.batch_size)]
   system=('You are a pretrained generative model estimating academic outcome probabilities from transformed tabular features. '
           'Return probabilities in order Approved, Fail, Withdrawn for each query, in the exact input order. Each triple must be finite, nonnegative and sum to one. '
           'Inputs are the same numerical training-fold-imputed, standardized and one-hot encoded features used by comparison classifiers. Sparse pairs [column,value] omit zero entries; '
           'do not treat zero as a missing observation. No student identity or future outcome is provided for query rows. Use only the supplied training examples and priors. '
           'These are probability estimates to be evaluated, not calibrated probabilities guaranteed by the model.')
   if self.prompt_style=='prior_focus':system+=' Respect the empirical training prior when examples alone are ambiguous.'
   elif self.prompt_style=='conservative':system+=' Avoid extreme probabilities unsupported by similar examples.'
   elif self.prompt_style!='reference':raise ValueError('Estilo no prefijado')
   user=json.dumps({'classes':self.classes_.tolist(),'columns':self.feature_names_,'training_pool_rows':self.training_rows_,'training_prior':self.prior_,'examples':self.examples_,'queries':[lookup[k] for k in batch]},separators=(',',':'))
   if client is None:client=ResponsesClient()
   parsed,_=client.predict_batch(system,user,len(batch));p=np.asarray(parsed,dtype=float)
   if p.shape!=(len(batch),3) or not np.isfinite(p).all() or (p<0).any() or (p>1).any() or (p.sum(axis=1)<=0).any():raise RuntimeError('LLM produjo probabilidades inválidas; no se reemplazan con resultados ficticios')
   if not np.allclose(p.sum(axis=1),1,atol=.02):raise RuntimeError('Las probabilidades no suman aproximadamente uno')
   p=p/p.sum(axis=1,keepdims=True)
   for k,v in zip(batch,p):self.prediction_cache_[k]=v.tolist()
  p=np.asarray([self.prediction_cache_[k] for k in keys]);t=float(self.score_temperature)
  if t<=0:raise ValueError('Temperatura de puntuación inválida')
  if t!=1:
   p=np.power(np.clip(p,1e-12,1),1/t);p/=p.sum(axis=1,keepdims=True)
  return p
 def predict(self,X):return self.classes_[np.argmax(self.predict_proba(X),axis=1)]
