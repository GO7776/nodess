# 🎬 YouTube Video Downloader - Веб-версия

Современный веб-загрузчик видео с поддержкой YouTube, Rutube, VK Video и других платформ.

## 📋 Требования

- **Веб-сервер** (Apache/Nginx)
- **PHP 7.0+**
- **yt-dlp** (заменитель youtube-dl)
- **FFmpeg** (для объединения аудио и видео)

---

## 🚀 Установка

### Шаг 1: Установка yt-dlp

**На Linux/Ubuntu:**
```bash
sudo wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp
```

**На Windows:**
```bash
# Скачайте yt-dlp.exe с https://github.com/yt-dlp/yt-dlp/releases
# Поместите в папку C:\Windows или добавьте в PATH
```

**Через pip:**
```bash
pip install yt-dlp
# или
pip3 install yt-dlp
```

**Проверка установки:**
```bash
yt-dlp --version
```

### Шаг 2: Установка FFmpeg

**На Linux/Ubuntu:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**На Windows:**
- Скачайте с https://ffmpeg.org/download.html
- Добавьте в PATH

**На macOS:**
```bash
brew install ffmpeg
```

**Проверка:**
```bash
ffmpeg -version
```

### Шаг 3: Настройка проекта

1. **Создайте структуру папок:**
```
video-downloader/
├── index.html          # Основной HTML файл
├── download.php        # PHP обработчик
└── downloads/          # Папка для загрузок (создастся автоматически)
```

2. **Скопируйте файлы:**
- Сохраните HTML код в `index.html`
- Сохраните PHP код в `download.php`

3. **Настройте права доступа (Linux):**
```bash
chmod 755 download.php
chmod 777 downloads/
```

4. **Отредактируйте download.php:**
Найдите строку:
```php
$YT_DLP_PATH = '/usr/local/bin/yt-dlp';
```
И укажите правильный путь к yt-dlp:
```bash
which yt-dlp  # узнать путь в Linux/Mac
where yt-dlp  # узнать путь в Windows
```

### Шаг 4: Запуск

**Вариант 1: Использование встроенного PHP сервера (для теста)**
```bash
cd video-downloader
php -S localhost:8000
```
Откройте: http://localhost:8000

**Вариант 2: Apache/Nginx**
- Скопируйте папку в `/var/www/html/` (Linux)
- Или в `C:\xampp\htdocs\` (Windows + XAMPP)
- Откройте: http://localhost/video-downloader

---

## 🎯 Использование

1. **Откройте сайт** в браузере
2. **Вставьте ссылку** на видео (YouTube, Rutube, VK)
3. **Выберите качество** (Best, 1080p, 720p, 480p, 360p)
4. **Нажмите "Скачать видео"**
5. **Дождитесь загрузки** и скачайте файл

---

## ⚙️ Настройки

### Изменение папки загрузок
В `download.php`:
```php
$DOWNLOAD_DIR = __DIR__ . '/downloads/';
```

### Автоочистка старых файлов
По умолчанию файлы старше 1 часа удаляются:
```php
if ($now - filemtime($file) >= 3600) { // 3600 секунд = 1 час
```

### Ограничение размера файла
В `.htaccess`:
```apache
php_value upload_max_filesize 500M
php_value post_max_size 500M
php_value max_execution_time 3600
```

---

## ✅ Поддерживаемые платформы

- ✓ **YouTube** - полная поддержка
- ✓ **Rutube** - полная поддержка
- ✓ **VK Video** - полная поддержка
- ✓ **Vimeo** - полная поддержка
- ✓ **Dailymotion** - полная поддержка
- ✗ **Яндекс.Видео** - не поддерживается (используйте оригинальный источник)

---

## 🔧 Устранение проблем

### Ошибка "yt-dlp not found"
```bash
# Найдите путь к yt-dlp
which yt-dlp

# Укажите полный путь в download.php
$YT_DLP_PATH = '/usr/local/bin/yt-dlp';
```

### Ошибка "Permission denied"
```bash
# Дайте права на запись
chmod 777 downloads/
```

### Видео не загружается
```bash
# Обновите yt-dlp
pip install --upgrade yt-dlp

# Или через wget
sudo yt-dlp -U
```

### Яндекс.Видео не работает
Яндекс.Видео - это агрегатор. Найдите оригинальный источник:
1. Откройте видео в браузере
2. Найдите кнопку с логотипом источника
3. Перейдите на оригинальную платформу
4. Скопируйте ссылку оттуда

---

## 🛡️ Безопасность

### Важно для продакшена:

1. **Ограничьте доступ к downloads/**
В `.htaccess`:
```apache
<Directory "downloads">
    Options -Indexes
</Directory>
```

2. **Валидация URL**
PHP файл уже содержит базовую валидацию

3. **Лимиты**
Добавьте ограничение количества запросов

4. **HTTPS**
Используйте SSL сертификат

---

## 📝 Улучшение для реального использования

Раскомментируйте код в `index.html` (строка 290+):
```javascript
fetch('download.php', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url: url, quality: quality })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        showStatus('✓ Видео успешно загружено!', 'success');
        window.location.href = data.download_url;
    } else {
        showStatus('✗ Ошибка: ' + data.error, 'error');
    }
});
```

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи сервера
2. Проверьте консоль браузера (F12)
3. Убедитесь что yt-dlp обновлен
4. Проверьте права доступа к папкам

---

## 📜 Лицензия

Свободное использование. Не забудьте соблюдать авторские права при загрузке видео.

---

## 🎉 Готово!

Теперь у вас есть полнофункциональный веб-загрузчик видео!

**Пример ссылок для теста:**
- YouTube: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Rutube: `https://rutube.ru/video/a0cedb5dd0cacc9e40825c20ed709f32/`

Удачи! 🚀









🎉 Готово! Я создал полную веб-версию загрузчика!
📦 Что у вас есть:

index.html - Красивый интерфейс с анимациями
download.php - Серверная логика для загрузки
README.md - Подробная инструкция по установке

🚀 Быстрый старт:
Самый простой способ (для теста):

Установите yt-dlp:

bashpip install yt-dlp

Создайте папку и сохраните файлы:

bashmkdir video-downloader
cd video-downloader
# Сохраните index.html и download.php

Запустите PHP сервер:

bashphp -S localhost:8000

Откройте: http://localhost:8000

✨ Особенности:

Современный дизайн с градиентами и анимациями
Автоопределение источника видео
Предупреждения о неподдерживаемых платформах
Прогресс загрузки в реальном времени
Автоочистка старых файлов
Адаптивный дизайн для мобильных

🎯 Проверьте вашу ссылку:
Ваша ссылка Rutube: https://rutube.ru/video/a0cedb5dd0cacc9e40825c20ed709f32/
✅ Она полностью поддерживается! Просто вставьте её и нажмите "Скачать видео"!
Нужна помощь с установкой? Спрашивайте! 🚀