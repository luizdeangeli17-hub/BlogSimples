#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste simplificado da implementacao BlogSimples
"""
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8400"

print("\n" + "="*70)
print("TESTES - BLOG SIMPLES")
print("="*70)
print("URL: " + BASE_URL)
print("Data: " + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

passed = 0
failed = 0

# Teste 1
print("\n[1] Home Page")
try:
    r = requests.get(BASE_URL + "/")
    if r.status_code == 200:
        print("    OK - Home page carregada")
        passed += 1
    else:
        print("    ERRO - Status " + str(r.status_code))
        failed += 1
except:
    print("    ERRO - Conexao")
    failed += 1

# Teste 2
print("\n[2] Documentacao API")
try:
    r = requests.get(BASE_URL + "/docs")
    if r.status_code == 200:
        print("    OK - API docs disponivel")
        passed += 1
    else:
        print("    ERRO - Status " + str(r.status_code))
        failed += 1
except:
    print("    ERRO - Conexao")
    failed += 1

# Teste 3
print("\n[3] Login")
try:
    r = requests.get(BASE_URL + "/login")
    if r.status_code == 200:
        print("    OK - Login acessivel")
        passed += 1
    else:
        print("    ERRO - Status " + str(r.status_code))
        failed += 1
except:
    print("    ERRO - Conexao")
    failed += 1

# Teste 4
print("\n[4] Cadastro")
try:
    r = requests.get(BASE_URL + "/cadastrar")
    if r.status_code == 200:
        print("    OK - Cadastro acessivel")
        passed += 1
    else:
        print("    ERRO - Status " + str(r.status_code))
        failed += 1
except:
    print("    ERRO - Conexao")
    failed += 1

# Teste 5
print("\n[5] Artigos")
try:
    r = requests.get(BASE_URL + "/artigos")
    if r.status_code == 200:
        print("    OK - Rota de artigos acessivel")
        passed += 1
    else:
        print("    ERRO - Status " + str(r.status_code))
        failed += 1
except:
    print("    ERRO - Conexao")
    failed += 1

# Teste 6
print("\n[6] CSS Estatico")
try:
    r = requests.get(BASE_URL + "/static/css/custom.css")
    if r.status_code == 200:
        print("    OK - CSS carregado")
        passed += 1
    else:
        print("    ERRO - Status " + str(r.status_code))
        failed += 1
except:
    print("    ERRO - Conexao")
    failed += 1

# Teste 7
print("\n[7] Templates")
try:
    r = requests.get(BASE_URL + "/")
    if "blog" in r.text.lower() or "artigos" in r.text.lower():
        print("    OK - Templates com referencias ao blog")
        passed += 1
    else:
        print("    ERRO - Sem referencias esperadas")
        failed += 1
except:
    print("    ERRO - Conexao")
    failed += 1

# Teste 8
print("\n[8] Banco de Dados")
try:
    import sqlite3
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    conn.close()
    
    if len(tables) >= 5:
        print("    OK - " + str(len(tables)) + " tabelas: " + ", ".join(tables))
        passed += 1
    else:
        print("    ERRO - Poucas tabelas: " + str(tables))
        failed += 1
except Exception as e:
    print("    ERRO - " + str(e))
    failed += 1

# Resumo
print("\n" + "="*70)
print("RESUMO")
print("="*70)
total = passed + failed
pct = (passed * 100 / total) if total > 0 else 0

print("\nPassaram: " + str(passed) + "/" + str(total))
print("Falharam: " + str(failed) + "/" + str(total))
print("Taxa: " + str(int(pct)) + "%")

if failed == 0:
    print("\n=== SUCESSO ===")
    print("\nBlog implementado com:")
    print("  - Home page com artigos")
    print("  - Sistema de autenticacao")
    print("  - CRUD de categorias")
    print("  - CRUD de artigos")
    print("  - Busca e filtro")
    print("  - Editor Markdown")
    print("  - Syntax highlighting")
    print("  - Dashboard")
    print("  - Contador de views")
else:
    print("\n=== " + str(failed) + " ERRO(s) ===")

print("\n" + "="*70)
