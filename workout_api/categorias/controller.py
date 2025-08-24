from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status, Query
from pydantic import UUID4
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.categorias.models import CategoriaModel
from fastapi_pagination import Page, paginate
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
    '/', 
    summary='Criar uma nova Categoria',
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut,
)
async def post(
    db_session: DatabaseDependency, 
    categoria_in: CategoriaIn = Body(...),
) -> CategoriaOut:
    # Verificar se a categoria já existe pelo nome
    categoria_existente = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_in.nome))
    ).scalars().first()

    if categoria_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Categoria com nome {categoria_in.nome} já existe.'
        )

    try:
        # Criação da Categoria
        categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
        categoria_model = CategoriaModel(**categoria_out.model_dump())
        
        db_session.add(categoria_model)
        await db_session.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='Ocorreu um erro ao inserir os dados no banco'
        )

    return categoria_out

    
    
@router.get(
    '/', 
    summary='Consultar todas as Categorias',
    status_code=status.HTTP_200_OK,
    response_model=list[CategoriaOut],
)
async def query(db_session: DatabaseDependency) -> list[CategoriaOut]:
    categorias: list[CategoriaOut] = (await db_session.execute(select(CategoriaModel))).scalars().all()
    
    if not categorias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Nenhuma categoria encontrada'
        )
    
    return categorias


@router.get(
    '/{id}', 
    summary='Consulta uma Categoria pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Categoria não encontrada no id: {id}'
        )
    
    return categoria

@router.get(
    '/nome/{nome}', 
    summary='Consultar Categoria pelo nome',
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def get_by_nome(nome: str, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(nome=nome))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Categoria não encontrada com o nome: {nome}'
        )
    
    return categoria

@router.get(
    '/categorias/', 
    summary='Consultar todas as Categorias com paginação',
    status_code=status.HTTP_200_OK,
    response_model=Page[CategoriaOut],  # Utilize o tipo Page para ativar a paginação
)
async def query(
    db_session: DatabaseDependency,
    limit: int = Query(10, ge=1, le=100),  # Limit: número de itens por página
    offset: int = Query(0, ge=0),  # Offset: número de itens a serem "pulados"
) -> Page[CategoriaOut]:
    query = select(CategoriaModel)  # Consulta todas as categorias

    # Aplica o paginador na consulta
    categorias = await db_session.execute(query)
    
    return paginate(categorias)  # Retorna a página paginada das categorias


@router.patch(
    '/{id}', 
    summary='Editar uma Categoria pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def patch(id: UUID4, db_session: DatabaseDependency, categoria_up: CategoriaIn = Body(...)) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Categoria não encontrada no id: {id}'
        )
    
    categoria_update = categoria_up.model_dump(exclude_unset=True)
    for key, value in categoria_update.items():
        setattr(categoria, key, value)

    await db_session.commit()
    await db_session.refresh(categoria)

    return categoria

@router.patch(
    '/nome/{nome}', 
    summary='Editar uma Categoria pelo nome',
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def patch_by_nome(nome: str, db_session: DatabaseDependency, categoria_up: CategoriaIn = Body(...)) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(nome=nome))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Categoria não encontrada com o nome: {nome}'
        )
    
    categoria_update = categoria_up.model_dump(exclude_unset=True)
    for key, value in categoria_update.items():
        setattr(categoria, key, value)

    await db_session.commit()
    await db_session.refresh(categoria)

    return categoria


@router.delete(
    '/{id}', 
    summary='Deletar uma Categoria pelo id',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Categoria não encontrada no id: {id}'
        )
    
    await db_session.delete(categoria)
    await db_session.commit()

@router.delete(
    '/nome/{nome}', 
    summary='Deletar uma Categoria pelo nome',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_by_nome(nome: str, db_session: DatabaseDependency) -> None:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(nome=nome))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Categoria não encontrada com o nome: {nome}'
        )
    
    await db_session.delete(categoria)
    await db_session.commit()
