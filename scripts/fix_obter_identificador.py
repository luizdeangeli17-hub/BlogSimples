import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

changed = []
for path in ROOT.rglob("*.py"):
    if path.exists():
        text = path.read_text(encoding='utf-8')
        if 'obter_identificador_cliente' in text:
            new = text.replace('obter_identificador_cliente', 'obter_identificador_cliente')
            path.write_text(new, encoding='utf-8')
            changed.append(str(path.relative_to(ROOT)))

print('Arquivos atualizados (obter_identificador_cliente -> obter_identificador_cliente):')
for p in changed:
    print(p)
print('Total:', len(changed))
