import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
import re

try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("Установите yt-dlp: pip install yt-dlp")
    exit(1)


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader Pro")
        self.root.geometry("750x650")
        self.root.resizable(False, False)
        
        # Переменные
        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.is_downloading = False
        self.download_thread = None
        
        self.create_widgets()
    
    def sanitize_filename(self, filename):
        """Очистка имени файла от запрещенных символов Windows"""
        # Запрещенные символы в Windows: \ / : * ? " < > |
        forbidden_chars = r'[<>:"/\\|?*]'
        # Заменяем на подчеркивание
        clean_name = re.sub(forbidden_chars, '_', filename)
        # Убираем точки в конце (Windows не любит)
        clean_name = clean_name.rstrip('.')
        # Ограничиваем длину (Windows лимит 255 символов)
        if len(clean_name) > 200:
            clean_name = clean_name[:200]
        return clean_name
    
    def create_widgets(self):
        # Основной фрейм с отступами
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Заголовок
        title_label = tk.Label(
            main_frame, 
            text="YouTube Video Downloader Pro", 
            font=("Arial", 18, "bold"),
            fg="#1976D2"
        )
        title_label.pack(pady=(0, 10))
        
        # Предупреждение о Яндекс.Видео
        warning_frame = tk.Frame(main_frame, bg="#FFF3CD", relief="solid", bd=1)
        warning_frame.pack(fill="x", pady=(0, 15))
        
        warning_text = tk.Label(
            warning_frame,
            text="⚠ Для видео с Яндекс.Видео:\nОткройте видео → найдите оригинальный источник (YouTube/Rutube/VK)\nИли используйте расширение для браузера",
            font=("Arial", 8),
            bg="#FFF3CD",
            fg="#856404",
            justify="left",
            padx=10,
            pady=8
        )
        warning_text.pack()
        
        # Фрейм для URL
        url_frame = tk.LabelFrame(main_frame, text="URL видео (вставьте прямую ссылку)", 
                                  font=("Arial", 10, "bold"), padx=10, pady=10)
        url_frame.pack(fill="x", pady=(0, 10))
        
        # Используем Text вместо Entry для лучшей поддержки вставки
        self.url_text = tk.Text(url_frame, height=3, font=("Arial", 10), wrap="word")
        self.url_text.pack(fill="x")
        
        # Привязываем события
        self.url_text.bind('<Control-v>', self.on_paste)
        self.url_text.bind('<Command-v>', self.on_paste)  # для macOS
        self.url_text.bind('<Return>', self.on_enter)
        self.url_text.bind('<Button-3>', self.show_context_menu)
        self.url_text.bind('<FocusIn>', self.on_focus)
        
        # Создаем контекстное меню
        self.create_context_menu()
        
        # Кнопки управления
        btn_frame = tk.Frame(url_frame)
        btn_frame.pack(pady=(5, 0), fill="x")
        
        clear_btn = tk.Button(
            btn_frame,
            text="Очистить",
            command=self.clear_url,
            font=("Arial", 8),
            bg="#FFE0E0",
            cursor="hand2"
        )
        clear_btn.pack(side="left")
        
        check_btn = tk.Button(
            btn_frame,
            text="Проверить ссылку",
            command=self.check_url,
            font=("Arial", 8),
            bg="#E3F2FD",
            cursor="hand2"
        )
        check_btn.pack(side="left", padx=5)
        
        info_btn = tk.Button(
            btn_frame,
            text="Получить инфо",
            command=self.get_video_info,
            font=("Arial", 8),
            bg="#E8F5E9",
            cursor="hand2"
        )
        info_btn.pack(side="left")
        
        # Фрейм с поддерживаемыми платформами
        support_frame = tk.LabelFrame(main_frame, text="Поддерживаемые платформы", 
                                      font=("Arial", 9, "bold"), padx=10, pady=5)
        support_frame.pack(fill="x", pady=(0, 10))
        
        support_text = tk.Label(
            support_frame,
            text="✓ YouTube  ✓ Rutube  ✓ VK Video  ✓ Vimeo  ✓ Dailymotion  ✓ TikTok\n✗ Яндекс.Видео (только оригинальные источники)",
            font=("Arial", 8),
            fg="#666666",
            justify="center"
        )
        support_text.pack()
        
        # Фрейм для выбора папки
        path_frame = tk.LabelFrame(main_frame, text="Папка для сохранения", 
                                   font=("Arial", 10, "bold"), padx=10, pady=10)
        path_frame.pack(fill="x", pady=(0, 10))
        
        path_select_frame = tk.Frame(path_frame)
        path_select_frame.pack(fill="x")
        
        path_entry = tk.Entry(
            path_select_frame, 
            textvariable=self.download_path, 
            font=("Arial", 10),
            state="readonly"
        )
        path_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = tk.Button(
            path_select_frame, 
            text="Обзор", 
            command=self.browse_folder,
            font=("Arial", 9),
            bg="#E3F2FD",
            cursor="hand2"
        )
        browse_btn.pack(side="left", padx=(5, 0))
        
        open_btn = tk.Button(
            path_select_frame, 
            text="Открыть папку", 
            command=self.open_download_folder,
            font=("Arial", 9),
            bg="#E8F5E9",
            cursor="hand2"
        )
        open_btn.pack(side="left", padx=(5, 0))
        
        # Выбор качества
        quality_frame = tk.LabelFrame(main_frame, text="Качество видео", 
                                     font=("Arial", 10, "bold"), padx=10, pady=10)
        quality_frame.pack(fill="x", pady=(0, 10))
        
        self.quality_var = tk.StringVar(value="best")
        quality_options = [
            ("Лучшее качество (авто)", "best"),
            ("1080p (Full HD)", "1080"),
            ("720p (HD)", "720"),
            ("480p (SD)", "480"),
            ("360p (низкое)", "360")
        ]
        
        for text, value in quality_options:
            tk.Radiobutton(
                quality_frame, 
                text=text, 
                variable=self.quality_var, 
                value=value,
                font=("Arial", 9)
            ).pack(anchor="w", pady=2)
        
        # Кнопка загрузки
        self.download_btn = tk.Button(
            main_frame, 
            text="СКАЧАТЬ ВИДЕО", 
            command=self.start_download,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=25,
            height=2,
            cursor="hand2",
            relief="raised",
            bd=3
        )
        self.download_btn.pack(pady=10)
        
        # Прогресс бар
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill="x", pady=(0, 10))
        
        self.progress = ttk.Progressbar(
            progress_frame, 
            length=650, 
            mode='determinate'
        )
        self.progress.pack()
        
        # Статус
        self.status_label = tk.Label(
            main_frame, 
            text="Готов к загрузке", 
            font=("Arial", 10, "bold"),
            fg="#4CAF50"
        )
        self.status_label.pack(pady=5)
        
        # Информация внизу
        info_label = tk.Label(
            main_frame,
            text="Совет: Вставьте прямую ссылку на видео (Ctrl+V) и нажмите Enter\nИспользуйте 'Получить инфо' для просмотра доступных качеств",
            font=("Arial", 8),
            fg="#999999",
            justify="center"
        )
        info_label.pack(side="bottom", pady=(5, 0))
    
    def detect_video_source(self, url):
        """Определяет источник видео"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'YouTube', True
        elif 'rutube.ru' in url:
            return 'Rutube', True
        elif 'vk.com' in url:
            return 'VK Video', True
        elif 'vimeo.com' in url:
            return 'Vimeo', True
        elif 'dailymotion.com' in url:
            return 'Dailymotion', True
        elif 'tiktok.com' in url:
            return 'TikTok', True
        elif 'yandex.ru/video' in url:
            return 'Яндекс.Видео', False
        else:
            return 'Неизвестный источник', None
    
    def get_video_info(self):
        """Получение информации о видео"""
        url = self.url_text.get("1.0", tk.END).strip()
        if not url:
            messagebox.showinfo("Информация", "Вставьте ссылку на видео для получения информации.")
            return
        
        source, supported = self.detect_video_source(url)
        if supported is False:
            messagebox.showwarning("Ошибка", f"{source} не поддерживается!")
            return
        
        self.update_status("Получение информации о видео...", "#2196F3")
        
        def fetch_info():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    title = info.get('title', 'Неизвестно')
                    duration = info.get('duration', 0)
                    uploader = info.get('uploader', 'Неизвестно')
                    
                    # Форматируем длительность
                    minutes = duration // 60
                    seconds = duration % 60
                    duration_str = f"{minutes}:{seconds:02d}"
                    
                    # Получаем доступные форматы
                    formats = info.get('formats', [])
                    resolutions = set()
                    for fmt in formats:
                        height = fmt.get('height')
                        if height:
                            resolutions.add(f"{height}p")
                    
                    resolutions_str = ", ".join(sorted(resolutions, reverse=True, key=lambda x: int(x[:-1]))) if resolutions else "Неизвестно"
                    
                    info_text = f"""
