"""
Script de teste automatizado para o fluxo completo do blog (Secao 17)
"""
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8400"

def test_home_page():
    """Teste 1: Verificar se home page carrega"""
    print("\n" + "="*60)
    print("TESTE 1: Home Page")
    print("="*60 + "\n")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("[OK] Home page carregada com sucesso")
            if "Blog" in response.text or "Artigos" in response.text:
                print("[OK] Pagina contem elementos esperados")
                return True
            else:
                print("[ERRO] Pagina nao contem elementos esperados")
                return False
        else:
            print(f"[ERRO] Erro ao carregar home page: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] Erro ao conectar: {str(e)}")
        return False

def test_api_docs():
    """Teste 2: Verificar documentacao API"""
    print("\n" + "="*60)
    print("TESTE 2: Documentacao API")
    print("="*60 + "\n")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("[OK] Documentacao API disponivel em /docs")
            return True
        else:
            print(f"[ERRO] Documentacao nao acessivel: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] Erro ao conectar: {str(e)}")
        return False

def test_categories_api():
    """Teste 3: Verificar se API de categorias responde"""
    print("\n" + "="*60)
    print("TESTE 3: API de Categorias")
    print("="*60 + "\n")
    try:
        response = requests.get(f"{BASE_URL}/api/categorias")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] API de categorias respondeu com {len(data.get('categorias', []))} categorias")
            return True
        else:
            print(f"[ERRO] Erro ao acessar API: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] Erro: {str(e)}")
        return False

def test_articles_api():
    """Teste 4: Verificar se API de artigos responde"""
    print("\n" + "="*60)
    print("TESTE 4: API de Artigos Publicos")
    print("="*60 + "\n")
    try:
        response = requests.get(f"{BASE_URL}/api/artigos")
        if response.status_code == 200:
            data = response.json()
            artigos = data.get('artigos', [])
            print(f"[OK] API de artigos respondeu com {len(artigos)} artigos publicados")
            if len(artigos) > 0:
                print(f"[INFO] Primeiro artigo: '{artigos[0].get('titulo', 'N/A')}'")
            return True
        else:
            print(f"[ERRO] Erro ao acessar API: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] Erro: {str(e)}")
        return False

def test_static_files():
    """Teste 5: Verificar se arquivos estaticos carregam"""
    print("\n" + "="*60)
    print("TESTE 5: Arquivos Estaticos")
    print("="*60 + "\n")
    try:
        response = requests.get(f"{BASE_URL}/static/css/custom.css")
        if response.status_code == 200:
            print("[OK] Arquivo CSS carregado com sucesso")
            return True
        else:
            print(f"[ERRO] CSS nao encontrado: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERRO] Erro ao conectar: {str(e)}")
        return False

def test_templates():
    """Teste 6: Verificar se templates importantes existem"""
    print("\n" + "="*60)
    print("TESTE 6: Templates Principais")
    print("="*60 + "\n")
    templates_to_check = [
        ("/", "Home Page"),
        ("/login", "Login"),
        ("/cadastrar", "Cadastro"),
    ]
    
    all_passed = True
    for path, name in templates_to_check:
        try:
            response = requests.get(f"{BASE_URL}{path}", allow_redirects=True)
            if response.status_code == 200:
                print(f"[OK] {name} esta acessivel")
            else:
                print(f"[ERRO] {name} retornou status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"[ERRO] Erro ao acessar {name}: {str(e)}")
            all_passed = False
    
    return all_passed

def test_database():
    """Teste 7: Verificar integridade do banco de dados"""
    print("\n" + "="*60)
    print("TESTE 7: Banco de Dados")
    print("="*60 + "\n")
    try:
        import sqlite3
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        required_tables = ['usuario', 'categoria', 'artigo', 'chamado', 'chat_sala']
        
        print(f"[INFO] Tabelas encontradas: {', '.join(table_names)}")
        
        all_required = all(t in table_names for t in required_tables)
        if all_required:
            print("[OK] Todas as tabelas obrigatorias existem")
        else:
            missing = [t for t in required_tables if t not in table_names]
            print(f"[ERRO] Tabelas faltando: {', '.join(missing)}")
            return False
        
        # Verificar se categoria tabela tem dados
        cursor.execute("SELECT COUNT(*) FROM categoria;")
        cat_count = cursor.fetchone()[0]
        print(f"[INFO] Total de categorias: {cat_count}")
        
        # Verificar se artigo tabela existe e estrutura
        cursor.execute("PRAGMA table_info(artigo);")
        artigo_cols = cursor.fetchall()
        col_names = [col[1] for col in artigo_cols]
        
        required_cols = ['id', 'titulo', 'resumo', 'conteudo', 'status', 'usuario_id', 'categoria_id']
        all_cols = all(c in col_names for c in required_cols)
        if all_cols:
            print("[OK] Tabela artigo tem todas as colunas obrigatorias")
        else:
            missing = [c for c in required_cols if c not in col_names]
            print(f"[ERRO] Colunas faltando em artigo: {', '.join(missing)}")
            return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"[ERRO] Erro ao verificar banco: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("TESTES AUTOMATIZADOS - BLOG SIMPLES")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Executar testes
    results = {
        "Home Page": test_home_page(),
        "Documentacao API": test_api_docs(),
        "API Categorias": test_categories_api(),
        "API Artigos": test_articles_api(),
        "Arquivos Estaticos": test_static_files(),
        "Templates": test_templates(),
        "Banco de Dados": test_database(),
    }
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60 + "\n")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[OK]" if result else "[FALHOU]"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n[SUCESSO] TODOS OS TESTES PASSARAM!")
        print("\nProximos passos:")
        print("1. Acesse http://127.0.0.1:8400 para testar a aplicacao")
        print("2. Cadastre um administrador")
        print("3. Crie categorias")
        print("4. Crie artigos com a persona de autor")
        print("5. Visualize como leitor")
        return True
    else:
        print("\n[ERRO] Alguns testes falharam!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
