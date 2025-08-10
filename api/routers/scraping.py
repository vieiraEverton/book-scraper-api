from datetime import datetime, timedelta

from fastapi import APIRouter, Depends

from api.security import get_current_user
from api.tasks import perform_scrape

router = APIRouter()

@router.get("/trigger", summary="Trigger the Scraping to start updating the Database", status_code=200)
async def trigger_scraping(
        current_user: dict = Depends(get_current_user)
):
    """
    Agenda a execução imediata (com atraso de 2 segundos) do processo de scraping para atualizar o banco de dados.

    ### Requisitos de autenticação
    - É necessário estar autenticado via **JWT Bearer Token**.
    - Usuários não autenticados receberão **401 Unauthorized**.

    ### Comportamento
    - Adiciona um job no scheduler interno para executar a função `perform_scrape`.
    - O agendamento usa o trigger `"date"` para rodar **uma única vez**.
    - O atraso de **2 segundos** é proposital para garantir execução correta em ambientes Docker.
    - Caso já exista um job com o mesmo ID (`initial_scrape`), ele será substituído.

    ### Response
    - **200 OK**: Confirmação de que o job foi agendado.
    - **401 Unauthorized**: Caso o token seja inválido ou ausente.

    ### Observações
    - Essa rota **não executa o scraping imediatamente**; apenas agenda a execução.
    - O scraping coleta dados de livros e atualiza a base local.
    """
    from api.main import scheduler
    scheduler.add_job(
        perform_scrape,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=2),  # This extra seconds was necessary in order to run it on docker
        id="initial_scrape",
        replace_existing=True
    )


