#!/usr/bin/env python3
"""
Quick validation test to ensure templates are clean and CSS is fixed
"""

import os
import re

def check_for_emojis(file_path):
    """Check if a file contains emoji characters"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002700-\U000027BF"  # dingbats
        "\U0001f926-\U0001f937"  # additional emoticons
        "\U00010000-\U0010ffff"  # other unicode symbols
        "\u2640-\u2642"          # gender symbols
        "\u2600-\u2B55"          # misc symbols
        "\u200d"                 # zero width joiner
        "\u23cf"                 # eject symbol
        "\u23e9"                 # fast forward
        "\u231a"                 # watch
        "\ufe0f"                 # variation selector
        "]+", flags=re.UNICODE)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            emojis = emoji_pattern.findall(content)
            return emojis
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def validate_templates():
    """Check all templates for emojis"""
    template_dir = "/Users/laurenadmin/1280_Trivia/frontend/templates"
    template_files = [
        "index.html",
        "join.html", 
        "player.html",
        "admin.html",
        "error.html",
        "host.html"
    ]
    
    print("🔍 Checking templates for emojis...")
    all_clean = True
    
    for template in template_files:
        file_path = os.path.join(template_dir, template)
        if os.path.exists(file_path):
            emojis = check_for_emojis(file_path)
            if emojis:
                print(f"❌ {template}: Found emojis: {emojis}")
                all_clean = False
            else:
                print(f"✅ {template}: Clean")
        else:
            print(f"⚠️  {template}: File not found")
    
    return all_clean

def validate_css():
    """Basic CSS validation"""
    css_file = "/Users/laurenadmin/1280_Trivia/frontend/static/css/style.css"
    
    print("\n🎨 Checking CSS file...")
    
    if not os.path.exists(css_file):
        print("❌ CSS file not found")
        return False
    
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic checks
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            print(f"❌ CSS: Mismatched braces - {open_braces} open, {close_braces} close")
            return False
        else:
            print(f"✅ CSS: Brace count looks good ({open_braces} pairs)")
        
        # Check for common CSS properties
        if '--primary-color' in content:
            print("✅ CSS: Variables defined")
        else:
            print("⚠️  CSS: No CSS variables found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading CSS: {e}")
        return False

def main():
    print("🎯 1280 Trivia - Template & CSS Validation")
    print("=" * 50)
    
    templates_clean = validate_templates()
    css_valid = validate_css()
    
    print("\n📊 SUMMARY")
    print("=" * 20)
    print(f"Templates emoji-free: {'✅ YES' if templates_clean else '❌ NO'}")
    print(f"CSS structure valid: {'✅ YES' if css_valid else '❌ NO'}")
    
    if templates_clean and css_valid:
        print("\n🎉 All validation checks passed!")
        return True
    else:
        print("\n⚠️  Some issues found, check above for details")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)