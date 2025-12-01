from flask import Flask, request, render_template_string, jsonify
import os
from .detectors import RuleBasedDetector
from .suggestion_engine import suggestions_for_smells

# ML dependencies are optional (not available in Vercel serverless)
try:
    from .ml_classifier import predict_code_quality, compute_quality_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    def predict_code_quality(*args, **kwargs):
        raise ImportError("ML dependencies not available")
    def compute_quality_score(label, confidence, smells):
        # Fallback quality score based on smell count
        return max(0, 100 - len(smells) * 10)

TEMPLATE = """
<!doctype html>
<title>Code Quality Analyzer</title>
<h1>Code Quality Analyzer</h1>
<form method=post>
Language: <select name=lang><option value="py">Python</option><option value="java">Java</option></select>
<br/>
<textarea name=code rows=20 cols=80 placeholder="Paste code here"></textarea>
<br/>
Model path (optional): <input name=model value="models/code_quality_model.joblib" size=40>
<br/>
<input type=submit value=Analyze>
</form>
{% if analysis %}
<h3>Quality score: {{ analysis.quality_score }}</h3>
<h2>Analysis</h2>
<h3>Smells</h3>
<ul>
{% for s in analysis.smells %}
  <li><b>{{ s.kind }}</b>: {{ s.message }} {% if s.lineno %}(line {{ s.lineno }}){% endif %}</li>
{% endfor %}
</ul>
<h3>Suggestions</h3>
<ul>
{% for s in analysis.suggestions %}
  <li><b>{{ s.smell.kind }}</b>: <ul>{% for sug in s.suggestions %}<li>{{ sug }}</li>{% endfor %}</ul></li>
{% endfor %}
</ul>
{% if analysis.ml_classification %}
<h3>ML Classification</h3>
<p>Label: {{ analysis.ml_classification.label }} (confidence: {{ '%.2f'|format(analysis.ml_classification.confidence) }})</p>
{% if analysis.ml_classification.quality_score is defined %}
<p>Quality score: {{ analysis.ml_classification.quality_score }}</p>
{% endif %}
{% endif %}
{% endif %}
"""


def create_app():
    app = Flask(__name__)
    # At startup, attempt to download model if MODEL_URL is provided and MODEL_PATH doesn't exist
    import os
    model_path = os.environ.get('MODEL_PATH', '/app/models/code_quality_model.joblib')
    model_url = os.environ.get('MODEL_URL')
    if model_url and not os.path.exists(model_path):
        try:
            import requests
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            resp = requests.get(model_url, timeout=60)
            if resp.status_code == 200:
                with open(model_path, 'wb') as fh:
                    fh.write(resp.content)
        except Exception:
            # If download fails, just continue; ML predictions will be disabled
            pass

    @app.route('/', methods=['GET', 'POST'])
    def index():
        analysis = None
        if request.method == 'POST':
            code = request.form['code']
            lang = request.form.get('lang', 'py')
            # first check form input; fallback to environment variable MODEL_PATH
            model_path = request.form.get('model')
            if not model_path:
                model_path = os.environ.get('MODEL_PATH')
            detector = RuleBasedDetector()
            if lang == 'java':
                smells = detector.detect_java_issues(code)
            else:
                smells = detector.detect_all(code)
            suggestions = suggestions_for_smells(smells)
            ml_result = None
            if model_path and ML_AVAILABLE:
                try:
                    label, prob = predict_code_quality(code, model_path)
                    ml_result = {'label': label, 'confidence': prob}
                except Exception:
                    ml_result = {'error': 'Failed to use model (not trained or invalid path)'}
            elif not ML_AVAILABLE:
                ml_result = {'error': 'ML dependencies not installed (use Docker deployment for ML features)'}
            # compute quality score even if ML not used
            score = compute_quality_score(None, None, smells)
            if ml_result and isinstance(ml_result, dict) and 'label' in ml_result:
                score = compute_quality_score(ml_result['label'], ml_result['confidence'], smells)
            analysis = {
                'smells': [s.to_dict() for s in smells],
                'suggestions': suggestions,
                'ml_classification': ml_result,
                'quality_score': score,
            }
        return render_template_string(TEMPLATE, analysis=analysis)

    @app.route('/api/analyze', methods=['POST'])
    def api_analyze():
        data = request.json
        code = data.get('code', '')
        model_path = data.get('model')
        if not model_path:
            model_path = os.environ.get('MODEL_PATH')
        detector = RuleBasedDetector()
        smells = detector.detect_all(code)
        suggestions = suggestions_for_smells(smells)
        ml_result = None
        if model_path and ML_AVAILABLE:
            try:
                label, prob = predict_code_quality(code, model_path)
                ml_result = {'label': label, 'confidence': prob}
            except Exception:
                ml_result = {'error': 'Failed to use model (not trained or invalid path)'}
        elif not ML_AVAILABLE:
            ml_result = {'error': 'ML dependencies not installed'}
        return jsonify({
            'smells': [s.to_dict() for s in smells],
            'suggestions': suggestions,
            'ml_classification': ml_result,
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
