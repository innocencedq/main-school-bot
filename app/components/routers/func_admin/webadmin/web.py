import secrets
from pathlib import Path
from urllib.parse import quote, unquote
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from config import ADMIN_KEY
from app.supportfunctions.main_utils import get_username_from_id
from app.database.data import User, async_session
from app.database.requests import get_all_users_info, check_admin, add_admin, remove_admin
from app.components.notifyprocesses.notify import message_admin
from app.database.requests import change_text_ui, get_all_strings_ui

app = FastAPI(title='AdminPanel')

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

sessions = {}

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        return sessions[session_id]
    return None

@app.get('/', response_class=HTMLResponse)
async def root():
    return RedirectResponse(url='/login')

@app.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse('login.html', {'request': request, 'error': None})

@app.post('/login')
async def login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...)
):
    if password == ADMIN_KEY and await check_admin(int(login)):
        session_id = secrets.token_urlsafe(32)
        username = await get_username_from_id(login)
        sessions[session_id] = {
            'login': username
        }
        
        response = RedirectResponse(url='/dashboard', status_code=303)
        response.set_cookie(key='session_id', value=session_id, httponly=True, max_age=86400)
        return response
    
    return templates.TemplateResponse(
        'login.html',
        {'request': request, 'error': 'Неверный ключ или юзернейм (ключ находится в README.md)'}
    )

@app.get('/logout')
async def logout():
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie('session_id')
    response.delete_cookie('last_action')
    return response

@app.get('/dashboard')
async def dashboard(request: Request):
    session_id = request.cookies.get('session_id')
    user = sessions.get(session_id)
    
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    
    users = await get_all_users_info()
    
    users_data = []
    for db_user in users:
        users_data.append({
            'tg_id': db_user.tg_id,
            'full_name': db_user.username or f"User_{db_user.tg_id}",
            'date_started': db_user.date_started,
            'requests_ai': db_user.requests_ai,
            'shift': db_user.shift,
            'tester': db_user.tester,
            'username': db_user.username,
            'is_admin': await check_admin(db_user.tg_id)
        })
    
    last_action = request.cookies.get('last_action')
    if last_action:
        last_action = unquote(last_action)
    
    response = templates.TemplateResponse(
        'dashboard.html',
        {
            'request': request,
            'users': users_data,
            'total_users': len(users_data),
            'admin': user,
            'last_action': last_action
        }
    )
    
    if last_action:
        response.delete_cookie('last_action')
    
    return response

@app.post('/send_all')
async def send_all(
    request: Request,
    message: str = Form(...)
):
    session_id = request.cookies.get('session_id')
    user = sessions.get(session_id)
    
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    
    await message_admin(message)
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    encoded_value = quote("Рассылка успешно отправлена!")
    response.set_cookie(
        key="last_action",
        value=encoded_value,
        max_age=30
    )
    return response

@app.post('/toggle_tester')
async def toggle_tester(
    request: Request,
    tg_id: int = Form(...)
):
    session_id = request.cookies.get('session_id')
    user = sessions.get(session_id)
    
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    
    async with async_session() as session:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            response = RedirectResponse(url="/dashboard", status_code=303)
            encoded_value = quote("Ошибка: пользователь не найден!")
            response.set_cookie(
                key="last_action",
                value=encoded_value,
                max_age=30
            )
            return response
        
        db_user.tester = not db_user.tester
        await session.commit()
        
        username = db_user.username or f"User_{db_user.tg_id}"
        new_status = "активирован" if db_user.tester else "деактивирован"
        
    response = RedirectResponse(url="/dashboard", status_code=303)
    message = f"Статус тестера для {username} {new_status}!"
    encoded_value = quote(message)
    response.set_cookie(
        key="last_action",
        value=encoded_value,
        max_age=30
    )
    return response

@app.post('/toggle_admin')
async def toggle_admin(
    request: Request,
    tg_id: int = Form(...)
):
    session_id = request.cookies.get('session_id')
    user = sessions.get(session_id)
    
    if not user:
        return RedirectResponse(url='/login', status_code=303)

    is_admin = await check_admin(tg_id)

    if not is_admin:
        await add_admin(tg_id)
        username = await get_username_from_id(tg_id)
    else:
        await remove_admin(tg_id)
        username = await get_username_from_id(tg_id)
        
    response = RedirectResponse(url="/dashboard", status_code=303)
    message = f"Вы забрали права администратора у {username}!" if is_admin else f"Вы выдали права администратора {username}!" 
    encoded_value = quote(message)
    response.set_cookie(
        key="last_action",
        value=encoded_value,
        max_age=30
    )
    return response

