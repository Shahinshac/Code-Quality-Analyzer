from flask import Flask, request, render_template_string, jsonify
import os
from dotenv import load_dotenv
from .detectors import RuleBasedDetector
from .suggestion_engine import suggestions_for_smells
from .ml_classifier import predict_code_quality, compute_quality_score
from .auto_fixer import CodeAutoFixer
from .complexity_analyzer import ComplexityAnalyzer
from .security_scanner import SecurityScanner
from .quality_scorer import QualityScorer

# Load environment variables from .env file
load_dotenv()

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
<title>Code Quality Analyzer - 40+ Programming Languages</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
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

.file-upload-zone {
  border: 3px dashed var(--border-color);
  border-radius: 15px;
  padding: 40px 20px;
  text-align: center;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  cursor: pointer;
  background: var(--input-bg);
}

.file-upload-zone:hover,
.file-upload-zone.drag-over {
  border-color: var(--primary-color);
  background: rgba(102, 126, 234, 0.05);
  transform: scale(1.02);
}

.file-upload-zone i {
  font-size: 3em;
  color: var(--primary-color);
  margin-bottom: 15px;
  display: block;
}

.file-upload-zone p {
  color: var(--text-color);
  margin: 10px 0;
}

.file-upload-zone input[type="file"] {
  display: none;
}

