import json
from app.database.data import User, async_session, Admin, Images, Advert, ReportTicket, Valentines, InprocessValentines
from sqlalchemy import exists, select, func, update, delete, desc, text

from app.components.routers.tickets.topics import create_topic
from app.components.logs.logs import logger
from app.supportfunctions.redis_misc import redis


async def get_all_users():
    async with async_session() as session:
        users = await session.scalars(select(User.tg_id))
        users_id = users.all()
        return users_id
    

async def is_user_exists(user, method: str = 'id') -> bool:
    """
        Entered:
            - user_id (chat_id)
            - method (id, username)
        Returned:
            - bool value (True, False)
    """
    async with async_session() as session:
        if method == 'id':
            user_exists = await session.scalar(
                select(exists().where(User.tg_id == user))
            )
            return bool(user_exists)
        elif method == 'username':
            user_exists = await session.scalar(
                select(exists().where(User.username == user))
            )
            return bool(user_exists)

    

async def get_full_info_user(user, method: str = 'id'):
    """
    Returned:
        - id (int)
        - tg_id (int)
        - username (str)
        - date_started (datetime)
        - notify_vk (bool)
        - quick_menu (bool)
        - requests_ai (int)
        - refresh_token (str)
        - access_token (str)
        - shift (bool)
        - extented_diary (bool)
        - tester (bool)
        - notify_diary (bool)

    Methods:
        - id
        - username
        
    """
    async with async_session() as session:
        if method == 'id':
            stmt = await session.scalar(select(User).where(User.tg_id == user))
        elif method == 'username':
            stmt = await session.scalar(select(User).where(User.username == user))


        if stmt:
            res = {
                "id": stmt.id,
                "tg_id": stmt.tg_id,
                "username": stmt.username,
                "date_started": stmt.date_started,
                "notify_vk": stmt.notify_vk,
                "quick_menu": stmt.quick_menu,
                "requests_ai": stmt.requests_ai,
                "refresh_token": stmt.refresh_token,
                "access_token": stmt.access_token,
                "shift": stmt.shift,
                "extented_diary": stmt.extended_diary,
                "tester": stmt.tester,
                "notify_diary": stmt.notify_diary,
                "allow_valentines": stmt.allow_valentines
            }
        else:
            return 'invalid-user'

        return res
    

async def create_user(id, username):
    async with async_session() as session:
        username = username if username else "unspecific_user"
        new_user = User(
                     tg_id=id,
                     username=username,)

        session.add(new_user)
        await session.commit()


async def get_all_users_with_notify():
    async with async_session() as session:
        value = await session.scalars(select(User.tg_id).filter_by(notify_vk=True))
        value = value.all()
        return value
    

async def get_all_users_with_notify_mark():
    async with async_session() as session:
        value = await session.scalars(select(User.tg_id).filter_by(notify_diary=True))
        value = value.all()
        return {"users": value}
    

async def get_user_with_notify_mark(user):
    async with async_session() as session:
        value = await session.scalar(select(User.notify_diary).where(User.tg_id == user))
        return value
    

async def get_user_with_notify(user):
    async with async_session() as session:
        value = await session.scalar(select(User.notify_vk).where(User.tg_id == user))
        return value


async def get_list_admin():
    async with async_session() as session:
        admins = await session.scalars(select(Admin.tg_id))
        admins_id = admins.all()
        return admins_id
    

async def get_developer_chat_id():
    async with async_session() as session:
        develop = await session.scalar(select(Admin.tg_id).where(Admin.username == 'developer'))
        return develop
    

async def update_status_developer(id, username):
    async with async_session() as session:
        develop_chat_id = await get_developer_chat_id()

        if develop_chat_id == id:
            stmt = update(Admin).where(Admin.tg_id == id).values(username = username)
            await session.execute(stmt)
            await session.commit()
            
            return 'admin'
        else:
            stmt = update(Admin).where(Admin.tg_id == id).values(username = 'developer')
            await session.execute(stmt)
            await session.commit()

            return 'developer'


async def get_list_username(user):
    async with async_session() as session:
        usernames = await session.scalars(select(User.username).filter_by(username=user))
        usernames_id = usernames.all()
        return usernames_id


async def get_username_with_id(username):
    async with async_session() as session:
        chat_id = await session.scalars(select(User.tg_id).filter_by(username=username))
        chat_id = chat_id.all()
        return chat_id


