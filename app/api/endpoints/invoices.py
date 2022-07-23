from datetime import datetime
import pendulum

import pytz
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import random
from app.api import deps
from app.core.config import settings
from app.models.model import Device, Invoice, User
from app.schemas.requests import InvoiceBaseRequest
from app.schemas.responses import DailyResponse, InvoiceBaseResponse
from sqlalchemy import cast, Date, func

timezone = pytz.timezone(settings.TIMEZONE)
router = APIRouter()


@router.post("/", response_model=InvoiceBaseResponse)
async def submit_invoice(
    invoice_request: InvoiceBaseRequest,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    """
    Submit invoice data.

    Requirements for submitting invoice data through API are:
    1. Device has been registered/added (as Administrator)
    2. Device has been assigned to a user (as Administrator)
    3. Login to get token then use the access token as Bearer token
    """
    result = await session.exec(select(Device).where(Device.user_id == current_user.id))
    devices = result.fetchall()
    if len(devices) == 0:
        raise HTTPException(status_code=400, detail="User has no device(s)")
    found = False
    for dev in devices:
        if dev.name == invoice_request.device_name:
            found = True
    if not found:
        raise HTTPException(
            status_code=400, detail=f"User has no device {invoice_request.device_name}"
        )
    try:
        invoice = Invoice(
            invoice_num=invoice_request.invoice_num,
            invoice_date=invoice_request.invoice_date,
            device_name=invoice_request.device_name,
            username=current_user.username,
            tax_value=invoice_request.tax_value,
            total_value=invoice_request.total_value,
            created_at=datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S"),
            modified_at=datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S"),
        )
        session.add(invoice)
        await session.commit()
        await session.refresh(invoice)
        # # TODO: put record in kinesis stream
        # task = task_put_invoice.delay(**json.loads(invoice_request.json()))
        return invoice

    except Exception as ex:
        print(str(ex))
        await session.rollback()
        raise HTTPException(
            status_code=500, detail="Something went wrong. Contact your admin"
        )


@router.get("/daily", response_model=DailyResponse)
async def get_daily_stats(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    """Get daily invoice statistics (sales, transactions) from current user"""
    result = await session.exec(
        select(Invoice.device_name, Invoice.invoice_num, Invoice.invoice_date, Invoice.total_value, Invoice.tax_value).where(Invoice.username == current_user.username).where(cast(Invoice.invoice_date, Date) == cast(pendulum.now().date(), Date)))

    data = result.fetchall()
    invoices = DailyResponse(
        username=current_user.username, total=0, tax=0, count=0, invoices=[])
    if len(data) != 0:
        total = sum([it.total_value for it in data])
        tax = sum([it.tax_value for it in data])
        invoices = DailyResponse(username=current_user.username, count=len(
            data), total=total, tax=tax, invoices=data)
    return invoices


@router.get('/weekly_stats')
async def weekly_statistics(
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session),
):
    """Weekly statistics (sales, tax, and transactions"""
    weekago = pendulum.now().subtract(days=6)
    now = pendulum.now()
    result = await session.exec(select(cast(Invoice.invoice_date, Date).label('date'), func.sum(Invoice.total_value).label('total'), func.sum(Invoice.tax_value).label('tax'), func.count().label('trx'))
                                .where(Invoice.username == current_user.username)
                                .where(cast(Invoice.invoice_date, Date) >= cast(weekago.date(), Date))
                                .where(cast(Invoice.invoice_date, Date) <= cast(now.date(), Date))
                                .group_by(cast(Invoice.invoice_date, Date))
                                .order_by(cast(Invoice.invoice_date, Date)))

    stats = result.fetchall()
    return stats


@router.get("/analytics")
async def analytics():
    """fake data"""
    sales = float(round(random.random(), 4) * 1000000)
    trx = int(round(random.random() * 100))
    tax = sales * 11 / 100
    return {"sales": sales, "trx": trx, "tax": tax}
