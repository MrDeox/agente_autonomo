#!/usr/bin/env python3
"""
Teste de conectividade API para diagnosticar problemas com LLM
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_openrouter():
    """Testa conectividade com OpenRouter"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY não encontrada")
        return False
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": [{"role": "user", "content": "Test"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"📡 OpenRouter Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ OpenRouter: Conectividade OK")
            return True
        else:
            print(f"❌ OpenRouter Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ OpenRouter Exception: {e}")
        return False

def test_gemini():
    """Testa conectividade com Gemini"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY não encontrada")
        return False
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{"parts": [{"text": "Test"}]}],
        "generationConfig": {"maxOutputTokens": 10}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"📡 Gemini Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Gemini: Conectividade OK")
            return True
        else:
            print(f"❌ Gemini Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Gemini Exception: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testando conectividade das APIs LLM...")
    print("=" * 50)
    
    openrouter_ok = test_openrouter()
    gemini_ok = test_gemini()
    
    print("=" * 50)
    print(f"📊 Resultado:")
    print(f"  OpenRouter: {'✅' if openrouter_ok else '❌'}")
    print(f"  Gemini: {'✅' if gemini_ok else '❌'}")
    
    if openrouter_ok or gemini_ok:
        print("🎉 Pelo menos uma API está funcionando!")
    else:
        print("💥 Ambas as APIs estão com problema!")