# 🎬 YouTube Video Downloader - Инструкция по установке

## ✅ Что исправлено

Веб-версия теперь работает так же, как Python-версия (55555.py):

1. ✅ **index.html** - Реальная загрузка через PHP (убрана симуляция)
2. ✅ **download.php** - Улучшенная обработка ошибок и форматов
3. ✅ **Sanitize filename** - Безопасные имена файлов для Windows
4. ✅ **Качество видео** - Правильные форматы как в Python
5. ✅ **Обработка ошибок** - Понятные сообщения об ошибках

---

## 🛠 Установка и настройка

### Шаг 1: Установите yt-dlp

**Windows:**
```bash
pip install yt-dlp
```

**Linux/Mac:**
```bash
pip install yt-dlp
# или
brew install yt-dlp
```

### Шаг 2: Настройте download.php

Откройте `download.php` и измените путь к yt-dlp (строки 7-13):

**Windows:**
```php
$YT_DLP_PATH = 'yt-dlp'; // Если yt-dlp в PATH
// или полный путь:
// $YT_DLP_PATH = 'C:\\Python\\Scripts\\yt-dlp.exe';
```

**Linux/Mac:**
```php
$YT_DLP_PATH = '/usr/local/bin/yt-dlp';
// или если в PATH:
// $YT_DLP_PATH = 'yt-dlp';
```

**Проверка пути к yt-dlp:**
```bash
# Windows
where yt-dlp

# Linux/Mac
which yt-dlp
```

### Шаг 3: Запустите веб-сервер

**Вариант 1: PHP встроенный сервер (для тестирования)**
```bash
cd TV
php -S localhost:8000
```

**Вариант 2: XAMPP/OpenServer/WAMP**
1. Скопируйте папку `TV` в htdocs (XAMPP) или domains (OpenServer)
2. Откройте в браузере: `http://localhost/TV/index.html`

### Шаг 4: Проверьте права доступа

**Linux/Mac:**
```bash
chmod +x download.php
mkdir downloads
chmod 755 downloads
```

---

## 🎯 Как пользоваться

1. Откройте `index.html` в браузере
2. Вставьте ссылку на видео (YouTube, Rutube, VK и др.)
3. Выберите качество
4. Нажмите "Скачать видео"
5. Файл загрузится в папку `downloads/` и автоматически начнет скачиваться к вам

---

## 📝 Поддерживаемые платформы

✅ **Работает:**
- YouTube
- Rutube
- VK Video
- Vimeo
- Dailymotion
- TikTok

❌ **НЕ работает напрямую:**
- Яндекс.Видео (нужна оригинальная ссылка)

---

## 🐛 Решение проблем

### Ошибка "yt-dlp not found"
```bash
# Проверьте установку
yt-dlp --version

# Переустановите
pip install -U yt-dlp
```

### Ошибка "Permission denied" (Linux)
```bash
chmod 755 download.php
chmod 755 downloads/
```

### Видео не скачивается
1. Проверьте, что yt-dlp установлен: `yt-dlp --version`
2. Проверьте путь в download.php
3. Попробуйте скачать вручную: `yt-dlp "URL"`
4. Обновите yt-dlp: `pip install -U yt-dlp`

### Ошибка 403/429
```bash
# Обновите yt-dlp
pip install -U yt-dlp

# Подождите несколько минут и попробуйте снова
```

---

## 🔧 Дополнительная настройка

### Изменить папку загрузок
В `download.php` (строка 16):
```php
$DOWNLOAD_DIR = __DIR__ . '/downloads/';
// измените на:
$DOWNLOAD_DIR = '/path/to/your/folder/';
```

### Изменить время хранения файлов
В `download.php` (последние строки):
```php
if ($now - filemtime($file) >= 3600) { // 1 час
// измените на:
if ($now - filemtime($file) >= 7200) { // 2 часа
```

---

## 📊 Сравнение версий

| Функция | 55555.py (Desktop) | Web-версия |
|---------|-------------------|------------|
| Загрузка видео | ✅ | ✅ |
| Выбор качества | ✅ | ✅ |
| Проверка источника | ✅ | ✅ |
| Обработка ошибок | ✅ | ✅ |
| Прогресс загрузки | ✅ Детальный | ✅ Базовый |
| Информация о видео | ✅ | ❌ (можно добавить) |
| Очистка имени файла | ✅ | ✅ |

---

## 🚀 Готово!

Теперь веб-версия работает так же надежно, как Python-версия!

**Запуск:**
```bash
# PHP сервер
cd TV
php -S localhost:8000

# Откройте в браузере
http://localhost:8000/index.html
```