.code-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.btn-action {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-action i {
  font-size: 1em;
}

.char-counter {
  text-align: right;
  font-size: 0.85em;
  color: var(--text-color);
  opacity: 0.7;
  margin-top: 5px;
}

.export-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.btn-export {
  background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-export:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(81, 207, 102, 0.4);
}

.toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: var(--success-color);
  color: white;
  padding: 15px 25px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  display: none;
  align-items: center;
  gap: 10px;
  z-index: 1000;
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.toast.show {
  display: flex;
}

.code-preview {
  background: #1e1e1e;
  border-radius: 10px;
  padding: 15px;
  margin: 15px 0;
  overflow-x: auto;
}

.code-preview pre {
  margin: 0;
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9em;
  line-height: 1.5;
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
  <div class="header">
    <h1><i class="fas fa-code"></i> Code Quality Analyzer</h1>
    <p><i class="fas fa-brain"></i> AI-Powered Static Code Analysis</p>
  </div>
  
  <div class="content">
    {% if error %}
    <div class="error">⚠️ {{ error }}</div>
    {% endif %}
    
    <form method="post" id="analyzeForm" onsubmit="return validateForm()">
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
        
        <div class="file-upload-zone" id="fileUploadZone" onclick="document.getElementById('fileInput').click()">
          <i class="fas fa-cloud-upload-alt"></i>
          <p><strong>Drop a file here or click to upload</strong></p>
          <p style="font-size: 0.9em; opacity: 0.8;">
            <span style="display: inline-block; padding: 4px 8px; background: #10b981; color: white; border-radius: 4px; font-size: 0.85em; margin-right: 8px;">🟢 Python: Full Support</span>
            <span style="display: inline-block; padding: 4px 8px; background: #f59e0b; color: white; border-radius: 4px; font-size: 0.85em; margin-right: 8px;">🟡 JS/Java/C++: Partial</span>
            <span style="display: inline-block; padding: 4px 8px; background: #6b7280; color: white; border-radius: 4px; font-size: 0.85em;">⚪ Others: Basic</span>
          </p>
          <input type="file" id="fileInput" accept=".py,.js,.ts,.java,.cpp,.c,.h,.hpp,.go,.rs,.rb,.php,.swift,.kt,.scala,.pl,.r,.m,.dart,.ex,.hs,.lua,.sh,.ps1,.sql,.html,.css,.xml,.yaml,.yml,.json,.md,.clj,.erl,.fs,.groovy,.jl,.vb,.asm,.f,.f90,.cob,.pas,.sol">
        </div>
        
        <textarea name="code" id="codeTextarea" rows="18" placeholder="Paste your code here for analysis...">{{ request.form.get('code', '') }}</textarea>
        <div class="char-counter" id="charCounter">0 characters</div>
      </div>
      
      <div class="advanced-options" style="margin: 20px 0; padding: 15px; background: var(--input-bg); border-radius: 10px; border: 1px solid var(--border-color);">
        <h4 style="margin-bottom: 10px; font-size: 1em;"><i class="fas fa-sliders-h"></i> Advanced Analysis</h4>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
          <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" name="autofix" value="true" id="autofixCheck" style="width: 18px; height: 18px; cursor: pointer;">
            <span><i class="fas fa-magic"></i> Auto-Fix Code</span>
          </label>
          <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" name="security" value="true" id="securityCheck" style="width: 18px; height: 18px; cursor: pointer;">
            <span><i class="fas fa-shield-alt"></i> Security Scan</span>
          </label>
        </div>
        <p style="margin-top: 8px; font-size: 0.85em; opacity: 0.7;">
          <i class="fas fa-rocket"></i> <strong>Advanced features (Auto-Fix, Complexity, Security):</strong> 
          <span style="color: #10b981;">✓ Python (Full Support)</span> | 
          <span style="color: #f59e0b;">⚠ Other languages (Coming Soon)</span>
        </p>
      </div>
      
      <div style="display: flex; gap: 10px; flex-wrap: wrap;">
        <button type="submit" class="btn-analyze" style="flex: 1; min-width: 200px;"><i class="fas fa-rocket"></i> Analyze Code</button>
        <button type="button" class="btn-action" onclick="clearCode()" style="padding: 15px 30px; background: #ff6b6b; color: white; border: none; border-radius: 10px; font-size: 1.1em; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(255,107,107,0.3);">
          <i class="fas fa-trash-alt"></i> Clear Code
        </button>
      </div>
    </form>
    
    <div class="loading" id="loading">
      <div class="spinner"></div>
      <p>Analyzing your code...</p>
    </div>
    
    {% if analysis %}
    <div class="results">
      <div class="export-buttons">
        <button class="btn-export" onclick="copyResults()">
          <i class="fas fa-copy"></i> Copy Results
        </button>
        <button class="btn-export" onclick="exportJSON()">
          <i class="fas fa-download"></i> Export JSON
        </button>
        <button class="btn-export" onclick="exportPDF()">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
      </div>
      
      <div class="score-card">
        <h2><i class="fas fa-chart-line"></i> Quality Score</h2>
        <div class="score-number">{{ analysis.quality_score }}<span style="font-size: 0.5em;">/100</span></div>
        {% if analysis.quality_details %}
        <span class="badge badge-{{ analysis.quality_details.grade|lower }}">Grade: {{ analysis.quality_details.grade }}</span>
        {% elif analysis.quality_score >= 80 %}
        <span class="badge badge-good">Excellent</span>
        {% elif analysis.quality_score >= 60 %}
        <span class="badge badge-warning">Good</span>
        {% else %}
        <span class="badge badge-bad">Needs Improvement</span>
        {% endif %}
        
        {% if analysis.quality_details and analysis.quality_details.components %}
        <div style="margin-top: 20px; text-align: left;">
          <h4 style="font-size: 1em; margin-bottom: 10px;">Score Breakdown:</h4>
          {% for name, comp in analysis.quality_details.components.items() %}
          <div style="margin: 8px 0; padding: 8px; background: rgba(0,0,0,0.1); border-radius: 5px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="text-transform: capitalize;">{{ name }}</span>
              <span style="font-weight: bold;">{{ comp.score }}/100</span>
            </div>
            <div style="width: 100%; height: 6px; background: rgba(0,0,0,0.2); border-radius: 3px; margin-top: 5px; overflow: hidden;">
              <div style="width: {{ comp.score }}%; height: 100%; background: {% if comp.score >= 80 %}#51cf66{% elif comp.score >= 60 %}#ffa500{% else %}#ff6b6b{% endif %}; transition: width 0.5s;"></div>
            </div>
          </div>
          {% endfor %}
        </div>
        {% endif %}
        
        {% if analysis.quality_details and analysis.quality_details.recommendations %}
        <div style="margin-top: 15px; text-align: left;">
          <h4 style="font-size: 0.9em; margin-bottom: 8px;">Recommendations:</h4>
          {% for rec in analysis.quality_details.recommendations %}
          <div style="margin: 5px 0; font-size: 0.85em; opacity: 0.9;">{{ rec }}</div>
          {% endfor %}
        </div>
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
      
      {% if analysis.complexity %}
      <div class="section">
        <h3><i class="fas fa-project-diagram"></i> Complexity Analysis</h3>
        
        {% if analysis.complexity.error %}
        <div style="padding: 15px; background: rgba(255,107,107,0.1); border-left: 4px solid #ff6b6b; border-radius: 5px;">
          <p><i class="fas fa-exclamation-triangle"></i> <strong>Error:</strong> {{ analysis.complexity.error }}</p>
        </div>
        {% elif analysis.complexity.info %}
        <div style="padding: 15px; background: rgba(245,158,11,0.1); border-left: 4px solid #f59e0b; border-radius: 5px;">
          <p><i class="fas fa-info-circle"></i> {{ analysis.complexity.info }}</p>
        </div>
        {% else %}
        
        {% if analysis.complexity.maintainability %}
        <div style="margin: 15px 0; padding: 15px; background: rgba(102,126,234,0.1); border-left: 4px solid #667eea; border-radius: 5px;">
          <h4 style="margin-bottom: 10px; font-size: 1em;">Maintainability Index</h4>
          <div style="font-size: 2em; font-weight: bold; color: #667eea;">{{ analysis.complexity.maintainability.score }}</div>
          <div>Rank: {{ analysis.complexity.maintainability.rank }} - {{ analysis.complexity.maintainability.classification }}</div>
        </div>
        {% endif %}
        
        {% if analysis.complexity.cyclomatic %}
        <h4 style="margin-top: 20px; margin-bottom: 10px; font-size: 1em;">Cyclomatic Complexity</h4>
        {% for item in analysis.complexity.cyclomatic %}
        <div style="margin: 8px 0; padding: 10px; background: var(--input-bg); border-radius: 5px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span><strong>{{ item.name }}</strong> (Line {{ item.line }})</span>
            <span class="badge badge-{% if item.complexity <= 5 %}good{% elif item.complexity <= 10 %}warning{% else %}bad{% endif %}">
              Complexity: {{ item.complexity }}
            </span>
          </div>
          <div style="font-size: 0.85em; margin-top: 5px; opacity: 0.8;">{{ item.classification }} (Rank: {{ item.rank }})</div>
        </div>
        {% endfor %}
        {% endif %}
        
        {% if analysis.complexity.raw_metrics %}
        <h4 style="margin-top: 20px; margin-bottom: 10px; font-size: 1em;">Code Metrics</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
          <div style="padding: 10px; background: var(--input-bg); border-radius: 5px; text-align: center;">
            <div style="font-size: 1.5em; font-weight: bold;">{{ analysis.complexity.raw_metrics.loc }}</div>
            <div style="font-size: 0.85em; opacity: 0.7;">Lines of Code</div>
          </div>
          <div style="padding: 10px; background: var(--input-bg); border-radius: 5px; text-align: center;">
            <div style="font-size: 1.5em; font-weight: bold;">{{ analysis.complexity.raw_metrics.lloc }}</div>
            <div style="font-size: 0.85em; opacity: 0.7;">Logical LOC</div>
          </div>
          <div style="padding: 10px; background: var(--input-bg); border-radius: 5px; text-align: center;">
            <div style="font-size: 1.5em; font-weight: bold;">{{ analysis.complexity.raw_metrics.comments }}</div>
            <div style="font-size: 0.85em; opacity: 0.7;">Comments</div>
          </div>
        </div>
        {% endif %}
      </div>
      {% endif %}
      {% endif %}
      
      {% if analysis.security %}
      <div class="section">
        <h3><i class="fas fa-shield-alt"></i> Security Analysis</h3>
        
        {% if analysis.security.error %}
        <div style="padding: 15px; background: rgba(255,107,107,0.1); border-left: 4px solid #ff6b6b; border-radius: 5px;">
          <p><i class="fas fa-exclamation-triangle"></i> <strong>Error:</strong> {{ analysis.security.error }}</p>
        </div>
        {% elif analysis.security.info %}
        <div style="padding: 15px; background: rgba(245,158,11,0.1); border-left: 4px solid #f59e0b; border-radius: 5px;">
          <p><i class="fas fa-info-circle"></i> {{ analysis.security.info }}</p>
        </div>
        {% else %}
        
        <div style="margin: 15px 0; padding: 15px; background: {% if analysis.security.score >= 80 %}rgba(81,207,102,0.1){% elif analysis.security.score >= 60 %}rgba(255,165,0,0.1){% else %}rgba(255,107,107,0.1){% endif %}; border-left: 4px solid {% if analysis.security.score >= 80 %}#51cf66{% elif analysis.security.score >= 60 %}#ffa500{% else %}#ff6b6b{% endif %}; border-radius: 5px;">
          <div style="font-size: 2em; font-weight: bold;">Security Score: {{ analysis.security.score }}/100</div>
          <div style="margin-top: 10px;">
            {% if analysis.security.summary %}
            <div>Total Issues: {{ analysis.security.summary.total }}</div>
            {% if analysis.security.summary.high > 0 %}
            <div style="color: #ff6b6b;"><i class="fas fa-exclamation-triangle"></i> High: {{ analysis.security.summary.high }}</div>
            {% endif %}
            {% if analysis.security.summary.medium > 0 %}
            <div style="color: #ffa500;"><i class="fas fa-exclamation-circle"></i> Medium: {{ analysis.security.summary.medium }}</div>
            {% endif %}
            {% if analysis.security.summary.low > 0 %}
            <div style="color: #51cf66;"><i class="fas fa-info-circle"></i> Low: {{ analysis.security.summary.low }}</div>
            {% endif %}
            {% endif %}
          </div>
        </div>
        
        {% if analysis.security.vulnerabilities %}
        <h4 style="margin-top: 20px; margin-bottom: 10px; font-size: 1em;">Vulnerabilities Found:</h4>
        {% for vuln in analysis.security.vulnerabilities %}
        <div style="margin: 10px 0; padding: 12px; background: var(--input-bg); border-left: 4px solid {% if vuln.severity == 'HIGH' %}#ff6b6b{% elif vuln.severity == 'MEDIUM' %}#ffa500{% else %}#51cf66{% endif %}; border-radius: 5px;">
          <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
            <strong>{{ vuln.test_name }}</strong>
            <span class="badge badge-{% if vuln.severity == 'HIGH' %}bad{% elif vuln.severity == 'MEDIUM' %}warning{% else %}good{% endif %}">
              {{ vuln.severity }}
            </span>
          </div>
          <div style="margin: 5px 0; font-size: 0.9em;">{{ vuln.message }}</div>
          {% if vuln.line %}
          <div style="font-size: 0.85em; opacity: 0.7;">Line {{ vuln.line }}</div>
          {% endif %}
          {% if vuln.code %}
          <div style="margin-top: 8px; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 3px; font-family: monospace; font-size: 0.85em; overflow-x: auto;">{{ vuln.code }}</div>
          {% endif %}
        </div>
        {% endfor %}
        {% else %}
        <div class="no-issues">✨ No security vulnerabilities detected! ✨</div>
        {% endif %}
        {% endif %}
      </div>
      {% endif %}
      
      {% if analysis.auto_fix %}
      <div class="section">
        <h3><i class="fas fa-magic"></i> Auto-Fix Report</h3>
        
        {% if analysis.auto_fix.error %}
        <div style="padding: 15px; background: rgba(255,107,107,0.1); border-left: 4px solid #ff6b6b; border-radius: 5px;">
          <p><i class="fas fa-exclamation-triangle"></i> <strong>Error:</strong> {{ analysis.auto_fix.error }}</p>
        </div>
        {% elif analysis.auto_fix.info %}
        <div style="padding: 15px; background: rgba(245,158,11,0.1); border-left: 4px solid #f59e0b; border-radius: 5px;">
          <p><i class="fas fa-info-circle"></i> {{ analysis.auto_fix.info }}</p>
        </div>
        {% elif analysis.auto_fix.fixes %}
        <div style="margin: 15px 0; padding: 15px; background: rgba(81,207,102,0.1); border-left: 4px solid #51cf66; border-radius: 5px;">
          <strong>{{ analysis.auto_fix.fixes|length }} fixes applied automatically!</strong>
        </div>
        
        <h4 style="margin-top: 20px; margin-bottom: 10px; font-size: 1em;">Applied Fixes:</h4>
        {% for fix in analysis.auto_fix.fixes %}
        <div style="margin: 8px 0; padding: 10px; background: var(--input-bg); border-radius: 5px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span><i class="fas fa-check-circle" style="color: #51cf66;"></i> {{ fix.type|upper }}</span>
            {% if fix.line %}<span style="opacity: 0.7;">Line {{ fix.line }}</span>{% endif %}
          </div>
          <div style="margin-top: 5px; font-size: 0.9em;">{{ fix.message }}</div>
        </div>
        {% endfor %}
        
        {% if analysis.auto_fix.fixed_code %}
        <div style="margin-top: 20px;">
          <h4 style="margin-bottom: 10px; font-size: 1em;">
            <i class="fas fa-code"></i> Fixed Code:
            <button type="button" onclick="copyFixedCode()" style="margin-left: 10px; padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 0.85em;">
              <i class="fas fa-copy"></i> Copy
            </button>
          </h4>
          <pre id="fixedCode" style="background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 8px; overflow-x: auto; max-height: 400px;"><code>{{ analysis.auto_fix.fixed_code }}</code></pre>
        </div>
        {% endif %}
        {% else %}
        <div class="no-issues">No automatic fixes available.</div>
        {% endif %}
      </div>
      {% endif %}
    </div>
    {% endif %}
  </div>
</div>

<div class="toast" id="toast">
  <i class="fas fa-check-circle"></i>
  <span id="toastMessage">Success!</span>
</div>

<script>
// Global references to DOM elements
const codeTextarea = document.getElementById('codeTextarea');
const fileInput = document.getElementById('fileInput');
const fileUploadZone = document.getElementById('fileUploadZone');

function copyFixedCode() {
  const codeElement = document.getElementById('fixedCode');
  if (codeElement) {
    const code = codeElement.textContent;
    navigator.clipboard.writeText(code).then(() => {
      showToast('Fixed code copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy:', err);
      showToast('Failed to copy code', 'error');
    });
  }
}

function clearCode() {
  if (codeTextarea) {
    codeTextarea.value = '';
    updateCharCounter();
    showToast('Code cleared');
  }
}

function validateForm() {
  const code = codeTextarea ? codeTextarea.value.trim() : '';
  
  if (!code) {
    showToast('Please enter some code to analyze', 'error');
    return false;
  }
  
  // Show loading indicator
  const loading = document.getElementById('loading');
  if (loading) {
    loading.style.display = 'block';
  }
  
  return true;
}

// File upload handling
if (fileInput && fileUploadZone && codeTextarea) {
  fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(event) {
        codeTextarea.value = event.target.result;
        updateCharCounter();
        showToast('Loaded ' + file.name);
        
        // Auto-detect language from file extension
        const ext = file.name.split('.').pop().toLowerCase();
        const langMap = {
          'py': 'python', 'js': 'javascript', 'ts': 'typescript',
          'java': 'java', 'cpp': 'cpp', 'c': 'c', 'h': 'c', 'hpp': 'cpp',
          'go': 'go', 'rs': 'rust', 'rb': 'ruby', 'php': 'php',
          'swift': 'swift', 'kt': 'kotlin', 'scala': 'scala',
          'pl': 'perl', 'r': 'r', 'm': 'matlab', 'dart': 'dart',
          'ex': 'elixir', 'hs': 'haskell', 'lua': 'lua',
          'sh': 'shell', 'ps1': 'powershell', 'sql': 'sql',
          'html': 'html', 'css': 'css', 'xml': 'xml',
          'yaml': 'yaml', 'yml': 'yaml', 'json': 'json', 'md': 'markdown'
        };
        
        const langSelector = document.getElementById('langSelect');
        if (langMap[ext] && langSelector) {
          langSelector.value = langMap[ext];
        }
      };
      reader.readAsText(file);
    }
  });

  // Drag and drop
  fileUploadZone.addEventListener('dragover', function(e) {
    e.preventDefault();
    e.stopPropagation();
    fileUploadZone.classList.add('drag-over');
  });

  fileUploadZone.addEventListener('dragleave', function(e) {
    e.preventDefault();
    e.stopPropagation();
    fileUploadZone.classList.remove('drag-over');
  });

  fileUploadZone.addEventListener('drop', function(e) {
    e.preventDefault();
    e.stopPropagation();
    fileUploadZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      fileInput.dispatchEvent(new Event('change'));
    }
  });
}

