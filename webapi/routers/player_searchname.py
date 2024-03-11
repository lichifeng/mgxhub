'''Search player by name'''

from datetime import datetime

from mgxhub.db.operation import search_players_by_name
from webapi import app


@app.get("/player/searchname")
async def search_player_by_name(
    player_name: str,
    stype: str = 'std',
    orderby: str = 'nagd',
    page: int = 0,
    page_size: int = 100
) -> dict:
    '''Search player by name

    Args:
        player_name (str): Player name to search
        stype (str, optional): Search type. 'std', 'prefix', 'suffix', 'exact'.
        orderby (str, optional): Order setting. Defaults to 'nagd'.
        page (int, optional): Page number. Defaults to 0.
        page_size (int, optional): Page size. Defaults to 100.

    Defined in: `webapi/routers/player_searchname.py`
    '''

    result = search_players_by_name(player_name, stype, orderby, page, page_size)

    current_time = datetime.now().isoformat()
    return {'players': result, 'generated_at': current_time}