from flask import Flask, request, render_template_string, jsonify
import os
from .detectors import RuleBasedDetector
from .suggestion_engine import suggestions_for_smells
from .ml_classifier import predict_code_quality, compute_quality_score

TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Code Quality Analyzer</title>
<style>
body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
h1 { color: #333; }
textarea { width: 100%; font-family: monospace; }
.error { color: red; background: #fee; padding: 10px; border-radius: 5px; margin: 10px 0; }
.success { color: green; }
input[type=submit] { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
input[type=submit]:hover { background: #0056b3; }
</style>
</head>
<body>
<h1>Code Quality Analyzer</h1>
{% if error %}
<div class="error">{{ error }}</div>
{% endif %}
<form method=post>
<p>
<label>Language:</label>
<select name=lang>
  <option value="py">Python</option>
  <option value="java">Java</option>
  <option value="javascript">JavaScript</option>
  <option value="typescript">TypeScript</option>
  <option value="cpp">C/C++</option>
  <option value="go">Go</option>
  <option value="rust">Rust</option>
  <option value="ruby">Ruby</option>
  <option value="php">PHP</option>
</select>
</p>
<p>
<textarea name=code rows=20 cols=80 placeholder="Paste your code here...">{{ request.form.get('code', '') }}</textarea>
</p>
<p>
<label>Model path (optional):</label>
<input name=model value="{{ request.form.get('model', 'models/code_quality_model.joblib') }}" size=40>
</p>
<p>
<input type=submit value="Analyze Code">
</p>
</form>
{% if analysis %}
<hr>
<h2>Analysis Results</h2>
<h3 class="success">Quality Score: {{ analysis.quality_score }}/100</h3>
<h3>Code Smells ({{ analysis.smells|length }})</h3>
<ul>
{% for s in analysis.smells %}
  <li><b>{{ s.kind }}</b>: {{ s.message }} {% if s.lineno %}(line {{ s.lineno }}){% endif %}</li>
{% endfor %}
{% if not analysis.smells %}
  <li>No code smells detected! Great job! ✅</li>
{% endif %}
</ul>
<h3>Suggestions</h3>
<ul>
{% for s in analysis.suggestions %}
  <li><b>{{ s.smell.kind }}</b>: 
    <ul>
    {% for sug in s.suggestions %}
      <li>{{ sug }}</li>
    {% endfor %}
    </ul>
  </li>
{% endfor %}
</ul>
{% if analysis.ml_classification %}
<h3>ML Classification</h3>
{% if analysis.ml_classification.error %}
  <p style="color: orange;">{{ analysis.ml_classification.error }}</p>
{% else %}
  <p>Label: <b>{{ analysis.ml_classification.label }}</b> (confidence: {{ '%.2f'|format(analysis.ml_classification.confidence) }})</p>
{% endif %}
{% endif %}
{% endif %}
</body>
</html>
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
        error = None
        if request.method == 'POST':
            try:
                code = request.form.get('code', '').strip()
                if not code:
                    error = 'Please provide some code to analyze'
                    return render_template_string(TEMPLATE, analysis=None, error=error)
                
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
                if model_path and os.path.exists(model_path):
                    try:
                        label, prob = predict_code_quality(code, model_path)
                        ml_result = {'label': label, 'confidence': prob}
                    except Exception as e:
                        ml_result = {'error': f'Failed to use model: {str(e)}'}
                elif model_path:
                    ml_result = {'error': 'Model file not found'}
                
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
            except Exception as e:
                error = f'Error analyzing code: {str(e)}'
                app.logger.error(f'Analysis error: {e}', exc_info=True)
        
        return render_template_string(TEMPLATE, analysis=analysis, error=error)

    @app.route('/api/analyze', methods=['POST'])
    def api_analyze():
        try:
            data = request.json
            code = data.get('code', '').strip()
            if not code:
                return jsonify({'error': 'No code provided'}), 400
            
            model_path = data.get('model')
            if not model_path:
                model_path = os.environ.get('MODEL_PATH')
            
            detector = RuleBasedDetector()
            smells = detector.detect_all(code)
            suggestions = suggestions_for_smells(smells)
            ml_result = None
            
            if model_path and os.path.exists(model_path):
                try:
                    label, prob = predict_code_quality(code, model_path)
                    ml_result = {'label': label, 'confidence': prob}
                except Exception as e:
                    ml_result = {'error': str(e)}
            
            score = compute_quality_score(
                ml_result.get('label') if ml_result else None,
                ml_result.get('confidence') if ml_result else None,
                smells
            )
            
            return jsonify({
                'smells': [s.to_dict() for s in smells],
                'suggestions': suggestions,
                'ml_classification': ml_result,
                'quality_score': score,
            })
        except Exception as e:
            app.logger.error(f'API error: {e}', exc_info=True)
            return jsonify({'error': str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
