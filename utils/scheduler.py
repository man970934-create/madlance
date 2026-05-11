"""Планировщик для архивации заданий и резюме"""
import asyncio
from datetime import datetime
from database import db


async def archive_expired_publications():
    """Архивирует просроченные задания и резюме"""
    await db.archive_expired_tasks()
    await db.archive_expired_resumes()


async def scheduler_loop():
    """Запускает планировщик каждый час"""
    while True:
        await archive_expired_publications()
        await asyncio.sleep(3600)
