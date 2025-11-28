import os
from typing import Tuple
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from joblib import dump, load
import numpy as np
from .parser import ASTFeatureExtractor


def extract_numeric_features(src: str) -> dict:
    extractor = ASTFeatureExtractor()
    feats = extractor.extract_features(src)
    # return selected numeric features
    return {
        'num_functions': feats.get('num_functions', 0),
        'avg_function_length': feats.get('avg_function_length', 0),
        'max_function_length': feats.get('max_function_length', 0),
        'num_classes': feats.get('num_classes', 0),
        'num_imports': feats.get('num_imports', 0),
        'num_assignments': feats.get('num_assignments', 0),
        'max_nesting': feats.get('max_nesting', 0),
    }


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # convert literal "\\n" sequences to real newlines
    if 'code' in df.columns:
        df['code'] = df['code'].astype(str).apply(lambda s: s.replace('\\n', '\n'))
    # Expected columns: 'code', 'label'
    return df


def featurize_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
    # numeric features
    numeric_features = []
    for src in df['code']:
        numeric_features.append(list(extract_numeric_features(src).values()))
    numeric_features = np.array(numeric_features)
    # token features
    vectorizer = CountVectorizer(ngram_range=(1,2), token_pattern=r"\b\w+\b", min_df=1)
    token_features = vectorizer.fit_transform(df['code'])

    # combine: numeric + tokens
    # For training, the pipeline should be maintained; but for simplicity, we return components
    return {'numeric': numeric_features, 'tokens': (token_features, vectorizer)}, df['label'].values


def train_model(df: pd.DataFrame, output_path: str):
    components, y = featurize_dataframe(df)
    numeric = components['numeric']
    tokens, vect = components['tokens']

    # scale numeric
    scaler = StandardScaler()
    numeric_scaled = scaler.fit_transform(numeric)

    # combine sparse tokens and dense numeric
    from scipy.sparse import hstack
    X = hstack([tokens, numeric_scaled])

    # simple logistic regression
    model = LogisticRegression(max_iter=1000)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Save model, vectorizer, scaler
    dump({'model': model, 'vectorizer': vect, 'scaler': scaler}, output_path)
    return acc


def load_model(path: str):
    data = load(path)
    return data['model'], data['vectorizer'], data['scaler']


def predict_code_quality(code: str, model_path: str):
    model, vect, scaler = load_model(model_path)
    numeric = np.array([list(extract_numeric_features(code).values())])
    numeric_scaled = scaler.transform(numeric)
    tokens = vect.transform([code])
    from scipy.sparse import hstack
    X = hstack([tokens, numeric_scaled])
    pred = model.predict(X)[0]
    prob = model.predict_proba(X).max()
    return pred, float(prob)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset')
    parser.add_argument('output')
    args = parser.parse_args()
    df = load_dataset(args.dataset)
    acc = train_model(df, args.output)
    print('Trained model accuracy:', acc)