async def get_image(week_name):
    res = await redis.get(name="week_name:" + week_name)
    if not res:
        async with async_session() as session:
            image_id = await session.scalar(select(Images.image_id).where(Images.image_name == week_name))
            await redis.set(name="week_name:" + week_name, value=image_id)
            return str(image_id)
    else:
        return res.decode('utf-8') if isinstance(res, bytes) else res
    

async def refresh_image(img_id, img_name):
    async with async_session() as session:
        stmt = update(Images).where(Images.image_name == img_name).values(image_id = img_id)
        await session.execute(stmt)
        await session.commit()
        
        await redis.delete('week_name:' + str(img_name))
    

async def load_image(img_id, img_name):
    async with async_session() as session:
        new_image = Images(
            image_id = img_id,
            image_name = img_name
        )
        session.add(new_image)
        await session.commit()

async def del_image_from_redis(week_name):
    await redis.delete(f'week_name:{week_name}')


async def get_requests_ai(user):
    async with async_session() as session:
        count = await session.scalar(select(User.requests_ai).where(User.tg_id == user))
        return count


async def count_users() -> int:
    async with async_session() as session:
        result = select(func.count(User.tg_id))
        result = await session.execute(result)
        return result.scalar()


async def get_quick_menu(user):
    async with async_session() as session:
        value = await session.scalar(select(User.quick_menu).where(User.tg_id == user))
        return value
    

async def get_refresh_token(user):
    async with async_session() as session:
        refresh_token = await session.scalar(select(User.refresh_token).where(User.tg_id == user))
        return refresh_token
    

async def get_access_token(user):
    async with async_session() as session:
        access_token = await session.scalar(select(User.access_token).where(User.tg_id == user))
        await redis.set(name="access_token:" + str(user), value=access_token)
        return access_token
    

async def update_tokens(access_token, refresh_token, user):
    async with async_session() as session:
        stmt = update(User).where(User.tg_id == user).values(access_token = access_token, refresh_token = refresh_token)
        await session.execute(stmt)
        await session.commit()


async def get_tester(user):
    async with async_session() as session:
        res = await session.scalar(select(User.tester).where(User.tg_id == user))
        return res
    

async def get_user_with_extended_diary(user):
    async with async_session() as session:
        res = await session.scalar(select(User.extended_diary).where(User.tg_id == user))
        return res
    

async def add_admin(telegram_id, username: str = None):
    await redis.delete('check_admin:' + str(telegram_id))
    async with async_session() as session:
        new_adm = Admin(
                    tg_id=telegram_id,
                    username=username if username else 'unspecified_admin',
                )
        session.add(new_adm)
        await session.commit()
        await redis.set(name="check_admin:" + str(telegram_id), value=1, ex=21600)


async def check_admin(user):
    res = await redis.get(name="check_admin:" + str(user))
    if not res:
        async with async_session() as session:
            sql_res = await session.scalar(select(Admin).where(Admin.tg_id == user))
            await redis.set(name="check_admin:" + str(user), value=1 if sql_res else 0, ex=21600)
            return bool(sql_res)
    else:
        return bool(int(res))


async def delete_user(user):
    async with async_session() as session:
        stmt = (delete(User).where(User.tg_id == user))
        await session.execute(stmt)
        await session.commit()


async def advert_write_sql(advert_title, advert_description, advert_image_id: str = None):
    async with async_session() as session:
        try:
            stmt = Advert(
                title = advert_title,
                description = advert_description,
                file_id = advert_image_id if advert_image_id else None
            )
            session.add(stmt)
            await session.commit()
        except Exception as e:
            await logger.info(f'Error in advert_write_sql -> {e}')


async def get_last_advert_id():
    res = await redis.get(name='last:advert:id')
    if not res:
        async with async_session() as session:
            stmt = await session.scalar(select(Advert.id).order_by(desc(Advert.id)).limit(1))
            await redis.set(name='last:advert:id', value=str(stmt))
            return stmt
    else:
        return int(res if res != b'None' else 0)
    

async def refresh_last_advert_id():
    await redis.delete('last:advert:id')


async def get_all_data_about_advert(id):
    async with async_session() as session:
        try:
            stmt = await session.scalar(select(Advert).where(Advert.id == id))
            res = {
                "id": stmt.id,
                "title": stmt.title,
                "description": stmt.description,
                "image_id": stmt.file_id,
                "date": stmt.date_created
            }
            return res
        
        except AttributeError:
            return None
    

async def update_data_about_advert(id, advert_title, advert_desc, advert_image):
    async with async_session() as session:
        stmt = update(Advert).where(Advert.id == id).values(title = advert_title,
                                                            description = advert_desc,
                                                            file_id = advert_image)
        await session.execute(stmt)
        await session.commit()


