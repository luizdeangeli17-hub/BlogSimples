from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class StatusArtigo(Enum):
    RASCUNHO = "Rascunho"
    PUBLICADO = "Publicado"
    PAUSADO = "Pausado"


@dataclass
class Artigo:
    # Campos obrigatórios (com defaults para permitir criação)
    id: Optional[int] = None
    titulo: str = ""
    resumo: str = ""
    conteudo: str = ""
    status: str = StatusArtigo.RASCUNHO.value
    usuario_id: int = 0
    categoria_id: int = 0
    qtde_visualizacoes: int = 0
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    data_publicacao: Optional[datetime] = None
    # Campos do JOIN (para exibição)
    usuario_nome: Optional[str] = None
    categoria_nome: Optional[str] = None