// Character counter
function updateCharCounter() {
  if (codeTextarea) {
    const count = codeTextarea.value.length;
    const counter = document.getElementById('charCounter');
    if (counter) {
      counter.textContent = count.toLocaleString() + ' characters';
    }
  }
}

if (codeTextarea) {
  codeTextarea.addEventListener('input', updateCharCounter);
}

// Code templates by language
const codeTemplates = {
  python: 'def calculate_sum(numbers):\\n    \\\"\\\"\\\"Calculate the sum of a list of numbers.\\\"\\\"\\\"\\n    total = 0\\n    for num in numbers:\\n        total += num\\n    return total\\n\\n# Example usage\\nresult = calculate_sum([1, 2, 3, 4, 5])\\nprint(f\\\"Sum: {result}\\\")',
  
  javascript: 'function calculateSum(numbers) {\\n  // Calculate the sum of an array of numbers\\n  let total = 0;\\n  for (const num of numbers) {\\n    total += num;\\n  }\\n  return total;\\n}\\n\\n// Example usage\\nconst result = calculateSum([1, 2, 3, 4, 5]);\\nconsole.log(`Sum: ${result}`);',
  
  java: 'public class Calculator {\\n    public static int calculateSum(int[] numbers) {\\n        int total = 0;\\n        for (int num : numbers) {\\n            total += num;\\n        }\\n        return total;\\n    }\\n    \\n    public static void main(String[] args) {\\n        int[] nums = {1, 2, 3, 4, 5};\\n        int result = calculateSum(nums);\\n        System.out.println(\\\"Sum: \\\" + result);\\n    }\\n}',
  
  cpp: '#include <iostream>\\n#include <vector>\\n\\nint calculateSum(const std::vector<int>& numbers) {\\n    int total = 0;\\n    for (int num : numbers) {\\n        total += num;\\n    }\\n    return total;\\n}\\n\\nint main() {\\n    std::vector<int> nums = {1, 2, 3, 4, 5};\\n    int result = calculateSum(nums);\\n    std::cout << \\\"Sum: \\\" << result << std::endl;\\n    return 0;\\n}',
  
  go: 'package main\\n\\nimport \\\"fmt\\\"\\n\\nfunc calculateSum(numbers []int) int {\\n    total := 0\\n    for _, num := range numbers {\\n        total += num\\n    }\\n    return total\\n}\\n\\nfunc main() {\\n    nums := []int{1, 2, 3, 4, 5}\\n    result := calculateSum(nums)\\n    fmt.Printf(\\\"Sum: %d\\\\n\\\", result)\\n}',
  
  typescript: 'function calculateSum(numbers: number[]): number {\\n  let total: number = 0;\\n  for (const num of numbers) {\\n    total += num;\\n  }\\n  return total;\\n}\\n\\n// Example usage\\nconst result: number = calculateSum([1, 2, 3, 4, 5]);\\nconsole.log(`Sum: ${result}`);',
  
  ruby: 'def calculate_sum(numbers)\\n  total = 0\\n  numbers.each do |num|\\n    total += num\\n  end\\n  total\\nend\\n\\n# Example usage\\nresult = calculate_sum([1, 2, 3, 4, 5])\\nputs \\\"Sum: #{result}\\\"',
  
  php: '<?php\\nfunction calculateSum($numbers) {\\n    $total = 0;\\n    foreach ($numbers as $num) {\\n        $total += $num;\\n    }\\n    return $total;\\n}\\n\\n// Example usage\\n$result = calculateSum([1, 2, 3, 4, 5]);\\necho \\\"Sum: \\\" . $result . \\\"\\\\n\\\";\\n?>',
  
  rust: 'fn calculate_sum(numbers: &[i32]) -> i32 {\\n    let mut total = 0;\\n    for num in numbers {\\n        total += num;\\n    }\\n    total\\n}\\n\\nfn main() {\\n    let nums = vec![1, 2, 3, 4, 5];\\n    let result = calculate_sum(&nums);\\n    println!(\\\"Sum: {}\\\", result);\\n}',
  
  swift: 'func calculateSum(numbers: [Int]) -> Int {\\n    var total = 0\\n    for num in numbers {\\n        total += num\\n    }\\n    return total\\n}\\n\\n// Example usage\\nlet result = calculateSum(numbers: [1, 2, 3, 4, 5])\\nprint(\\\"Sum: \\\\(result)\\\")',
  
  csharp: 'using System;\\nusing System.Linq;\\n\\nclass Calculator {\\n    static int CalculateSum(int[] numbers) {\\n        int total = 0;\\n        foreach (int num in numbers) {\\n            total += num;\\n        }\\n        return total;\\n    }\\n    \\n    static void Main() {\\n        int[] nums = {1, 2, 3, 4, 5};\\n        int result = CalculateSum(nums);\\n        Console.WriteLine($\\\"Sum: {result}\\\");\\n    }\\n}',
  
  kotlin: 'fun calculateSum(numbers: List<Int>): Int {\\n    var total = 0\\n    for (num in numbers) {\\n        total += num\\n    }\\n    return total\\n}\\n\\nfun main() {\\n    val nums = listOf(1, 2, 3, 4, 5)\\n    val result = calculateSum(nums)\\n    println(\\\"Sum: $result\\\")\\n}',
  
  scala: 'object Calculator {\\n  def calculateSum(numbers: List[Int]): Int = {\\n    var total = 0\\n    for (num <- numbers) {\\n      total += num\\n    }\\n    total\\n  }\\n  \\n  def main(args: Array[String]): Unit = {\\n    val nums = List(1, 2, 3, 4, 5)\\n    val result = calculateSum(nums)\\n    println(s\\\"Sum: $result\\\")\\n  }\\n}',
  
  r: 'calculate_sum <- function(numbers) {\\n  total <- 0\\n  for (num in numbers) {\\n    total <- total + num\\n  }\\n  return(total)\\n}\\n\\n# Example usage\\nresult <- calculate_sum(c(1, 2, 3, 4, 5))\\nprint(paste(\\\"Sum:\\\", result))'
};

