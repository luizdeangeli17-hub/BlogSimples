from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria


class CriarArtigoDTO(BaseModel):
    titulo: str
    resumo: str
    conteudo: str
    categoria_id: int

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, value: str) -> str:
        """Valida o título do artigo (3-100 caracteres)."""
        validar_string_obrigatoria(value, "Título")
        if len(value.strip()) < 3 or len(value.strip()) > 100:
            raise ValueError("Título deve ter entre 3 e 100 caracteres")
        return value.strip()

    @field_validator("resumo")
    @classmethod
    def validar_resumo(cls, value: str) -> str:
        """Valida o resumo (até 300 caracteres)."""
        if value and len(value.strip()) > 300:
            raise ValueError("Resumo deve ter no máximo 300 caracteres")
        return value.strip() if value else ""

    @field_validator("conteudo")
    @classmethod
    def validar_conteudo(cls, value: str) -> str:
        """Valida o conteúdo do artigo (obrigatório)."""
        validar_string_obrigatoria(value, "Conteúdo")
        return value.strip()

    @field_validator("categoria_id")
    @classmethod
    def validar_categoria_id(cls, value: int) -> int:
        """Valida se categoria_id é um inteiro positivo."""
        if value <= 0:
            raise ValueError("Categoria ID deve ser um número positivo")
        return value


class AlterarArtigoDTO(BaseModel):
    titulo: str
    resumo: str
    conteudo: str
    categoria_id: int
    status: str

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, value: str) -> str:
        """Valida o título do artigo (3-100 caracteres)."""
        validar_string_obrigatoria(value, "Título")
        if len(value.strip()) < 3 or len(value.strip()) > 100:
            raise ValueError("Título deve ter entre 3 e 100 caracteres")
        return value.strip()

    @field_validator("resumo")
    @classmethod
    def validar_resumo(cls, value: str) -> str:
        """Valida o resumo (até 300 caracteres)."""
        if value and len(value.strip()) > 300:
            raise ValueError("Resumo deve ter no máximo 300 caracteres")
        return value.strip() if value else ""

    @field_validator("conteudo")
    @classmethod
    def validar_conteudo(cls, value: str) -> str:
        """Valida o conteúdo do artigo (obrigatório)."""
        validar_string_obrigatoria(value, "Conteúdo")
        return value.strip()

    @field_validator("categoria_id")
    @classmethod
    def validar_categoria_id(cls, value: int) -> int:
        """Valida se categoria_id é um inteiro positivo."""
        if value <= 0:
            raise ValueError("Categoria ID deve ser um número positivo")
        return value

    @field_validator("status")
    @classmethod
    def validar_status(cls, value: str) -> str:
        """Valida o status do artigo."""
        status_validos = ["Rascunho", "Publicado", "Pausado"]
        if value not in status_validos:
            raise ValueError(f"Status deve ser um de: {', '.join(status_validos)}")
        return value
