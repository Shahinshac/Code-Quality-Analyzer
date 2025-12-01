from flask import Flask, request, render_template_string, jsonify
import os
from .detectors import RuleBasedDetector
from .suggestion_engine import suggestions_for_smells
from .ml_classifier import predict_code_quality, compute_quality_score

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Code Quality Analyzer - 40+ Programming Languages</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-attachment: fixed;
  min-height: 100vh;
  padding: 20px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  overflow: hidden;
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(-30px); }
  to { opacity: 1; transform: translateY(0); }
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 50px 40px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: pulse 15s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.header h1 {
  font-size: 2.8em;
  margin-bottom: 10px;
  animation: fadeInDown 0.8s ease-in;
  position: relative;
  z-index: 1;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.header h1 i {
  animation: rotate360 3s linear infinite;
  display: inline-block;
}

@keyframes rotate360 {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.header p {
  font-size: 1.2em;
  opacity: 0.95;
  position: relative;
  z-index: 1;
  animation: fadeIn 1s ease-in 0.3s both;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-30px); }
  to { opacity: 1; transform: translateY(0); }
}

.content {
  padding: 40px;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
  font-size: 1.1em;
}

.language-selector {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 25px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 15px;
}

.language-selector::-webkit-scrollbar {
  width: 8px;
}

.language-selector::-webkit-scrollbar-track {
  background: #e0e0e0;
  border-radius: 10px;
}

.language-selector::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
}

.language-option {
  position: relative;
}

.language-option input[type="radio"] {
  position: absolute;
  opacity: 0;
}

.language-option label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 10px;
  background: white;
  border: 2px solid #ddd;
  border-radius: 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  font-size: 0.9em;
  position: relative;
  overflow: hidden;
}

.language-option label::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.language-option label:hover::before {
  width: 300px;
  height: 300px;
}

.language-option label i {
  font-size: 1.1em;
  transition: transform 0.3s ease;
}

.language-option input[type="radio"]:checked + label {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  transform: scale(1.05);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.5);
  animation: bounce 0.5s ease;
}

@keyframes bounce {
  0%, 100% { transform: scale(1.05); }
  50% { transform: scale(1.1); }
}

.language-option input[type="radio"]:checked + label i {
  transform: scale(1.2) rotate(5deg);
  animation: wiggle 0.5s ease;
}

@keyframes wiggle {
  0%, 100% { transform: scale(1.2) rotate(0deg); }
  25% { transform: scale(1.2) rotate(-5deg); }
  75% { transform: scale(1.2) rotate(5deg); }
}

.language-option label:hover {
  border-color: #667eea;
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.language-option label:active {
  transform: translateY(-1px);
}

textarea {
  width: 100%;
  padding: 15px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  border: 2px solid #ddd;
  border-radius: 10px;
  resize: vertical;
  transition: border-color 0.3s ease;
  background: #f9f9f9;
}

textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

input[type="text"] {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

input[type="text"]:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn-analyze {
  width: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.3em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
}

.btn-analyze::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.btn-analyze:hover::before {
  width: 400px;
  height: 400px;
}

.btn-analyze:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.6);
}

.btn-analyze:active {
  transform: translateY(-2px) scale(1);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.5);
}

.btn-analyze i {
  margin-right: 10px;
  animation: pulse-icon 2s ease-in-out infinite;
}

@keyframes pulse-icon {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.error {
  background: #fee;
  color: #c33;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 20px;
  border-left: 4px solid #c33;
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.results {
  margin-top: 40px;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.score-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 15px;
  text-align: center;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.score-number {
  font-size: 4em;
  font-weight: bold;
  margin: 10px 0;
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  from { transform: scale(0); }
  to { transform: scale(1); }
}

.section {
  background: #f9f9f9;
  padding: 25px;
  border-radius: 15px;
  margin-bottom: 25px;
  border-left: 5px solid #667eea;
}

.section h3 {
  color: #667eea;
  margin-bottom: 15px;
  font-size: 1.5em;
}

.smell-item {
  background: white;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 10px;
  border-left: 4px solid #ff6b6b;
  animation: slideInLeft 0.5s ease-out;
}

@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-30px); }
  to { opacity: 1; transform: translateX(0); }
}

