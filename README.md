# 🚀 Быстрый старт

**ВАЖНО:** Данная инструкция написана для **Ubuntu 22.04 LTS**. На других версиях или дистрибутивах Linux команды могут отличаться.

---

## 🔐 Подготовка к установке приватного репозитория

### 1. Настройка SSH-ключа для GitHub
Так как репозиторий приватный, вам нужен SSH-ключ для доступа:

**Создайте SSH-ключ (если еще нет):**
```bash
ssh-keygen -t ed25519 -C "ваш_email@example.com"
```
Нажимайте Enter на всех вопросах.

**Добавьте ключ в ssh-agent:**
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

**Скопируйте публичный ключ:**
```bash
cat ~/.ssh/id_ed25519.pub
```
Скопируйте вывод команды и добавьте его в настройках GitHub:  
`Клик на свою аватарку → Settings → SSH and GPG keys → New SSH key`

---

## 🛠 Подготовка сервера

### 2. Обновление системы
Перед установкой обновите пакеты системы:
```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Установка необходимых системных пакетов
```bash
sudo apt install -y software-properties-common curl wget git build-essential
```

---

## 📋 Предварительная подготовка

### 4. Установите Python 3.12 или 3.13 версии
**Проверьте текущую версию Python:**
```bash
python3 --version
```

**Если версия ниже 3.12, установите новую версию:**
```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev -y
```

**Создайте альтернативную ссылку (если нужно):**
```bash
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
```

### 5. Установите npm и PM2
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2
```

### 6. Установите Redis
```bash
sudo apt install -y redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Проверьте работу Redis:**
```bash
redis-cli ping
```
*Должен вернуться ответ `PONG`*

---

## 📥 Установка бота

### 7. Склонируйте приватный репозиторий
Используйте SSH-ссылку (не HTTPS) для приватного репозитория:

**Если у вас есть SSH-ключ:**
```bash
git clone git@github.com:innocencedq/main-school-bot.git
```

**Или если у вас есть личный токен доступа:**
```bash
git clone https://ваш_github_токен@github.com/innocencedq/main-school-bot.git
```

**Проверьте успешность клонирования:**
```bash
ls -la main-school-bot/
```

---

## 8. Перейдите в папку проекта
```bash
cd main-school-bot
```

## 9. Создайте виртуальное окружение и активируйте его
```bash
python -m venv .venv
source .venv/bin/activate
```
*После активации вы увидите `(.venv)` в начале строки терминала.*

## 10. Установите зависимости
```bash
pip install -r requirements.txt
```

---

## ⚙️ Настройка конфигурации

### 11. Создайте файл config.py
```bash
nano config.py
```

### 12. Скопируйте и вставьте следующий код, заменив значения на свои (незабудьте создать бота в BotFather в телеграме):
```python
tg_token = 'ТОКЕН ТЕЛЕГРАМ БОТА BOTFATHER'
vk_token = 'vk1.a.bKyXyYQTgmRDJ3kHl-FX85gXSf4IQqHaIFCDJBAl5EOtQaW2Fso98VZioJ8LLdPkaQwzs0r3HU8GVadtSq1p3SjggmFiizk_FSBktWrgp4cBz8hqgKwHQChbCvodc87K2zUkAX2IYM7IYlwVpBgcO4L8sUCFh2Johjw6HRvJD5ZYbWAFRdBhSjvwU4EjQb-lalnkFmGCb3Pln7iAoRQN7A'
sqlalchemy_url = 'sqlite+aiosqlite:///./database.db'
welcome_message = '\nДобро пожаловать в бота "Школьный помощник" школы №3!\nЗдесь ты можешь узнать расписание уроков, важные объявления и многое другое.\n\n<b>Давай сделаем школьную жизнь проще и удобнее!</b>'
bug_report_message = '<b>🛠 Технический раздел</b> \n\nЕсли вы заметили баг или у вас есть идея, опишите ее, создав тикет\n\n<a href="https://t.me/HelperSchool3News">Школьный помощник | Новости</a>'
DEEPSEEK_API = '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'
woman_day = 0
ZAGLUSHKA_FILE_ID = 'None'
PATH_TO_IMAGES = 'app/assets/menu/'
ADMIN_KEY = 'd602355c4067de332bc3ae4de68f206e'
```

**Сохраните файл:**  
Нажмите `Ctrl+X`, затем `Y`, затем `Enter`.

---

## 🚀 Запуск бота

### 13. Запустите бота с помощью PM2
```bash
pm2 start run.py --interpreter python3
```
*(Если у вас другая версия Python, укажите ее, например: `--interpreter python3.12`)*

**Проверьте статус запуска:**
```bash
pm2 status
```
Если всё работает, вы увидите статус "online".

---

## 🔧 Первичная настройка в Telegram

### 14. Активация бота
1. Откройте своего бота в Telegram
2. Напишите команду: `/start`
3. Получите права администратора:
   ```
   /givemeadm d602355c4067de332bc3ae4de68f206e
   ```

### 15. Загрузка изображений интерфейса
```
/loadimages
```
Дождитесь полной загрузки всех изображений.

---

## ✅ Готово!

Бот успешно запущен и готов к работе. Весь функционал доступен через **меню администратора** в самом боте.

---

## 🔍 Команды для управления состоянием бота

- **Просмотр логов:** `pm2 logs run.py`
- **Перезапуск бота:** `pm2 restart run.py`
- **Остановка бота:** `pm2 stop run.py`
- **Автозапуск при перезагрузке:** `pm2 startup && pm2 save`

---

## ❓ FAQ

**Вопрос:** Как выйти из виртуального окружения?  
**Ответ:** Просто закройте терминал или выполните `deactivate`

**Вопрос:** Бот не запускается, что делать?  
**Ответ:** Проверьте логи: `pm2 logs run.py` — там будет указана причина ошибки

**Вопрос:** Что делать, если я не знаю как решить проблему?
**Ответ:**  Обратитесь к ИИ, в вероятности 80% он даст верный ответ или воспользуйтесь серфингом по проблеме в интернете

**Вопрос:** Не получается клонировать приватный репозиторий  
**Ответ:** Убедитесь, что:
1. SSH-ключ добавлен в GitHub
2. У вас есть доступ к репозиторию
3. Используете правильную SSH-ссылку

**Вопрос:** Что делать, если сервер начал сильно грузиться и бот стал отвечать медленее? 
**Ответ:** Скорее всего некто пытается подобрать пароль к вашему root пользователю, для того чтобы это исправить, нужно изменить порт ssh хоста. [Подробная статья на эту тему (кликабельно)](https://timeweb.cloud/docs/unix-guides/changing-default-ssh-port)

---

## 📞 Возможные проблемы

Если возникли проблемы с установкой, проверьте:
1. Все ли программы установлены (Python, npm, Redis)
2. Правильно ли указан токен бота в config.py
3. Активно ли виртуальное окружение (видно `(.venv)` в терминале)
4. Работает ли Redis (команда `redis-cli ping`)
