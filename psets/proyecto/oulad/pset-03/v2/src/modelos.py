"""Seis familias iniciales; defaults salvo semilla para reproducibilidad."""
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.dummy import DummyClassifier
from .llm import OpenAIPromptClassifier

def candidatos(seed=42):
    return {
        "lineal": LogisticRegression(random_state=seed),
        "bagging": RandomForestClassifier(random_state=seed),
        "boosting": HistGradientBoostingClassifier(random_state=seed),
        "red_neuronal": MLPClassifier(random_state=seed),
        "bayes": GaussianNB(),
        "llm_generativo": OpenAIPromptClassifier(random_state=seed),
    }

def ingenua():
    return DummyClassifier(strategy="most_frequent")


def construir_modelo(nombre,*,solo_estaticas=False):
    from .pipeline import construir_pipeline
    p=construir_pipeline(candidatos()[nombre],solo_estaticas=solo_estaticas)
    if nombre=='llm_generativo':p.named_steps['preparacion'].set_output(transform='pandas')
    return p