📹 Название: {title[:60]}...

👤 Автор: {uploader}
⏱ Длительность: {duration_str}
🎬 Доступные качества: {resolutions_str}
🌐 Источник: {source}

✓ Видео готово к загрузке!
                    """
                    
                    self.root.after(0, lambda: messagebox.showinfo("Информация о видео", info_text.strip()))
                    self.root.after(0, lambda: self.update_status("Информация получена", "#4CAF50"))
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось получить информацию:\n{error_msg[:200]}"))
                self.root.after(0, lambda: self.update_status("Ошибка получения информации", "#F44336"))
        
        thread = threading.Thread(target=fetch_info, daemon=True)
        thread.start()
    
    def check_url(self):
        """Проверка URL перед загрузкой"""
        url = self.url_text.get("1.0", tk.END).strip()
        if not url:
            messagebox.showinfo("Проверка", "Поле URL пустое.\n\nВставьте ссылку на видео.")
            return
        
        source, supported = self.detect_video_source(url)
        
        if supported is False:
            messagebox.showwarning(
                "Неподдерживаемый источник",
                f"Источник: {source}\n\n"
                "❌ Яндекс.Видео не поддерживается напрямую.\n\n"
                "Решение:\n"
                "1. Откройте видео в Яндекс.Видео\n"
                "2. Найдите оригинальный источник (YouTube, Rutube, VK)\n"
                "3. Скопируйте ссылку с оригинального источника\n\n"
                "Или используйте расширения для браузера."
            )
        elif supported is True:
            messagebox.showinfo(
                "Проверка URL",
                f"✓ Источник: {source}\n\n"
                "Эта платформа поддерживается!\n"
                "Можно начинать загрузку.\n\n"
                "Используйте 'Получить инфо' для просмотра деталей."
            )
        else:
            messagebox.showwarning(
                "Неизвестный источник",
                f"Источник: {source}\n\n"
                "Попробуем загрузить, но гарантий нет.\n"
                "Работает лучше всего с YouTube, Rutube, VK Video."
            )
    
    def extract_url(self, text):
        """Извлекает URL из текста"""
        # Паттерны для различных видео платформ
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtu\.be/[\w-]+',
            r'https?://(?:www\.)?rutube\.ru/video/[\w-]+',
            r'https?://vk\.com/video[\w-]+',
            r'https?://(?:www\.)?vimeo\.com/\d+',
            r'https?://[^\s]+',  # любой URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return text.strip()
    
    def on_paste(self, event=None):
        """Обработка вставки текста"""
        try:
            # Очищаем поле
            self.url_text.delete("1.0", tk.END)
            # Получаем текст из буфера
            clipboard_text = self.root.clipboard_get()
            # Извлекаем URL
            url = self.extract_url(clipboard_text)
            # Вставляем только URL
            self.url_text.insert("1.0", url)
            
            # Проверяем источник
            source, supported = self.detect_video_source(url)
            if supported is False:
                self.update_status(f"⚠ {source} - требуется оригинальная ссылка!", "#FF9800")
            else:
                self.update_status(f"✓ URL вставлен ({source}). Нажмите Enter или Скачать", "#2196F3")
            
            return "break"
        except:
            pass
    
    def on_focus(self, event=None):
        """При фокусе на поле - выделяем весь текст"""
        self.url_text.tag_add("sel", "1.0", "end")
    
    def on_enter(self, event=None):
        """Обработка нажатия Enter"""
        content = self.url_text.get("1.0", tk.END).strip()
        self.url_text.delete("1.0", tk.END)
        self.url_text.insert("1.0", content)
        self.start_download()
        return "break"
    
    def clear_url(self):
        """Очистка поля URL"""
        self.url_text.delete("1.0", tk.END)
        self.url_text.focus()
        self.update_status("Поле очищено. Вставьте новую ссылку", "#666666")
    
    def create_context_menu(self):
        """Создаем контекстное меню"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Вставить (Ctrl+V)", command=self.paste_from_menu)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Очистить", command=self.clear_url)
    
    def show_context_menu(self, event):
        """Показываем контекстное меню"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def paste_from_menu(self):
        """Вставка из контекстного меню"""
        self.on_paste()
    
    def copy_text(self):
        """Копирование текста"""
        try:
            selected = self.url_text.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except:
            text = self.url_text.get("1.0", tk.END).strip()
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
    
    def browse_folder(self):
        """Выбор папки для сохранения"""
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)
            self.update_status(f"Папка изменена: {os.path.basename(folder)}", "#4CAF50")
    
    def open_download_folder(self):
        """Открыть папку загрузок в проводнике"""
        path = self.download_path.get()
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showerror("Ошибка", "Папка не существует!")
    
    def update_status(self, message, color="#666666"):
        """Обновление статуса"""
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()
    
    def progress_hook(self, d):
        """Обработчик прогресса загрузки"""
        if d['status'] == 'downloading':
            try:
                # Пытаемся получить процент загрузки
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                
                if total > 0:
                    percent = (downloaded / total) * 100
                    self.root.after(0, lambda: self.progress.config(value=percent))
                    
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    self.root.after(0, lambda: self.update_status(
                        f"Загрузка: {percent:.1f}% | Скорость: {speed} | Осталось: {eta}", 
                        "#2196F3"
                    ))
                else:
                    # Если размер неизвестен, показываем индикатор
                    percent_str = d.get('_percent_str', 'N/A')
                    self.root.after(0, lambda: self.update_status(
                        f"Загрузка: {percent_str}", 
                        "#2196F3"
                    ))
            except Exception as e:
                self.root.after(0, lambda: self.update_status("Загрузка в процессе...", "#2196F3"))
                
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress.config(value=100))
            self.root.after(0, lambda: self.update_status("Обработка и сохранение файла...", "#FF9800"))
    
    def download_video(self):
        """Основная функция загрузки видео"""
        url = self.url_text.get("1.0", tk.END).strip()
        download_path = self.download_path.get()
        
        if not url:
            messagebox.showerror("Ошибка", "Введите URL видео!")
            self.reset_download_state()
            return
        
        # Проверяем источник
        source, supported = self.detect_video_source(url)
        if supported is False:
            messagebox.showerror(
                "Неподдерживаемый источник",
                f"{source} не поддерживается!\n\n"
                "Решение:\n"
                "• Откройте видео на Яндекс.Видео\n"
                "• Найдите кнопку с логотипом источника (YouTube/Rutube/VK)\n"
                "• Перейдите на оригинальный источник\n"
                "• Скопируйте ссылку оттуда\n\n"
                "Пример: если видео с YouTube, откройте его на youtube.com"
            )
            self.reset_download_state()
            return
        
        if not os.path.exists(download_path):
            messagebox.showerror("Ошибка", "Указанная папка не существует!")
            self.reset_download_state()
            return
        
        try:
            quality = self.quality_var.get()
            
            # Упрощенная и более надежная стратегия выбора формата
            if quality == "best":
                format_string = "best[ext=mp4]/best"
            else:
                format_string = f"best[height<={quality}][ext=mp4]/best[height<={quality}]/best"
            
            # Настройки yt-dlp с улучшенной обработкой
            ydl_opts = {
                'format': format_string,
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'outtmpl': {
                    'default': os.path.join(download_path, '%(title)s.%(ext)s')
                },
                'progress_hooks': [self.progress_hook],
                'postprocessor_hooks': [],
                'quiet': False,
                'no_warnings': False,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'no_color': True,
                'extract_flat': False,
                # Ограничение на имя файла
                'restrictfilenames': False,
                'windowsfilenames': True,  # Безопасные имена для Windows
            }
            
            self.root.after(0, lambda: self.update_status(f"Получение информации ({source})...", "#2196F3"))
            
            with YoutubeDL(ydl_opts) as ydl:
                # Сначала получаем информацию
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'видео')
                clean_title = self.sanitize_filename(video_title)
                
                self.root.after(0, lambda: self.update_status(f"Загрузка: {clean_title[:40]}...", "#2196F3"))
                self.root.after(0, lambda: self.progress.config(value=0))
                
                # Загружаем видео
                ydl.download([url])
            
            self.root.after(0, lambda: self.progress.config(value=100))
            self.root.after(0, lambda: self.update_status("✓ ЗАГРУЗКА ЗАВЕРШЕНА!", "#4CAF50"))
            
            # Показываем сообщение с кнопкой для открытия папки
            result = messagebox.askquestion(
                "Успех", 
                f"Видео успешно загружено!\n\n"
                f"Название: {clean_title[:50]}...\n"
                f"Папка: {download_path}\n\n"
                "Открыть папку с файлом?",
                icon='info'
            )
            
            if result == 'yes':
                os.startfile(download_path)
            
        except Exception as e:
            error_message = str(e)
            self.root.after(0, lambda: self.progress.config(value=0))
            self.root.after(0, lambda: self.update_status("✗ Ошибка загрузки", "#F44336"))
            
            # Улучшенная обработка ошибок
            if 'yandex' in url.lower() or 'YandexVideo' in error_message:
                messagebox.showerror(
                    "Ошибка: Яндекс.Видео",
                    "Яндекс.Видео не поддерживается!\n\n"
                    "Что делать:\n"
                    "1. Откройте это видео в браузере\n"
                    "2. Найдите оригинальный источник\n"
                    "3. Скопируйте ссылку с YouTube/Rutube/VK\n"
                    "4. Вставьте её сюда\n\n"
                    f"Техническая ошибка:\n{error_message[:200]}"
                )
            elif 'Private video' in error_message or 'members-only' in error_message:
                messagebox.showerror(
                    "Ошибка доступа",
                    "Это приватное видео или доступно только для подписчиков.\n\n"
                    "Видео нельзя скачать."
                )
            elif 'Video unavailable' in error_message:
                messagebox.showerror(
                    "Видео недоступно",
                    "Видео недоступно, удалено или заблокировано.\n\n"
                    "Проверьте ссылку и доступность видео в браузере."
                )
            elif 'HTTP Error 403' in error_message or 'HTTP Error 429' in error_message:
                messagebox.showerror(
                    "Ошибка доступа",
                    "Доступ запрещен или превышен лимит запросов.\n\n"
                    "Попробуйте:\n"
                    "• Подождать несколько минут\n"
                    "• Проверить интернет-соединение\n"
                    "• Обновить yt-dlp: pip install -U yt-dlp"
                )
            else:
                messagebox.showerror(
                    "Ошибка загрузки",
                    f"Не удалось загрузить видео.\n\n"
                    f"Источник: {source}\n\n"
                    "Проверьте:\n"
                    "• Правильность ссылки\n"
                    "• Доступность видео (не удалено, не заблокировано)\n"
                    "• Интернет-соединение\n"
                    "• Наличие свободного места на диске\n\n"
                    f"Ошибка: {error_message[:200]}"
                )
        
        finally:
            self.reset_download_state()
    
    def reset_download_state(self):
        """Сброс состояния после загрузки"""
        self.is_downloading = False
        self.download_btn.config(state="normal", bg="#4CAF50")
        if "завершена" not in self.status_label.cget("text").lower():
            self.update_status("Готов к загрузке", "#4CAF50")
    
    def start_download(self):
        """Запуск загрузки"""
        if self.is_downloading:
            messagebox.showwarning("Внимание", "Загрузка уже идет!")
            return
        
        url = self.url_text.get("1.0", tk.END).strip()
        if not url:
            messagebox.showwarning("Внимание", "Сначала вставьте ссылку на видео!")
            self.url_text.focus()
            return
        
        self.is_downloading = True
        self.download_btn.config(state="disabled", bg="#9E9E9E")
        self.progress.config(value=0, mode='determinate')
        self.update_status("Начинаем загрузку...", "#2196F3")
        
        thread = threading.Thread(target=self.download_video, daemon=True)
        thread.start()


def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    
    # Центрируем окно на экране
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
