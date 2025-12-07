from typing import Optional
from model.categoria_model import Categoria
from sql.categoria_sql import *
from util.db_util import obter_conexao


def _row_to_categoria(row) -> Categoria:
    """
    Converte uma linha do banco de dados em objeto Categoria.
    """
    return Categoria(
        id=row["id"],
        nome=row["nome"],
        descricao=row["descricao"],
        data_cadastro=row["data_cadastro"],
        data_atualizacao=row["data_atualizacao"],
    )


def criar_tabela():
    """
    Cria a tabela de categorias se ela não existir.
    Deve ser chamada na inicialização do sistema.
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(categoria: Categoria) -> Optional[Categoria]:
    """
    Insere uma nova categoria no banco de dados.

    Returns:
        Categoria com ID preenchido se sucesso, None se erro
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERIR, (categoria.nome, categoria.descricao))
            categoria.id = cursor.lastrowid
            return categoria
    except Exception as e:
        print(f"Erro ao inserir categoria: {e}")
        return None


def alterar(categoria: Categoria) -> bool:
    """
    Atualiza uma categoria existente.
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(ALTERAR, (categoria.nome, categoria.descricao, categoria.id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao alterar categoria: {e}")
        return False


def excluir(id: int) -> bool:
    """
    Exclui uma categoria do banco de dados.
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(EXCLUIR, (id,))
            return cursor.rowcount > 0

    except Exception as e:
        print(f"Erro ao excluir categoria: {e}")
        return False


def obter_por_id(id: int) -> Optional[Categoria]:
    """
    Busca uma categoria por ID.
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_ID, (id,))
            row = cursor.fetchone()
            if row:
                return _row_to_categoria(row)
            return None
    except Exception as e:
        print(f"Erro ao obter categoria por ID: {e}")
        return None


def obter_todos() -> list[Categoria]:
    """
    Retorna todas as categorias do banco de dados.
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_TODOS)
            rows = cursor.fetchall()
            return [_row_to_categoria(row) for row in rows]
    except Exception as e:
        print(f"Erro ao obter todas as categorias: {e}")
        return []


def obter_por_nome(nome: str) -> Optional[Categoria]:
    """
    Busca uma categoria pelo nome exato.
    """
    try:
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_NOME, (nome,))
            row = cursor.fetchone()
            if row:
                return _row_to_categoria(row)
            return None
    except Exception as e:
        print(f"Erro ao obter categoria por nome: {e}")
        return None