.smell-kind {
  font-weight: 600;
  color: #c33;
  text-transform: uppercase;
  font-size: 0.9em;
}

.suggestion-item {
  background: white;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 10px;
  border-left: 4px solid #51cf66;
}

.no-issues {
  text-align: center;
  padding: 40px;
  color: #51cf66;
  font-size: 1.3em;
  font-weight: 600;
}

.ml-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: 20px;
  border-radius: 15px;
  margin-top: 20px;
}

.loading {
  display: none;
  text-align: center;
  padding: 20px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.badge {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
  margin-right: 5px;
}

.badge-good { background: #51cf66; color: white; }
.badge-bad { background: #ff6b6b; color: white; }
.badge-warning { background: #ffa500; color: white; }

.btn-example {
  background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(81, 207, 102, 0.3);
  position: relative;
  overflow: hidden;
}

.btn-example::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.btn-example:hover::before {
  width: 300px;
  height: 300px;
}

.btn-example:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 6px 20px rgba(81, 207, 102, 0.5);
}

.btn-example:active {
  transform: translateY(-1px) scale(1.02);
}

.btn-example i {
  margin-right: 8px;
  animation: book-flip 2s ease-in-out infinite;
}

@keyframes book-flip {
  0%, 100% { transform: rotateY(0deg); }
  50% { transform: rotateY(180deg); }
}

.advanced-options {
  margin-top: 15px;
  border-top: 2px solid #e0e0e0;
  padding-top: 15px;
}

.toggle-advanced {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.toggle-advanced:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.toggle-advanced i {
  transition: transform 0.3s ease;
}

.toggle-advanced.active i {
  transform: rotate(180deg);
}

.advanced-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.advanced-content.show {
  max-height: 200px;
  margin-top: 15px;
}

@media (max-width: 768px) {
  .language-selector {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
  .header h1 { font-size: 1.8em; }
  .score-number { font-size: 3em; }
}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1><i class="fas fa-code"></i> Code Quality Analyzer</h1>
    <p><i class="fas fa-globe"></i> Supporting 40+ Programming Languages with AI-Powered Insights</p>
  </div>
  
  <div class="content">
    {% if error %}
    <div class="error">⚠️ {{ error }}</div>
    {% endif %}
    
    <form method="post" id="analyzeForm">
      <div class="form-group">
        <label><i class="fas fa-laptop-code"></i> Select Programming Language:</label>
        <div class="language-selector">
          <div class="language-option">
            <input type="radio" name="lang" value="python" id="lang-python" {% if not request.form.get('lang') or request.form.get('lang') == 'python' %}checked{% endif %}>
            <label for="lang-python"><i class="fab fa-python"></i> Python</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="javascript" id="lang-js" {% if request.form.get('lang') == 'javascript' %}checked{% endif %}>
            <label for="lang-js"><i class="fab fa-js"></i> JavaScript</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="typescript" id="lang-ts" {% if request.form.get('lang') == 'typescript' %}checked{% endif %}>
            <label for="lang-ts"><i class="fas fa-file-code"></i> TypeScript</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="java" id="lang-java" {% if request.form.get('lang') == 'java' %}checked{% endif %}>
            <label for="lang-java"><i class="fab fa-java"></i> Java</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="cpp" id="lang-cpp" {% if request.form.get('lang') == 'cpp' %}checked{% endif %}>
            <label for="lang-cpp"><i class="fas fa-copyright"></i> C/C++</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="csharp" id="lang-csharp" {% if request.form.get('lang') == 'csharp' %}checked{% endif %}>
            <label for="lang-csharp"><i class="fas fa-hashtag"></i> C#</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="go" id="lang-go" {% if request.form.get('lang') == 'go' %}checked{% endif %}>
            <label for="lang-go"><i class="fas fa-cubes"></i> Go</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="rust" id="lang-rust" {% if request.form.get('lang') == 'rust' %}checked{% endif %}>
            <label for="lang-rust"><i class="fas fa-gear"></i> Rust</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="ruby" id="lang-ruby" {% if request.form.get('lang') == 'ruby' %}checked{% endif %}>
            <label for="lang-ruby"><i class="far fa-gem"></i> Ruby</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="php" id="lang-php" {% if request.form.get('lang') == 'php' %}checked{% endif %}>
            <label for="lang-php"><i class="fab fa-php"></i> PHP</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="swift" id="lang-swift" {% if request.form.get('lang') == 'swift' %}checked{% endif %}>
            <label for="lang-swift"><i class="fab fa-swift"></i> Swift</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="kotlin" id="lang-kotlin" {% if request.form.get('lang') == 'kotlin' %}checked{% endif %}>
            <label for="lang-kotlin"><i class="fas fa-k"></i> Kotlin</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="scala" id="lang-scala" {% if request.form.get('lang') == 'scala' %}checked{% endif %}>
            <label for="lang-scala"><i class="fas fa-s"></i> Scala</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="perl" id="lang-perl" {% if request.form.get('lang') == 'perl' %}checked{% endif %}>
            <label for="lang-perl"><i class="fas fa-file-code"></i> Perl</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="r" id="lang-r" {% if request.form.get('lang') == 'r' %}checked{% endif %}>
            <label for="lang-r"><i class="fab fa-r-project"></i> R</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="matlab" id="lang-matlab" {% if request.form.get('lang') == 'matlab' %}checked{% endif %}>
            <label for="lang-matlab"><i class="fas fa-calculator"></i> MATLAB</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="dart" id="lang-dart" {% if request.form.get('lang') == 'dart' %}checked{% endif %}>
            <label for="lang-dart"><i class="fas fa-d"></i> Dart</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="elixir" id="lang-elixir" {% if request.form.get('lang') == 'elixir' %}checked{% endif %}>
            <label for="lang-elixir"><i class="fas fa-flask"></i> Elixir</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="haskell" id="lang-haskell" {% if request.form.get('lang') == 'haskell' %}checked{% endif %}>
            <label for="lang-haskell"><i class="fas fa-h"></i> Haskell</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="lua" id="lang-lua" {% if request.form.get('lang') == 'lua' %}checked{% endif %}>
            <label for="lang-lua"><i class="fas fa-moon"></i> Lua</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="shell" id="lang-shell" {% if request.form.get('lang') == 'shell' %}checked{% endif %}>
            <label for="lang-shell"><i class="fas fa-terminal"></i> Shell</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="powershell" id="lang-powershell" {% if request.form.get('lang') == 'powershell' %}checked{% endif %}>
            <label for="lang-powershell"><i class="fas fa-terminal"></i> PowerShell</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="sql" id="lang-sql" {% if request.form.get('lang') == 'sql' %}checked{% endif %}>
            <label for="lang-sql"><i class="fas fa-database"></i> SQL</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="html" id="lang-html" {% if request.form.get('lang') == 'html' %}checked{% endif %}>
            <label for="lang-html"><i class="fab fa-html5"></i> HTML</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="css" id="lang-css" {% if request.form.get('lang') == 'css' %}checked{% endif %}>
            <label for="lang-css"><i class="fab fa-css3"></i> CSS</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="xml" id="lang-xml" {% if request.form.get('lang') == 'xml' %}checked{% endif %}>
            <label for="lang-xml"><i class="fas fa-code"></i> XML</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="yaml" id="lang-yaml" {% if request.form.get('lang') == 'yaml' %}checked{% endif %}>
            <label for="lang-yaml"><i class="fas fa-file-code"></i> YAML</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="json" id="lang-json" {% if request.form.get('lang') == 'json' %}checked{% endif %}>
            <label for="lang-json"><i class="fas fa-brackets-curly"></i> JSON</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="markdown" id="lang-markdown" {% if request.form.get('lang') == 'markdown' %}checked{% endif %}>
            <label for="lang-markdown"><i class="fab fa-markdown"></i> Markdown</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="clojure" id="lang-clojure" {% if request.form.get('lang') == 'clojure' %}checked{% endif %}>
            <label for="lang-clojure"><i class="fas fa-copyright"></i> Clojure</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="erlang" id="lang-erlang" {% if request.form.get('lang') == 'erlang' %}checked{% endif %}>
            <label for="lang-erlang"><i class="fas fa-e"></i> Erlang</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="fsharp" id="lang-fsharp" {% if request.form.get('lang') == 'fsharp' %}checked{% endif %}>
            <label for="lang-fsharp"><i class="fas fa-hashtag"></i> F#</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="groovy" id="lang-groovy" {% if request.form.get('lang') == 'groovy' %}checked{% endif %}>
            <label for="lang-groovy"><i class="fas fa-g"></i> Groovy</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="julia" id="lang-julia" {% if request.form.get('lang') == 'julia' %}checked{% endif %}>
            <label for="lang-julia"><i class="fas fa-j"></i> Julia</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="objectivec" id="lang-objectivec" {% if request.form.get('lang') == 'objectivec' %}checked{% endif %}>
            <label for="lang-objectivec"><i class="fab fa-apple"></i> Objective-C</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="vb" id="lang-vb" {% if request.form.get('lang') == 'vb' %}checked{% endif %}>
            <label for="lang-vb"><i class="fas fa-v"></i> Visual Basic</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="assembly" id="lang-assembly" {% if request.form.get('lang') == 'assembly' %}checked{% endif %}>
            <label for="lang-assembly"><i class="fas fa-microchip"></i> Assembly</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="fortran" id="lang-fortran" {% if request.form.get('lang') == 'fortran' %}checked{% endif %}>
            <label for="lang-fortran"><i class="fas fa-f"></i> Fortran</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="cobol" id="lang-cobol" {% if request.form.get('lang') == 'cobol' %}checked{% endif %}>
            <label for="lang-cobol"><i class="fas fa-cubes"></i> COBOL</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="pascal" id="lang-pascal" {% if request.form.get('lang') == 'pascal' %}checked{% endif %}>
            <label for="lang-pascal"><i class="fas fa-p"></i> Pascal</label>
          </div>
          <div class="language-option">
            <input type="radio" name="lang" value="solidity" id="lang-solidity" {% if request.form.get('lang') == 'solidity' %}checked{% endif %}>
            <label for="lang-solidity"><i class="fab fa-ethereum"></i> Solidity</label>
          </div>
        </div>
      </div>
      
      <div class="form-group">
        <label><i class="fas fa-code"></i> Enter Your Code:</label>
        <div style="margin-bottom: 10px;">
          <button type="button" class="btn-example" onclick="loadExample()"><i class="fas fa-book"></i> Load Example Code</button>
        </div>
        <textarea name="code" id="codeTextarea" rows="18" placeholder="Paste your code here for analysis...">{{ request.form.get('code', '') }}</textarea>
      </div>
      
      <div class="advanced-options">
        <button type="button" class="toggle-advanced" onclick="toggleAdvanced()">
          <i class="fas fa-cog"></i> Advanced Options
          <i class="fas fa-chevron-down"></i>
        </button>
        <div class="advanced-content" id="advancedContent">
          <div class="form-group">
            <label><i class="fas fa-robot"></i> ML Model Path (Optional):</label>
            <input type="text" name="model" value="{{ request.form.get('model', 'models/code_quality_model.joblib') }}" placeholder="Path to ML model file">
          </div>
        </div>
      </div>
      
      <button type="submit" class="btn-analyze"><i class="fas fa-rocket"></i> Analyze Code</button>
    </form>
    
    <div class="loading" id="loading">
      <div class="spinner"></div>
      <p>Analyzing your code...</p>
    </div>
    
    {% if analysis %}
    <div class="results">
      <div class="score-card">
        <h2><i class="fas fa-chart-line"></i> Overall Quality Score</h2>
        <div class="score-number">{{ analysis.quality_score }}<span style="font-size: 0.5em;">/100</span></div>
        {% if analysis.quality_score >= 80 %}
        <span class="badge badge-good">Excellent</span>
        {% elif analysis.quality_score >= 60 %}
        <span class="badge badge-warning">Good</span>
        {% else %}
        <span class="badge badge-bad">Needs Improvement</span>
        {% endif %}
      </div>
      
      <div class="section">
        <h3><i class="fas fa-bug"></i> Code Smells Detected ({{ analysis.smells|length }})</h3>
        {% if analysis.smells %}
        {% for s in analysis.smells %}
        <div class="smell-item">
          <div class="smell-kind">{{ s.kind }}</div>
          <div>{{ s.message }}</div>
          {% if s.lineno %}<small style="color: #888;">Line {{ s.lineno }}</small>{% endif %}
        </div>
        {% endfor %}
        {% else %}
        <div class="no-issues">✨ No code smells detected! Your code looks clean! ✨</div>
        {% endif %}
      </div>
      
      {% if analysis.suggestions %}
      <div class="section">
        <h3><i class="fas fa-lightbulb"></i> Improvement Suggestions</h3>
        {% for s in analysis.suggestions %}
        <div class="suggestion-item">
          <strong>{{ s.smell.kind }}:</strong>
          <ul style="margin: 10px 0 0 20px;">
          {% for sug in s.suggestions %}
            <li>{{ sug }}</li>
          {% endfor %}
          </ul>
        </div>
        {% endfor %}
      </div>
      {% endif %}
      
      {% if analysis.ml_classification %}
      <div class="ml-card">
        <h3><i class="fas fa-brain"></i> AI Classification</h3>
        {% if analysis.ml_classification.error %}
        <p>⚠️ {{ analysis.ml_classification.error }}</p>
        {% else %}
        <p><strong>Prediction:</strong> {{ analysis.ml_classification.label|upper }}</p>
        <p><strong>Confidence:</strong> {{ '%.1f'|format(analysis.ml_classification.confidence * 100) }}%</p>
        {% endif %}
      </div>
      {% endif %}
    </div>
    {% endif %}
  </div>
</div>

<script>
function toggleAdvanced() {
  const content = document.getElementById('advancedContent');
  const button = document.querySelector('.toggle-advanced');
  content.classList.toggle('show');
  button.classList.toggle('active');
}

// Example code snippets for each language
const examples = {
  python: `# Example: Poor Python code with multiple issues
def calculate(x,y,z):
    a=x+y
    b=a*z
    c=b/2
    d=c-10
    e=d+5
    f=e*3
    return f

class MyClass:
    def __init__(self):
        self.data=[]
    
    def process(self,item):
        self.data.append(item)
        return len(self.data)

# Global variable
counter = 0

def increment():
    global counter
    counter = counter + 1
    return counter`,

  javascript: `// Example: Poor JavaScript code with issues
function processData(arr) {
  var result = [];
  for (var i = 0; i < arr.length; i++) {
    var item = arr[i];
    if (item != null) {
      result.push(item * 2);
    }
  }
  return result;
}

// Unused variable
var unused = 'test';

// Long parameter list
function createUser(name, email, age, address, phone, city, country) {
  return {
    name: name,
    email: email,
    age: age,
    address: address
  };
}

// Complex nested code
function validate(data) {
  if (data) {
    if (data.user) {
      if (data.user.name) {
        return true;
      }
    }
  }
  return false;
}`,

  typescript: `// Example: TypeScript code with issues
interface User {
  name: string;
  email: string;
}

function processUser(user: any): any {
  const result: any = {};
  result.name = user.name;
  result.email = user.email;
  return result;
}

class DataProcessor {
  private data: any[] = [];
  
  add(item: any): void {
    this.data.push(item);
  }
  
  process(): any {
    let result: any = [];
    for (let i = 0; i < this.data.length; i++) {
      result.push(this.data[i]);
    }
    return result;
  }
}`,

  java: `// Example: Java code with issues
public class Calculator {
    private int a, b, c, d, e, f;
    
    public int calculate(int x, int y, int z) {
        a = x + y;
        b = a * z;
        c = b / 2;
        d = c - 10;
        e = d + 5;
        f = e * 3;
        return f;
    }
    
    public void processData(int[] data) {
        for (int i = 0; i < data.length; i++) {
            System.out.println(data[i]);
        }
    }
}

class UserManager {
    public String createUser(String name, String email, 
                           int age, String address, 
                           String phone, String city) {
        return name + email + age;
    }
}`,

  cpp: `// Example: C++ code with issues
#include <iostream>
using namespace std;

int global_counter = 0;

class DataProcessor {
public:
    int* data;
    int size;
    
    void process(int x, int y, int z) {
        int a = x + y;
        int b = a * z;
        int c = b / 2;
        cout << c << endl;
    }
    
    void allocate(int n) {
        data = new int[n];
        size = n;
    }
};

int calculate(int a, int b, int c, int d, int e) {
    return a + b + c + d + e;
}`,

  go: `// Example: Go code with issues
package main

import "fmt"

var GlobalCounter int = 0

func ProcessData(x int, y int, z int, a int, b int) int {
    result := x + y
    result = result * z
    result = result + a
    result = result - b
    return result
}

type DataProcessor struct {
    data []int
}

func (d *DataProcessor) Add(item int) {
    d.data = append(d.data, item)
}

func main() {
    var unused string = "test"
    fmt.Println(ProcessData(1, 2, 3, 4, 5))
}`,

  rust: `// Example: Rust code with issues
fn process_data(x: i32, y: i32, z: i32) -> i32 {
    let a = x + y;
    let b = a * z;
    let c = b / 2;
    let d = c - 10;
    let e = d + 5;
    let f = e * 3;
    f
}

struct DataProcessor {
    data: Vec<i32>,
}

impl DataProcessor {
    fn new() -> DataProcessor {
        DataProcessor { data: Vec::new() }
    }
    
    fn add(&mut self, item: i32) {
        self.data.push(item);
    }
}

fn main() {
    let _unused = "test";
    let result = process_data(1, 2, 3);
    println!("{}", result);
}`,

  ruby: `# Example: Ruby code with issues
def process_data(x, y, z, a, b)
  result = x + y
  result = result * z
  result = result + a
  result = result - b
  result
end

class DataProcessor
  def initialize
    @data = []
  end
  
  def add(item)
    @data.push(item)
  end
  
  def process
    result = []
    for i in 0..@data.length-1
      result.push(@data[i] * 2)
    end
    result
  end
end

$global_counter = 0

def increment
  $global_counter = $global_counter + 1
end`,

  php: `<?php
// Example: PHP code with issues
function processData($x, $y, $z, $a, $b) {
    $result = $x + $y;
    $result = $result * $z;
    $result = $result + $a;
    $result = $result - $b;
    return $result;
}

class DataProcessor {
    private $data = array();
    
    public function add($item) {
        array_push($this->data, $item);
    }
    
    public function process() {
        $result = array();
        for ($i = 0; $i < count($this->data); $i++) {
            $result[] = $this->data[$i] * 2;
        }
        return $result;
    }
}

$global_counter = 0;

function increment() {
    global $global_counter;
    $global_counter = $global_counter + 1;
    return $global_counter;
}
?>`
};

function loadExample() {
  const selectedLang = document.querySelector('input[name="lang"]:checked').value;
  const codeTextarea = document.getElementById('codeTextarea');
  
  if (examples[selectedLang]) {
    codeTextarea.value = examples[selectedLang];
    codeTextarea.scrollTop = 0;
  }
}

document.getElementById('analyzeForm').addEventListener('submit', function() {
  document.getElementById('loading').style.display = 'block';
});
</script>
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