async def deleting_data_about_advert(id):
    async with async_session() as session:
        stmt = (delete(Advert).where(Advert.id == id))
        await session.execute(stmt)

        result = await session.execute(select(Advert).order_by(Advert.id))
        items = result.scalars().all()

        for index, item in enumerate(items, start=1):
            if item.id != index:
                await session.execute(
                    text(f"UPDATE advert SET id = {index} WHERE id = {item.id}")
                )
        
        await session.commit()


async def create_ticket(username, id, message):
    async with async_session() as session:
        stmt = ReportTicket(
            from_username = username,
            from_id = id,
            topic = 'not_created'
        )
        session.add(stmt)
        await session.commit()
        await session.refresh(stmt)

        ticket_id = stmt.id
        topic = await create_topic(ticket_id, message, username, id)

        stmt = update(ReportTicket).where(ReportTicket.id == ticket_id).values(topic=topic)
        await session.execute(stmt)
        await session.commit()


async def get_info_ticket(id, method: str):
    async with async_session() as session:
        if method == 'telegram':
            stmt = await session.scalar(select(ReportTicket).where(ReportTicket.from_id == id, ReportTicket.closed == False))

        elif method == 'id':
            stmt = await session.scalar(select(ReportTicket).where(ReportTicket.id == id, ReportTicket.closed == False))
        
        elif method == 'topic':
            stmt = await session.scalar(select(ReportTicket).where(ReportTicket.topic == id, ReportTicket.closed == False))

        res = {
            "id": stmt.id,
            "from_username": stmt.from_username,
            "from_id": stmt.from_id,
            "closed": stmt.closed,
            "topic": stmt.topic
        }
        return res
    

async def close_ticket(id, method: str):
    async with async_session() as session:
        if method == 'topic':
            stmt = (update(ReportTicket).where(ReportTicket.topic == id).values(closed=True))
        elif method == 'telegram':
            stmt = (update(ReportTicket).where(ReportTicket.from_id == id).values(closed=True))
        elif method == 'id':
            stmt = (update(ReportTicket).where(ReportTicket.id == id).values(closed=True))

        await session.execute(stmt)
        await session.commit()
    

async def get_list_open_tickets():
    async with async_session() as session:
        stmt = await session.scalars(select(ReportTicket.id).filter_by(closed=False))
        stmt = stmt.all()
        return stmt
    

async def check_status_topic(id, method: str):
    async with async_session() as session:
        if method == 'telegram':
            stmt = await session.scalar(select(ReportTicket.closed).where(ReportTicket.from_id == id, ReportTicket.closed == False))

        elif method == 'id':
            stmt = await session.scalar(select(ReportTicket.closed).where(ReportTicket.id == id, ReportTicket.closed == False))
        
        elif method == 'topic':
            stmt = await session.scalar(select(ReportTicket.closed).where(ReportTicket.topic == id, ReportTicket.closed == False))
        
        return bool(stmt)


async def get_shift(id):
    res = await redis.get(name='user:shift:' + str(id))
    if not res:
        async with async_session() as session:
            stmt = await session.scalar(select(User.shift).where(User.tg_id == int(id)))
            await redis.set(name="user:shift:" + str(id), value=stmt)
            return stmt
    else:
        return res.decode('utf-8') if isinstance(res, bytes) else res
        

async def change_user_shift(id, choosed):
    async with async_session() as session:
        stmt = update(User).where(User.tg_id == id).values(shift = choosed)
        await session.execute(stmt)
        await session.commit()
        await redis.delete("user:shift:" + str(id))


async def get_unread_valentines(id):
    async with async_session() as session:
        result = select(func.count(Valentines.id)).where(Valentines.receiver_id == id, 
                                                         Valentines.is_read == False)
        result = await session.execute(result)
        return result.scalar()
    

async def get_ids_valentines(id):
    redis_data = await redis.get(name='user-list-valentines:' + str(id))
    
    if redis_data is not None:
        res = json.loads(redis_data)
        return res
    
    async with async_session() as session:
        stmt = await session.scalars(select(Valentines.id).filter_by(receiver_id=id))
        result = stmt.all()
        if result:
            await redis.set(
                name='user-list-valentines:' + str(id), 
                value=json.dumps(result), 
                ex=21600
            )
        
        return result
    

async def is_sending_allowed(id) -> bool:
    async with async_session() as session:
        stmt = await session.scalar(select(User.allow_valentines).where(User.tg_id == id))
        return bool(stmt)


