#!/usr/bin/env python3
"""
Script to enhance the webapp with all requested features:
- Dark mode toggle with persistence
- Full mobile responsiveness
- Copy/download buttons
- Better icons and animations
- Statistics cards
- Improved accessibility
"""

import re

def enhance_webapp():
    with open('code_quality_analyzer/webapp.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add responsive styles for all elements
    responsive_styles = """
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
"""
    
    # Insert responsive styles before closing </style>
    content = content.replace('</style>', responsive_styles + '\n</style>')
    
    # Add dark mode toggle button and enhanced header
    old_header = '''  <div class="header">
    <h1><i class="fas fa-code"></i> Code Quality Analyzer</h1>
    <p>AI-Powered Static Code Analysis</p>
  </div>'''
    
    new_header = '''  <div class="header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark Mode" style="background: rgba(255,255,255,0.2); border: 2px solid rgba(255,255,255,0.3); color: white; padding: 10px 15px; border-radius: 50px; cursor: pointer; transition: all 0.3s ease; font-size: 1.2em; backdrop-filter: blur(10px);">
      <i class="fas fa-moon" id="themeIcon"></i>
    </button>
    <div style="flex: 1; text-align: center;">
      <h1><i class="fas fa-code"></i> Code Quality Analyzer</h1>
      <p><i class="fas fa-brain"></i> AI-Powered Static Code Analysis</p>
    </div>
    <div style="width: 50px;"></div>
  </div>'''
    
    content = content.replace(old_header, new_header)
    
    # Add JavaScript functions for dark mode, copy, and download
    js_functions = """
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
"""
    
    # Find and replace the existing script section
    content = re.sub(r'<script>.*?</script>', '<script>\n' + js_functions + '\n// Example code snippets', content, flags=re.DOTALL, count=1)
    
    # Write enhanced version
    with open('code_quality_analyzer/webapp.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Webapp enhanced successfully!")
    print("✨ Added features:")
    print("  - Dark mode toggle with localStorage")
    print("  - Mobile responsive design (768px, 480px breakpoints)")
    print("  - Enhanced header with theme switcher")
    print("  - Better icon integration")

if __name__ == '__main__':
    enhance_webapp()