@app.post('/update_requests_ai')
async def update_requests_ai(
    request: Request,
    tg_id: int = Form(...),
    amount: int = Form(...)
):
    session_id = request.cookies.get('session_id')
    user = sessions.get(session_id)
    
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    
    async with async_session() as session:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            response = RedirectResponse(url="/dashboard", status_code=303)
            encoded_value = quote("Ошибка: пользователь не найден!")
            response.set_cookie(
                key="last_action",
                value=encoded_value,
                max_age=30
            )
            return response
        
        db_user.requests_ai += amount
        if db_user.requests_ai < 0:
            db_user.requests_ai = 0
        await session.commit()
        
        username = db_user.username or f"User_{db_user.tg_id}"
        new_amount = db_user.requests_ai
        
    response = RedirectResponse(url="/dashboard", status_code=303)
    message = f"AI запросы для {username}: {new_amount}!"
    encoded_value = quote(message)
    response.set_cookie(
        key="last_action",
        value=encoded_value,
        max_age=30
    )
    return response

@app.post('/toggle_shift')
async def toggle_shift(
    request: Request,
    tg_id: int = Form(...)
):
    session_id = request.cookies.get('session_id')
    user = sessions.get(session_id)
    
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    
    async with async_session() as session:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            response = RedirectResponse(url="/dashboard", status_code=303)
            encoded_value = quote("Ошибка: пользователь не найден!")
            response.set_cookie(
                key="last_action",
                value=encoded_value,
                max_age=30
            )
            return response
        
        db_user.shift = 2 if db_user.shift == 1 else 1
        await session.commit()
        
        username = db_user.username or f"User_{db_user.tg_id}"
        new_shift = db_user.shift
        
    response = RedirectResponse(url="/dashboard", status_code=303)
    message = f"Смена для {username} изменена на {new_shift}!"
    encoded_value = quote(message)
    response.set_cookie(
        key="last_action",
        value=encoded_value,
        max_age=30
    )
    return response

@app.get('/edit_texts', response_class=HTMLResponse)
async def edit_texts_page(request: Request):
    session_id = request.cookies.get('session_id')
    user = sessions.get(session_id)
    
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    
    texts = await get_all_strings_ui()
    
    last_action = request.cookies.get('last_action')
    if last_action:
        last_action = unquote(last_action)
    
    response = templates.TemplateResponse(
        'edit_texts.html',
        {
            'request': request,
            'texts': texts,
            'admin': user,
            'last_action': last_action
        }
    )
    
    if last_action:
        response.delete_cookie('last_action')
    
    return response

@app.post('/update_text')
async def update_text(
    request: Request,
    text_id: int = Form(...),
    text_name: str = Form(...),
    text_value: str = Form(...)
):
    session_id = request.cookies.get('session_id')
    user = sessions.get(session_id)
    
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    
    try:
        await change_text_ui(text_name, text_value)
        
        response = RedirectResponse(url="/edit_texts", status_code=303)
        encoded_value = quote(f"Текст '{text_name}' успешно обновлен!")
        response.set_cookie(
            key="last_action",
            value=encoded_value,
            max_age=30
        )
        return response
        
    except Exception as e:
        response = RedirectResponse(url="/edit_texts", status_code=303)
        encoded_value = quote(f"Ошибка при обновлении текста: {str(e)}")
        response.set_cookie(
            key="last_action",
            value=encoded_value,
            max_age=30
        )
        return response

@app.post('/add_text')
async def add_text(
    request: Request,
    text_name: str = Form(...),
    text_value: str = Form(...)
):
    session_id = request.cookies.get('session_id')
    user = sessions.get(session_id)
    
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    
    try:
        from app.database.data import StringsUI
        from app.database.data import async_session
        
        async with async_session() as session:
            new_text = StringsUI(name=text_name, text=text_value)
            session.add(new_text)
            await session.commit()
        
        response = RedirectResponse(url="/edit_texts", status_code=303)
        encoded_value = quote(f"Новый текст '{text_name}' успешно создан!")
        response.set_cookie(
            key="last_action",
            value=encoded_value,
            max_age=30
        )
        return response
        
    except Exception as e:
        response = RedirectResponse(url="/edit_texts", status_code=303)
        encoded_value = quote(f"Ошибка при создании текста: {str(e)}")
        response.set_cookie(
            key="last_action",
            value=encoded_value,
            max_age=30
        )
        return response
