import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

replacements = [
    ("Perfil.AUTOR", "Perfil.AUTOR"),
    ("Perfil.LEITOR", "Perfil.LEITOR"),
    ("Perfil.AUTOR.value", "Perfil.AUTOR.value"),
    ("Perfil.LEITOR.value", "Perfil.LEITOR.value"),
    ("obter_identificador_cliente", "obter_identificador_cliente"),
    ("Autor", "Autor"),
    ("Leitor", "Leitor"),
    ("autor", "autor"),
    ("leitor", "leitor"),
]

exts = {".py", ".html", ".md", ".json", ".txt"}

changed = []
for path in ROOT.rglob("*"):
    if path.is_file() and path.suffix in exts:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        new = text
        for a, b in replacements:
            new = new.replace(a, b)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))

print("Arquivos modificados:")
for p in changed:
    print(p)
print(f"Total: {len(changed)}")
