'''Reparse a record file to update its information'''

from datetime import datetime

from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse

from mgxhub import cfg
from mgxhub.db import db_raw
from mgxhub.model.orm import File
from mgxhub.processor import FileProcessor
from mgxhub.storage import S3Adapter
from webapi.admin_api import admin_api


def _reparse(guid: str) -> None:
    oss = S3Adapter(**cfg.s3)
    db = db_raw()
    file_records = db.query(File.md5).filter(File.game_guid == guid).all()
    file_md5s = [f[0] for f in file_records]
    db.close()
    for filemd5 in file_md5s:
        downloaded = oss.download(f"/records/{filemd5}.zip")
        if downloaded:
            FileProcessor(
                downloaded,
                syncproc=True,
                s3replace=False,
                cleanup=True,
                buffermeta=[f"{filemd5}.zip", datetime.now().isoformat()]
            )


@admin_api.get("/game/reparse", tags=['game'])
async def reparse_a_record(background_tasks: BackgroundTasks, guid: str) -> dict:
    '''Reparse a record file to update its information.

    Used when parser is updated.

    - **guid**: The GUID of the record file.

    Defined in: `webapi/routers/game_reparse.py`
    '''

    background_tasks.add_task(_reparse, guid)

    return JSONResponse(status_code=202, content={"detail": f"Reparse command sent for [{guid}]"})