async def create_valentine_user(receiver_id, sender_id, message, method: str = 'id'):
    async with async_session() as session:
        if method == 'id':
            creation = Valentines(
                receiver_id = receiver_id,
                sender_id = sender_id,
                message = message
            )
            session.add(creation)
            await session.commit()
            await session.refresh(creation)
            await redis.delete('user-list-valentines:' + str(receiver_id))

            return creation.id
        
        elif method == 'username':
            creation = InprocessValentines(
                receiver_username = receiver_id,
                sender_id = sender_id,
                message = message
            )
            session.add(creation)
            await session.commit()


async def get_info_about_valentine(valentine_id):
    """
    Returned:
        - id (int)
        - receiver_id (int)
        - sender_id (int)
        - message (str)
        - is_read (bool)
        - may_react (bool)
    """
    redis_key = 'valentine-info:' + str(valentine_id)

    redis_data = await redis.get(name=redis_key)
    if redis_data:
        return json.loads(redis_data)

    async with async_session() as session:
        stmt = await session.scalar(select(Valentines).where(Valentines.id == valentine_id))
        
        result = {
            "id": stmt.id,
            "receiver_id": stmt.receiver_id,
            "sender_id": stmt.sender_id,
            "message": stmt.message,
            "is_read": stmt.is_read,
            "may_react": stmt.may_react
        }
        
        await redis.set(
            name=redis_key,
            value=json.dumps(result),
            ex=21600
        )
        
        return result
    

async def update_reading_valentine(id):
    async with async_session() as session:
        stmt = update(Valentines).where(Valentines.id == id).values(is_read = True)
        await session.execute(stmt)
        await session.commit()
        await redis.delete('valentine-info:' + str(id))


async def update_rights_react(id):
    async with async_session() as session:
        stmt = update(Valentines).where(Valentines.id == id).values(may_react = False)
        await session.execute(stmt)
        await session.commit()
        await redis.delete('valentine-info:' + str(id))


async def is_sending_before(receiver_username, sender_id):
    async with async_session() as session:
        data = await get_full_info_user(receiver_username, 'username')
        if data != 'invalid-user':
            receiver_id = data.get('tg_id')
            stmt = await session.scalar(select(Valentines).where(Valentines.receiver_id == receiver_id, Valentines.sender_id == sender_id))
        else:
            stmt = await session.scalar(select(InprocessValentines).where(InprocessValentines.sender_id == sender_id, InprocessValentines.receiver_username == receiver_username))

        return bool(stmt)
    

async def get_user_for_profile_info(id):
    """
    Returned:
        - count_sents (int)
        - count_received (int)
    """
    async with async_session() as session:
        stmt = select(func.count(Valentines.id)).where(Valentines.receiver_id == id)
        stmt2 = select(func.count(Valentines.id)).where(Valentines.sender_id == id)

        count_sents = await session.execute(stmt2)
        count_received = await session.execute(stmt)

        return count_sents.scalar(), count_received.scalar()
    

async def change_allow_valentines(id):
    async with async_session() as session:
        data = await get_full_info_user(id, 'id')
        status = data.get('allow_valentines')
        
        if status:
            stmt = update(User).where(User.tg_id == id).values(allow_valentines = False)
            await session.execute(stmt)
            await session.commit()
        else:
            stmt = update(User).where(User.tg_id == id).values(allow_valentines = True)
            await session.execute(stmt)
            await session.commit()


async def get_ids_valentinesinprocess(username):
    async with async_session() as session:
        stmt = await session.scalars(select(InprocessValentines.id).filter_by(receiver_username=username))
        result = stmt.all()
        
        return result
    

async def delete_valentineinprocess(id):
    async with async_session() as session:
        stmt = (delete(InprocessValentines).where(InprocessValentines.id == id))
        await session.execute(stmt)
        await session.commit()


async def change_tables_info_valentine(chat_id, username):
    async with async_session() as session:
        stmt = await session.scalars(select(InprocessValentines).where(InprocessValentines.receiver_username == username))
        res1 = stmt.all()

        if res1:
            for valentine in res1:
                valentine_id = valentine.id
                sender_id = valentine.sender_id
                message = valentine.message

                creation = Valentines(
                    receiver_id=chat_id,
                    sender_id=sender_id,
                    message=message
                )

                session.add(creation)
                await session.commit()

                await delete_valentineinprocess(valentine_id)

            return 'has_valentines'
        else:
            return 'hasnt_valentines'