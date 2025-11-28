import streamlit as st
from code_quality_analyzer.detectors import RuleBasedDetector
from code_quality_analyzer.suggestion_engine import suggestions_for_smells, autofix_code
from code_quality_analyzer.ml_classifier import load_model, predict_code_quality
import os

st.title("Code Quality Analyzer (Streamlit)")
lang = st.selectbox('Language', ['py', 'java'])
code = st.text_area('Paste code here', height=300)
model_path = st.text_input('Model path (optional)', value=os.getenv('MODEL_PATH', 'models/code_quality_model.joblib'))
auto = st.checkbox('Apply autofix')

if st.button('Analyze'):
    detector = RuleBasedDetector()
    if lang == 'java':
        smells = detector.detect_java_issues(code)
    else:
        smells = detector.detect_all(code)
    st.subheader('Smells')
    for s in smells:
        st.write(f"{s.lineno or '-'}: {s.kind} - {s.message}")
    st.subheader('Suggestions')
    for s in suggestions_for_smells(smells):
        st.write(f"{s['smell']['kind']}: {s['suggestions']}")
    if model_path and os.path.exists(model_path) and lang != 'java':
        try:
            label, prob = predict_code_quality(code, model_path)
            st.subheader('ML Classification')
            st.write({'label': label, 'confidence': prob})
        except Exception as e:
            st.error('Model load/predict error: ' + str(e))
    if auto:
        fixed = autofix_code(code)
        st.subheader('Autofix result')
        st.code(fixed, language='python')