// Export functions
function copyResults() {
  const results = document.querySelector('.results');
  if (!results) return;
  
  const text = results.innerText;
  navigator.clipboard.writeText(text).then(() => {
    showToast('Results copied to clipboard!');
  }).catch(err => {
    showToast('Failed to copy', 'error');
  });
}

function exportJSON() {
  const analysisData = {
    timestamp: new Date().toISOString(),
    language: document.getElementById('langSelect')?.value || 'unknown',
    smells: [],
    suggestions: [],
    qualityScore: null,
    mlClassification: null
  };
  
  // Extract data from results
  const smellItems = document.querySelectorAll('.smell-item');
  smellItems.forEach(item => {
    const kind = item.querySelector('.smell-kind')?.textContent;
    const message = item.textContent.replace(kind, '').trim();
    analysisData.smells.push({ kind, message });
  });
  
  const scoreNumber = document.querySelector('.score-number');
  if (scoreNumber) {
    analysisData.qualityScore = parseInt(scoreNumber.textContent);
  }
  
  const blob = new Blob([JSON.stringify(analysisData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'code-analysis-' + Date.now() + '.json';
  a.click();
  URL.revokeObjectURL(url);
  
  showToast('JSON exported successfully!');
}

function exportPDF() {
  try {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Title
    doc.setFontSize(20);
    doc.text('Code Quality Analysis Report', 20, 20);
    
    // Date
    doc.setFontSize(10);
    doc.text('Generated: ' + new Date().toLocaleString(), 20, 30);
    
    // Quality Score
    const scoreNumber = document.querySelector('.score-number');
    if (scoreNumber) {
      doc.setFontSize(16);
      doc.text('Quality Score: ' + scoreNumber.textContent, 20, 45);
    }
    
    // Code Smells
    doc.setFontSize(14);
    doc.text('Code Smells:', 20, 60);
    
    const smellItems = document.querySelectorAll('.smell-item');
    let yPos = 70;
    doc.setFontSize(10);
    
    smellItems.forEach((item, index) => {
      if (yPos > 270) {
        doc.addPage();
        yPos = 20;
      }
      const kind = item.querySelector('.smell-kind')?.textContent || '';
      const message = item.textContent.replace(kind, '').trim();
      doc.text((index + 1) + '. ' + kind + ': ' + message.substring(0, 80), 20, yPos);
      yPos += 10;
    });
    
    doc.save('code-analysis-' + Date.now() + '.pdf');
    showToast('PDF exported successfully!');
  } catch (err) {
    showToast('PDF export failed', 'error');
    console.error('PDF export error:', err);
  }
}

function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  const toastMessage = document.getElementById('toastMessage');
  
  toastMessage.textContent = message;
  toast.style.background = type === 'error' ? 'var(--error-color)' : 'var(--success-color)';
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
  // Ctrl+Enter or Cmd+Enter to submit
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    document.querySelector('form').submit();
  }
  
  // Escape to clear
  if (e.key === 'Escape' && document.activeElement === codeTextarea) {
    clearCode();
  }
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  // Initialize character counter for pre-filled content
  if (codeTextarea && codeTextarea.value) {
    updateCharCounter();
  }
  
  // Highlight code in results if present
  document.querySelectorAll('pre code').forEach((block) => {
    hljs.highlightElement(block);
  });
});

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
                
                lang = request.form.get('lang', 'python')
                enable_autofix = request.form.get('autofix') == 'true'
                enable_security = request.form.get('security') == 'true'
                
                # Try to find model in common locations
                model_path = os.environ.get('MODEL_PATH')
                if not model_path:
                    possible_paths = [
                        'models/code_quality_model.joblib',
                        '../models/code_quality_model.joblib',
                        os.path.join(os.path.dirname(__file__), '..', 'models', 'code_quality_model.joblib'),
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            model_path = path
                            break
                
                # Basic detection
                detector = RuleBasedDetector()
                smells = detector.detect_all_languages(code, lang)
                suggestions = suggestions_for_smells(smells)
                
                # ML Classification
                ml_result = None
                if model_path and os.path.exists(model_path):
                    try:
                        label, prob = predict_code_quality(code, model_path)
                        ml_result = {'label': label, 'confidence': prob}
                    except Exception as e:
                        ml_result = {'error': f'ML prediction failed: {str(e)}'}
                else:
                    if model_path:
                        ml_result = {'error': f'Model file not found: {model_path}'}
                
                # NEW: Complexity Analysis (Python only)
                complexity_data = None
                if lang.lower() == 'python':
                    try:
                        complexity_analyzer = ComplexityAnalyzer()
                        complexity_data = complexity_analyzer.analyze(code)
                    except Exception as e:
                        app.logger.error(f'Complexity analysis error: {e}')
                        complexity_data = {'error': f'Complexity analysis failed: {str(e)}'}
                else:
                    complexity_data = {'info': f'Complexity analysis is currently available for Python only. {lang} support coming soon.'}
                
                # NEW: Security Scan (Python only)
                security_data = None
                if enable_security:
                    if lang.lower() == 'python':
                        try:
                            security_scanner = SecurityScanner()
                            security_data = security_scanner.scan(code)
                        except Exception as e:
                            app.logger.error(f'Security scan error: {e}')
                            security_data = {'error': f'Security scan failed: {str(e)}', 'vulnerabilities': []}
                    else:
                        security_data = {'info': f'Security scanning is currently available for Python only. {lang} support coming soon.', 'vulnerabilities': []}
                
                # NEW: Auto-fix suggestions (Python only)
                fixed_code = None
                auto_fix_report = None
                if enable_autofix:
                    if lang.lower() == 'python':
                        try:
                            auto_fixer = CodeAutoFixer()
                            fixed_code, fixes = auto_fixer.fix_all(code)
                            auto_fix_report = {'fixed_code': fixed_code, 'fixes': fixes}
                        except Exception as e:
                            app.logger.error(f'Auto-fix error: {e}')
                            auto_fix_report = {'error': f'Auto-fix failed: {str(e)}', 'fixes': []}
                    else:
                        auto_fix_report = {'info': f'Auto-fix is currently available for Python only. {lang} support coming soon.', 'fixes': []}
                
                # NEW: Enhanced Quality Score
                quality_scorer = QualityScorer()
                quality_score_data = quality_scorer.calculate_score(
                    smells,
                    complexity_data,
                    security_data,
                    auto_fix_report
                )
                
                analysis = {
                    'smells': [s.to_dict() for s in smells],
                    'suggestions': suggestions,
                    'ml_classification': ml_result,
                    'quality_score': quality_score_data.get('total_score', 75),
                    'quality_details': quality_score_data,
                    'complexity': complexity_data,
                    'security': security_data,
                    'auto_fix': auto_fix_report,
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
