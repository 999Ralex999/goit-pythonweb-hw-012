from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter(tags=["utils"])

@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar_one_or_none() != 1:
            raise HTTPException(status_code=500, detail="Database misconfigured")
        return {"message": "Database is running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
