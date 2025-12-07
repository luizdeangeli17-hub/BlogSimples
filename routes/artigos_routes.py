from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

# DTOs e modelo
from dtos.artigo_dto import CriarArtigoDTO, AlterarArtigoDTO
from model.artigo_model import Artigo, StatusArtigo
from model.usuario_logado_model import UsuarioLogado

# Repositórios
from repo import artigo_repo, categoria_repo

# Utilitários
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.perfis import Perfil
from util.template_util import criar_templates

# ----------------------------------------------------------------------
# Configurações do router e dos templates
# ----------------------------------------------------------------------
router = APIRouter(prefix="/artigos")
templates = criar_templates()

# Rate limiter dinâmico para rotas de artigos
artigos_limiter = DynamicRateLimiter(
    chave_max="rate_limit_artigos_max",
    chave_minutos="rate_limit_artigos_minutos",
    padrao_max=20,
    padrao_minutos=1,
    nome="artigos"
)

# ----------------------------------------------------------------------
# Rotas PRIVADAS (Autores e Administradores)
# ----------------------------------------------------------------------

@router.get("/meus")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def meus_artigos(
    request: Request,
    usuario_logado: UsuarioLogado = None,
):
    """
    Lista todos os artigos do usuário logado (Autor).
    """
    # Verificar identificador para rate limiting
    identificador = obter_identificador_cliente(request)
    if not artigos_limiter.verificar(identificador):
        informar_erro(request, "Muitas requisições. Tente novamente em alguns momentos.")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # Obter artigos do usuário
    artigos = artigo_repo.obter_por_usuario(usuario_logado.id)
    
    return templates.TemplateResponse(
        request=request,
        name="artigos/meus.html",
        context={
            "artigos": artigos,
            "usuario_logado": usuario_logado,
        },
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def cadastrar_get(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Formulário para criar novo artigo.
    """
    # Obter categorias para o select
    categorias = categoria_repo.obter_todos()
    
    return templates.TemplateResponse(
        request=request,
        name="artigos/cadastrar.html",
        context={
            "categorias": categorias,
            "usuario_logado": usuario_logado,
        },
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def cadastrar_post(
    request: Request,
    titulo: str = Form(...),
    resumo: str = Form(...),
    conteudo: str = Form(...),
    categoria_id: int = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Cria um novo artigo.
    """
    try:
        # Validar dados com DTO
        dto = CriarArtigoDTO(
            titulo=titulo,
            resumo=resumo,
            conteudo=conteudo,
            categoria_id=categoria_id,
        )

        # Verificar se o título já existe
        if artigo_repo.titulo_existe(dto.titulo):
            informar_erro(request, "Este título já existe. Use um título diferente.")
            categorias = categoria_repo.obter_todos()
            return templates.TemplateResponse(
                request=request,
                name="artigos/cadastrar.html",
                context={
                    "categorias": categorias,
                    "usuario_logado": usuario_logado,
                    "titulo": titulo,
                    "resumo": resumo,
                    "conteudo": conteudo,
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Criar novo artigo em rascunho
        artigo = Artigo(
            id=0,
            titulo=dto.titulo,
            resumo=dto.resumo,
            conteudo=dto.conteudo,
            status=StatusArtigo.RASCUNHO.value,
            usuario_id=usuario_logado.id,
            categoria_id=dto.categoria_id,
            qtde_visualizacoes=0,
            data_cadastro=datetime.now(),
            data_atualizacao=datetime.now(),
            data_publicacao=None,
            usuario_nome=usuario_logado.nome,
            categoria_nome="",
        )

        # Inserir no banco
        artigo_id = artigo_repo.inserir(artigo)
        if not artigo_id:
            informar_erro(request, "Erro ao criar o artigo. Tente novamente.")
            categorias = categoria_repo.obter_todos()
            return templates.TemplateResponse(
                request=request,
                name="artigos/cadastrar.html",
                context={
                    "categorias": categorias,
                    "usuario_logado": usuario_logado,
                    "titulo": titulo,
                    "resumo": resumo,
                    "conteudo": conteudo,
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        informar_sucesso(request, "Artigo criado com sucesso!")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = "; ".join([f"{erro['loc'][0]}: {erro['msg']}" for erro in e.errors()])
        informar_erro(request, f"Erro na validação: {erros}")
        categorias = categoria_repo.obter_todos()
        return templates.TemplateResponse(
            request=request,
            name="artigos/cadastrar.html",
            context={
                "categorias": categorias,
                "usuario_logado": usuario_logado,
                "titulo": titulo,
                "resumo": resumo,
                "conteudo": conteudo,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def editar_get(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Formulário para editar um artigo.
    """
    # Obter artigo
    artigo = artigo_repo.obter_por_id(id)
    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar permissão (autor ou admin)
    if artigo.usuario_id != usuario_logado.id and usuario_logado.perfil != Perfil.ADMIN.value:
        informar_erro(request, "Você não tem permissão para editar este artigo.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    # Obter categorias
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        request=request,
        name="artigos/editar.html",
        context={
            "artigo": artigo,
            "categorias": categorias,
            "usuario_logado": usuario_logado,
        },
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def editar_post(
    request: Request,
    id: int,
    titulo: str = Form(...),
    resumo: str = Form(...),
    conteudo: str = Form(...),
    categoria_id: int = Form(...),
    status: str = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Atualiza um artigo existente.
    """
    try:
        # Obter artigo
        artigo = artigo_repo.obter_por_id(id)
        if not artigo:
            raise ErroValidacaoFormulario("Artigo não encontrado.")

        # Verificar permissão
        if artigo.usuario_id != usuario_logado.id and usuario_logado.perfil != Perfil.ADMIN.value:
            raise ErroValidacaoFormulario("Você não tem permissão para editar este artigo.")

        # Validar dados com DTO
        dto = AlterarArtigoDTO(
            titulo=titulo,
            resumo=resumo,
            conteudo=conteudo,
            categoria_id=categoria_id,
            status=status,
        )

        # Verificar se o título já existe (excluindo este artigo)
        if artigo_repo.titulo_existe(dto.titulo, excluir_id=id):
            raise ErroValidacaoFormulario("Este título já existe. Use um título diferente.")

        # Atualizar artigo
        artigo.titulo = dto.titulo
        artigo.resumo = dto.resumo
        artigo.conteudo = dto.conteudo
        artigo.categoria_id = dto.categoria_id
        artigo.status = dto.status
        artigo.data_atualizacao = datetime.now().isoformat()

        if not artigo_repo.alterar(artigo):
            raise ErroValidacaoFormulario("Erro ao atualizar o artigo. Tente novamente.")

        informar_sucesso(request, "Artigo atualizado com sucesso!")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = "; ".join([f"{erro['loc'][0]}: {erro['msg']}" for erro in e.errors()])
        informar_erro(request, f"Erro na validação: {erros}")
        artigo = artigo_repo.obter_por_id(id)
        categorias = categoria_repo.obter_todos()
        return templates.TemplateResponse(
            request=request,
            name="artigos/editar.html",
            context={
                "artigo": artigo,
                "categorias": categorias,
                "usuario_logado": usuario_logado,
                "titulo": titulo,
                "resumo": resumo,
                "conteudo": conteudo,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except ErroValidacaoFormulario as e:
        informar_erro(request, str(e))
        artigo = artigo_repo.obter_por_id(id)
        categorias = categoria_repo.obter_todos()
        return templates.TemplateResponse(
            request=request,
            name="artigos/editar.html",
            context={
                "artigo": artigo,
                "categorias": categorias,
                "usuario_logado": usuario_logado,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def excluir(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Exclui um artigo.
    """
    # Obter artigo
    artigo = artigo_repo.obter_por_id(id)
    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar permissão
    if artigo.usuario_id != usuario_logado.id and usuario_logado.perfil != Perfil.ADMIN.value:
        informar_erro(request, "Você não tem permissão para excluir este artigo.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    # Excluir
    if not artigo_repo.excluir(id):
        informar_erro(request, "Erro ao excluir o artigo. Tente novamente.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    informar_sucesso(request, "Artigo excluído com sucesso!")
    return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/publicar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def publicar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Publica um artigo (muda status para 'Publicado' e define data_publicacao).
    """
    # Obter artigo
    artigo = artigo_repo.obter_por_id(id)
    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar permissão
    if artigo.usuario_id != usuario_logado.id and usuario_logado.perfil != Perfil.ADMIN.value:
        informar_erro(request, "Você não tem permissão para publicar este artigo.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    # Atualizar status
    if not artigo_repo.alterar_status(id, StatusArtigo.PUBLICADO.value):
        informar_erro(request, "Erro ao publicar o artigo. Tente novamente.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    informar_sucesso(request, "Artigo publicado com sucesso!")
    return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/pausar/{id}")
@requer_autenticacao([Perfil.AUTOR.value, Perfil.ADMIN.value])
async def pausar(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Pausa um artigo publicado (muda status para 'Pausado').
    """
    # Obter artigo
    artigo = artigo_repo.obter_por_id(id)
    if not artigo:
        informar_erro(request, "Artigo não encontrado.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar permissão
    if artigo.usuario_id != usuario_logado.id and usuario_logado.perfil != Perfil.ADMIN.value:
        informar_erro(request, "Você não tem permissão para pausar este artigo.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    # Atualizar status
    if not artigo_repo.alterar_status(id, StatusArtigo.PAUSADO.value):
        informar_erro(request, "Erro ao pausar o artigo. Tente novamente.")
        return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)

    informar_sucesso(request, "Artigo pausado com sucesso!")
    return RedirectResponse(url="/artigos/meus", status_code=status.HTTP_303_SEE_OTHER)


# ----------------------------------------------------------------------
# Rotas PÚBLICAS (sem autenticação)
# ----------------------------------------------------------------------

@router.get("/")
async def buscar(
    request: Request,
    termo: Optional[str] = None,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Busca e lista artigos publicados (com busca opcional).
    """
    # Verificar identificador para rate limiting
    identificador = obter_identificador_cliente(request)
    if not artigos_limiter.verificar(identificador):
        informar_erro(request, "Muitas requisições. Tente novamente em alguns momentos.")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # Buscar artigos
    if termo:
        artigos = artigo_repo.buscar_por_titulo(termo)
    else:
        artigos = artigo_repo.obter_publicados()

    # Obter categorias para filtro
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        request=request,
        name="artigos/buscar.html",
        context={
            "artigos": artigos,
            "categorias": categorias,
            "termo": termo or "",
            "usuario_logado": usuario_logado,
        },
    )


@router.get("/ler/{id}")
async def ler(
    request: Request,
    id: int,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Exibe um artigo publicado e incrementa visualizações.
    """
    # Obter artigo
    artigo = artigo_repo.obter_por_id(id)
    if not artigo or artigo.status != StatusArtigo.PUBLICADO.value:
        informar_erro(request, "Artigo não encontrado ou não está publicado.")
        return RedirectResponse(url="/artigos/", status_code=status.HTTP_303_SEE_OTHER)

    # Incrementar visualizações
    artigo_repo.incrementar_visualizacoes(id)

    return templates.TemplateResponse(
        request=request,
        name="artigos/ler.html",
        context={
            "artigo": artigo,
            "usuario_logado": usuario_logado,
        },
    )
