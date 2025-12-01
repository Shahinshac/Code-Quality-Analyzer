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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
<title>Code Quality Analyzer - 40+ Programming Languages</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --success-color: #51cf66;
  --error-color: #ff6b6b;
  --warning-color: #ffa500;
  --bg-color: #ffffff;
  --text-color: #333333;
  --card-bg: #ffffff;
  --input-bg: #f9f9f9;
  --border-color: #ddd;
}

.dark-mode {
  --bg-color: #1a1a2e;
  --text-color: #eee;
  --card-bg: #16213e;
  --input-bg: #0f3460;
  --border-color: #2a2a40;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  background-attachment: fixed;
  min-height: 100vh;
  padding: 20px;
  transition: all 0.3s ease;
}

@media (max-width: 768px) {
  body {
    padding: 10px;
  }
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  background: var(--card-bg);
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

.language-dropdown {
  width: 100%;
  padding: 15px;
  font-size: 1.1em;
  border: 2px solid #ddd;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  background-image: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.language-dropdown:hover {
  border-color: #667eea;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
  transform: translateY(-2px);
}

.language-dropdown:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
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

@media (max-width: 768px) {
  .header {
    padding: 30px 20px;
    flex-direction: column;
    gap: 15px;
  }
  
  .header h1 {
    font-size: 1.8em;
  }
  
  .header p {
    font-size: 1em;
  }
  
  .content {
    padding: 25px 20px;
  }
  
  .form-group label {
    font-size: 1em;
  }
  
  .language-dropdown {
    padding: 12px;
    font-size: 1em;
  }
  
  textarea {
    padding: 12px;
    font-size: 13px;
  }
  
  .btn-analyze {
    padding: 16px;
    font-size: 1.1em;
  }
  
  .score-number {
    font-size: 3em;
  }
  
  .section {
    padding: 20px 15px;
  }
  
  .section h3 {
    font-size: 1.2em;
  }
}

@media (max-width: 480px) {
  .header h1 {
    font-size: 1.5em;
  }
  
  .header p {
    font-size: 0.9em;
  }
  
  .content {
    padding: 20px 15px;
  }
  
  textarea {
    font-size: 12px;
  }
  
  .btn-analyze {
    padding: 14px;
    font-size: 1em;
  }
  
  .score-number {
    font-size: 2.5em;
  }
  
  .section {
    padding: 15px 12px;
  }
}

</style>
</head>
<body>
<div class="container">
  <div class="header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark Mode" style="background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.3); color: white; padding: 10px 15px; border-radius: 50px; cursor: pointer; transition: all 0.3s ease; font-size: 1.2em; backdrop-filter: blur(10px);">
      <i class="fas fa-moon" id="themeIcon"></i>
    </button>
    <div style="flex: 1; text-align: center;">
      <h1><i class="fas fa-code"></i> Code Quality Analyzer</h1>
      <p><i class="fas fa-brain"></i> AI-Powered Static Code Analysis</p>
    </div>
    <div style="width: 50px;"></div>
  </div>
  
  <div class="content">
    {% if error %}
    <div class="error">⚠️ {{ error }}</div>
    {% endif %}
    
    <form method="post" id="analyzeForm">
      <div class="form-group">
        <label><i class="fas fa-laptop-code"></i> Programming Language</label>
        <select name="lang" id="langSelect" class="language-dropdown">
          <option value="python" {% if not request.form.get('lang') or request.form.get('lang') == 'python' %}selected{% endif %}>🐍 Python</option>
          <option value="javascript" {% if request.form.get('lang') == 'javascript' %}selected{% endif %}>💛 JavaScript</option>
          <option value="typescript" {% if request.form.get('lang') == 'typescript' %}selected{% endif %}>💙 TypeScript</option>
          <option value="java" {% if request.form.get('lang') == 'java' %}selected{% endif %}>☕ Java</option>
          <option value="cpp" {% if request.form.get('lang') == 'cpp' %}selected{% endif %}>⚡ C/C++</option>
          <option value="csharp" {% if request.form.get('lang') == 'csharp' %}selected{% endif %}>🔷 C#</option>
          <option value="go" {% if request.form.get('lang') == 'go' %}selected{% endif %}>🔵 Go</option>
          <option value="rust" {% if request.form.get('lang') == 'rust' %}selected{% endif %}>🦀 Rust</option>
          <option value="ruby" {% if request.form.get('lang') == 'ruby' %}selected{% endif %}>💎 Ruby</option>
          <option value="php" {% if request.form.get('lang') == 'php' %}selected{% endif %}>🐘 PHP</option>
          <option value="swift" {% if request.form.get('lang') == 'swift' %}selected{% endif %}>🍎 Swift</option>
          <option value="kotlin" {% if request.form.get('lang') == 'kotlin' %}selected{% endif %}>🎯 Kotlin</option>
          <option value="scala" {% if request.form.get('lang') == 'scala' %}selected{% endif %}>📊 Scala</option>
          <option value="perl" {% if request.form.get('lang') == 'perl' %}selected{% endif %}>🐪 Perl</option>
          <option value="r" {% if request.form.get('lang') == 'r' %}selected{% endif %}>📈 R</option>
          <option value="matlab" {% if request.form.get('lang') == 'matlab' %}selected{% endif %}>🧮 MATLAB</option>
          <option value="dart" {% if request.form.get('lang') == 'dart' %}selected{% endif %}>🎯 Dart</option>
          <option value="elixir" {% if request.form.get('lang') == 'elixir' %}selected{% endif %}>💧 Elixir</option>
          <option value="haskell" {% if request.form.get('lang') == 'haskell' %}selected{% endif %}>λ Haskell</option>
          <option value="lua" {% if request.form.get('lang') == 'lua' %}selected{% endif %}>🌙 Lua</option>
          <option value="shell" {% if request.form.get('lang') == 'shell' %}selected{% endif %}>🐚 Shell</option>
          <option value="powershell" {% if request.form.get('lang') == 'powershell' %}selected{% endif %}>⚙️ PowerShell</option>
          <option value="sql" {% if request.form.get('lang') == 'sql' %}selected{% endif %}>🗄️ SQL</option>
          <option value="html" {% if request.form.get('lang') == 'html' %}selected{% endif %}>🌐 HTML</option>
          <option value="css" {% if request.form.get('lang') == 'css' %}selected{% endif %}>🎨 CSS</option>
          <option value="xml" {% if request.form.get('lang') == 'xml' %}selected{% endif %}>📋 XML</option>
          <option value="yaml" {% if request.form.get('lang') == 'yaml' %}selected{% endif %}>📄 YAML</option>
          <option value="json" {% if request.form.get('lang') == 'json' %}selected{% endif %}>📦 JSON</option>
          <option value="markdown" {% if request.form.get('lang') == 'markdown' %}selected{% endif %}>📝 Markdown</option>
          <option value="clojure" {% if request.form.get('lang') == 'clojure' %}selected{% endif %}>🔮 Clojure</option>
          <option value="erlang" {% if request.form.get('lang') == 'erlang' %}selected{% endif %}>📡 Erlang</option>
          <option value="fsharp" {% if request.form.get('lang') == 'fsharp' %}selected{% endif %}>🔶 F#</option>
          <option value="groovy" {% if request.form.get('lang') == 'groovy' %}selected{% endif %}>🎵 Groovy</option>
          <option value="julia" {% if request.form.get('lang') == 'julia' %}selected{% endif %}>🔬 Julia</option>
          <option value="objectivec" {% if request.form.get('lang') == 'objectivec' %}selected{% endif %}>🍏 Objective-C</option>
          <option value="vb" {% if request.form.get('lang') == 'vb' %}selected{% endif %}>📘 Visual Basic</option>
          <option value="assembly" {% if request.form.get('lang') == 'assembly' %}selected{% endif %}>⚙️ Assembly</option>
          <option value="fortran" {% if request.form.get('lang') == 'fortran' %}selected{% endif %}>🔢 Fortran</option>
          <option value="cobol" {% if request.form.get('lang') == 'cobol' %}selected{% endif %}>💼 COBOL</option>
          <option value="pascal" {% if request.form.get('lang') == 'pascal' %}selected{% endif %}>🎓 Pascal</option>
          <option value="solidity" {% if request.form.get('lang') == 'solidity' %}selected{% endif %}>⛓️ Solidity</option>
        </select>
      </div>
      
      <div class="form-group">
        <label><i class="fas fa-code"></i> Code</label>
        <div style="margin-bottom: 10px;">
          <button type="button" class="btn-example" onclick="loadExample()"><i class="fas fa-book"></i> Load Example</button>
        </div>
        <textarea name="code" id="codeTextarea" rows="18" placeholder="Paste your code here for analysis...">{{ request.form.get('code', '') }}</textarea>
      </div>
      
      <div class="advanced-options">
        <button type="button" class="toggle-advanced" onclick="toggleAdvanced()">
          <i class="fas fa-cog"></i> Advanced
          <i class="fas fa-chevron-down"></i>
        </button>
        <div class="advanced-content" id="advancedContent">
          <div class="form-group">
            <label><i class="fas fa-robot"></i> ML Model Path</label>
            <input type="text" name="model" value="{{ request.form.get('model', 'models/code_quality_model.joblib') }}" placeholder="Path to ML model file">
          </div>
        </div>
      </div>
      
      <button type="submit" class="btn-analyze"><i class="fas fa-rocket"></i> Analyze</button>
    </form>
    
    <div class="loading" id="loading">
      <div class="spinner"></div>
      <p>Analyzing your code...</p>
    </div>
    
    {% if analysis %}
    <div class="results">
      <div class="score-card">
        <h2><i class="fas fa-chart-line"></i> Quality Score</h2>
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
        <h3><i class="fas fa-bug"></i> Code Smells ({{ analysis.smells|length }})</h3>
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
        <h3><i class="fas fa-lightbulb"></i> Suggestions</h3>
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

function toggleTheme() {
  const html = document.documentElement;
  const icon = document.getElementById('themeIcon');
  
  if (html.classList.contains('dark-mode')) {
    html.classList.remove('dark-mode');
    icon.classList.remove('fa-sun');
    icon.classList.add('fa-moon');
    localStorage.setItem('theme', 'light');
  } else {
    html.classList.add('dark-mode');
    icon.classList.remove('fa-moon');
    icon.classList.add('fa-sun');
    localStorage.setItem('theme', 'dark');
  }
}

// Load saved theme
window.addEventListener('DOMContentLoaded', function() {
  const savedTheme = localStorage.getItem('theme');
  const icon = document.getElementById('themeIcon');
  
  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark-mode');
    if (icon) {
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
    }
  }
});

// Example code snippets
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
