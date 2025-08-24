from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status, Query
from pydantic import UUID4
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from fastapi_pagination import Page, paginate
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo Centro de treinamento',
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency, 
    centro_treinamento_in: CentroTreinamentoIn = Body(...),
) -> CentroTreinamentoOut:
    # Verificar se o centro de treinamento já existe pelo nome
    centro_treinamento_existente = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_in.nome))
    ).scalars().first()

    if centro_treinamento_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Centro de treinamento com nome {centro_treinamento_in.nome} já existe.'
        )

    try:
        # Criação do Centro de Treinamento
        centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
        centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())
        
        db_session.add(centro_treinamento_model)
        await db_session.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='Ocorreu um erro ao inserir os dados no banco'
        )

    return centro_treinamento_out

    
    
@router.get(
    '/', 
    summary='Consultar todos os centros de treinamento',
    status_code=status.HTTP_200_OK,
    response_model=list[CentroTreinamentoOut],
)
async def query(db_session: DatabaseDependency) -> list[CentroTreinamentoOut]:
    centros_treinamento_out: list[CentroTreinamentoOut] = (
        await db_session.execute(select(CentroTreinamentoModel))
    ).scalars().all()
    
    if not centros_treinamento_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Nenhum centro de treinamento encontrado'
        )
    
    return centros_treinamento_out


@router.get(
    '/{id}', 
    summary='Consulta um centro de treinamento pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro_treinamento_out: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    if not centro_treinamento_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Centro de treinamento não encontrado no id: {id}'
        )
    
    return centro_treinamento_out

@router.get(
    '/by-name/{nome}', 
    summary='Consulta um centro de treinamento pelo nome',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def get_by_name(nome: str, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro_treinamento_out: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=nome))
    ).scalars().first()

    if not centro_treinamento_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Centro de treinamento não encontrado no nome: {nome}'
        )
    
    return centro_treinamento_out

@router.get(
    '/centros_treinamento/', 
    summary='Consultar todos os Centros de Treinamento com paginação',
    status_code=status.HTTP_200_OK,
    response_model=Page[CentroTreinamentoOut],  # Utilize o tipo Page para ativar a paginação
)
async def query(
    db_session: DatabaseDependency,
    limit: int = Query(10, ge=1, le=100),  # Limit: número de itens por página
    offset: int = Query(0, ge=0),  # Offset: número de itens a serem "pulados"
) -> Page[CentroTreinamentoOut]:
    query = select(CentroTreinamentoModel)  # Consulta todos os centros de treinamento

    # Aplica o paginador na consulta
    centros_treinamento = await db_session.execute(query)
    
    return paginate(centros_treinamento)  # Retorna a página paginada dos centros de treinamento

@router.patch(
    '/by-name/{nome}', 
    summary='Editar um centro de treinamento pelo nome',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def patch_by_name(nome: str, db_session: DatabaseDependency, centro_treinamento_up: CentroTreinamentoIn = Body(...)) -> CentroTreinamentoOut:
    centro_treinamento_out: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=nome))
    ).scalars().first()

    if not centro_treinamento_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Centro de treinamento não encontrado no nome: {nome}'
        )

    centro_treinamento_update = centro_treinamento_up.model_dump(exclude_unset=True)
    for key, value in centro_treinamento_update.items():
        setattr(centro_treinamento_out, key, value)

    await db_session.commit()
    await db_session.refresh(centro_treinamento_out)

    return centro_treinamento_out

@router.patch(
    '/{id}', 
    summary='Editar um centro de treinamento pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def patch(id: UUID4, db_session: DatabaseDependency, centro_treinamento_up: CentroTreinamentoIn = Body(...)) -> CentroTreinamentoOut:
    centro_treinamento_out: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    if not centro_treinamento_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Centro de treinamento não encontrado no id: {id}'
        )

    centro_treinamento_update = centro_treinamento_up.model_dump(exclude_unset=True)
    for key, value in centro_treinamento_update.items():
        setattr(centro_treinamento_out, key, value)

    await db_session.commit()
    await db_session.refresh(centro_treinamento_out)

    return centro_treinamento_out


@router.delete(
    '/by-name/{nome}', 
    summary='Deletar um centro de treinamento pelo nome',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_by_name(nome: str, db_session: DatabaseDependency) -> None:
    centro_treinamento_out: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=nome))
    ).scalars().first()

    if not centro_treinamento_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Centro de treinamento não encontrado no nome: {nome}'
        )
    
    await db_session.delete(centro_treinamento_out)
    await db_session.commit()

@router.delete(
    '/{id}', 
    summary='Deletar um centro de treinamento pelo id',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    centro_treinamento_out: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    if not centro_treinamento_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Centro de treinamento não encontrado no id: {id}'
        )
    
    await db_session.delete(centro_treinamento_out)
    await db_session.commit()
