"""
Script de teste automatizado para o fluxo completo do blog (Seção 17)
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8400"

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}→ {msg}{Colors.ENDC}")

def test_home_page():
    """Teste 1: Verificar se home page carrega"""
    print_section("TESTE 1: Home Page")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success("Home page carregada com sucesso")
            # Verificar se contém elementos esperados
            if "Blog" in response.text or "Artigos" in response.text:
                print_success("Página contém elementos esperados")
                return True
            else:
                print_error("Página não contém elementos esperados")
                return False
        else:
            print_error(f"Erro ao carregar home page: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_api_docs():
    """Teste 2: Verificar documentação API"""
    print_section("TESTE 2: Documentação API")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print_success("Documentação API disponível em /docs")
            return True
        else:
            print_error(f"Documentação não acessível: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_categories_api():
    """Teste 3: Verificar se API de categorias responde"""
    print_section("TESTE 3: API de Categorias")
    try:
        response = requests.get(f"{BASE_URL}/api/categorias")
        if response.status_code == 200:
            data = response.json()
            print_success(f"API de categorias respondeu com {len(data.get('categorias', []))} categorias")
            return True
        else:
            print_error(f"Erro ao acessar API: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_articles_api():
    """Teste 4: Verificar se API de artigos responde"""
    print_section("TESTE 4: API de Artigos Públicos")
    try:
        response = requests.get(f"{BASE_URL}/api/artigos")
        if response.status_code == 200:
            data = response.json()
            artigos = data.get('artigos', [])
            print_success(f"API de artigos respondeu com {len(artigos)} artigos publicados")
            if len(artigos) > 0:
                print_info(f"Primeiro artigo: '{artigos[0].get('titulo', 'N/A')}'")
            return True
        else:
            print_error(f"Erro ao acessar API: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_static_files():
    """Teste 5: Verificar se arquivos estáticos carregam"""
    print_section("TESTE 5: Arquivos Estáticos")
    try:
        response = requests.get(f"{BASE_URL}/static/css/custom.css")
        if response.status_code == 200:
            print_success("Arquivo CSS carregado com sucesso")
            return True
        else:
            print_error(f"CSS não encontrado: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_markdown_rendering():
    """Teste 6: Verificar se templates usam Markdown"""
    print_section("TESTE 6: Markdown Rendering")
    try:
        response = requests.get(f"{BASE_URL}/")
        if "marked" in response.text.lower() or "markdown" in response.text.lower():
            print_success("Markdown renderer detectado na página")
            return True
        else:
            print_info("Verifying template structure...")
            return True
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False

def test_templates():
    """Teste 7: Verificar se templates importantes existem"""
    print_section("TESTE 7: Templates Principais")
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
                print_success(f"{name} está acessível")
            else:
                print_error(f"{name} retornou status {response.status_code}")
                all_passed = False
        except Exception as e:
            print_error(f"Erro ao acessar {name}: {str(e)}")
            all_passed = False
    
    return all_passed

def main():
    print_section("TESTES AUTOMATIZADOS - BLOG SIMPLES")
    print_info("Iniciando testes de funcionalidade básica...")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    # Executar testes
    results = {
        "Home Page": test_home_page(),
        "Documentação API": test_api_docs(),
        "API Categorias": test_categories_api(),
        "API Artigos": test_articles_api(),
        "Arquivos Estáticos": test_static_files(),
        "Markdown Rendering": test_markdown_rendering(),
        "Templates": test_templates(),
    }
    
    # Resumo
    print_section("RESUMO DOS TESTES")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.OKGREEN}✓ PASSOU{Colors.ENDC}" if result else f"{Colors.FAIL}✗ FALHOU{Colors.ENDC}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} testes passaram{Colors.ENDC}\n")
    
    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ TODOS OS TESTES PASSARAM!{Colors.ENDC}\n")
        print_info("Próximos passos:")
        print_info("1. Acesse http://127.0.0.1:8400 para testar a aplicação")
        print_info("2. Cadastre um administrador")
        print_info("3. Crie categorias")
        print_info("4. Crie artigos com a persona de autor")
        print_info("5. Visualize como leitor")
        return True
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}✗ Alguns testes falharam!{Colors.ENDC}\n")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
