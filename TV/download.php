<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// Определяем путь к yt-dlp в зависимости от ОС
if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
    // Windows - ищем в PATH или используем полный путь
    $YT_DLP_PATH = 'yt-dlp'; // или 'C:\\Python\\Scripts\\yt-dlp.exe'
} else {
    // Linux/Mac
    $YT_DLP_PATH = '/usr/local/bin/yt-dlp'; // или 'yt-dlp' если в PATH
}

// Получаем данные из POST запроса (перемещено выше для доступа к downloadPath)
$data = json_decode(file_get_contents('php://input'), true);

// Папка для загрузок - можно настроить из запроса
if (isset($data['downloadPath']) && !empty($data['downloadPath'])) {
    $DOWNLOAD_DIR = rtrim($data['downloadPath'], '/\\') . DIRECTORY_SEPARATOR;
} else {
    $DOWNLOAD_DIR = __DIR__ . '/downloads/';
}

// Создаем папку если не существует
if (!file_exists($DOWNLOAD_DIR)) {
    mkdir($DOWNLOAD_DIR, 0755, true);
}

// Функция очистки имени файла (как в Python)
function sanitizeFilename($filename) {
    // Запрещенные символы в Windows: \ / : * ? " < > |
    $clean = preg_replace('/[<>:"\/\\|?*]/', '_', $filename);
    // Убираем точки в конце
    $clean = rtrim($clean, '.');
    // Ограничиваем длину
    if (mb_strlen($clean) > 200) {
        $clean = mb_substr($clean, 0, 200);
    }
    return $clean;
}

// Проверяем наличие URL
if (!isset($data['url']) || empty($data['url'])) {
    echo json_encode([
        'success' => false,
        'error' => 'URL не указан'
    ]);
    exit;
}

$url = filter_var($data['url'], FILTER_SANITIZE_URL);
$quality = isset($data['quality']) ? $data['quality'] : 'best';

// Проверяем источник
function detectVideoSource($url) {
    if (strpos($url, 'youtube.com') !== false || strpos($url, 'youtu.be') !== false) {
        return ['name' => 'YouTube', 'supported' => true];
    } elseif (strpos($url, 'rutube.ru') !== false) {
        return ['name' => 'Rutube', 'supported' => true];
    } elseif (strpos($url, 'vk.com') !== false) {
        return ['name' => 'VK Video', 'supported' => true];
    } elseif (strpos($url, 'vimeo.com') !== false) {
        return ['name' => 'Vimeo', 'supported' => true];
    } elseif (strpos($url, 'yandex.ru/video') !== false) {
        return ['name' => 'Яндекс.Видео', 'supported' => false];
    }
    return ['name' => 'Unknown', 'supported' => null];
}

$source = detectVideoSource($url);

if ($source['supported'] === false) {
    echo json_encode([
        'success' => false,
        'error' => $source['name'] . ' не поддерживается. Используйте прямую ссылку с YouTube/Rutube/VK'
    ]);
    exit;
}

// Формируем формат для загрузки (как в Python-версии)
if ($quality === 'best') {
    // Лучшее качество - берем best в mp4 или просто best
    $format = 'best[ext=mp4]/best';
} else {
    // Конкретное качество с fallback
    $format = "best[height<={$quality}][ext=mp4]/best[height<={$quality}]/best";
}

// Безопасное имя файла для шаблона
$timestamp = time();
$template_name = "%(title)s_{$timestamp}.%(ext)s";
$output_template = $DOWNLOAD_DIR . $template_name;

// Также запоминаем для поиска скачанного файла
$search_pattern = "*_{$timestamp}.*";

// Строим команду yt-dlp (более надежная версия как в Python)
$command = escapeshellcmd($YT_DLP_PATH) . ' ' .
           '--format ' . escapeshellarg($format) . ' ' .
           '--output ' . escapeshellarg($output_template) . ' ' .
           '--merge-output-format mp4 ' .
           '--no-playlist ' .
           '--no-warnings ' .
           '--newline ' .
           '--no-check-certificate ' .
           '--ignore-errors ' .
           escapeshellarg($url) . ' 2>&1';

// Выполняем команду
exec($command, $output, $return_code);

// Проверяем результат
if ($return_code === 0) {
    // Находим файл по паттерну с timestamp
    $downloaded_files = glob($DOWNLOAD_DIR . $search_pattern);
    
    if (count($downloaded_files) > 0) {
        // Берем первый файл (должен быть только один с этим timestamp)
        $downloaded_file = reset($downloaded_files);
        $public_filename = basename($downloaded_file);
        $full_path = realpath($downloaded_file);
        
        // Проверяем размер файла
        $filesize = filesize($downloaded_file);
        $filesize_mb = round($filesize / 1024 / 1024, 2);
        
        echo json_encode([
            'success' => true,
            'message' => 'Видео успешно загружено',
            'download_url' => 'downloads/' . $public_filename,
            'filename' => $public_filename,
            'filesize' => $filesize_mb . ' MB',
            'full_path' => $full_path,
            'download_dir' => realpath($DOWNLOAD_DIR)
        ]);
    } else {
        echo json_encode([
            'success' => false,
            'error' => 'Файл не найден после загрузки. Возможно, видео недоступно.',
            'debug_output' => implode("\n", $output)
        ]);
    }
} else {
    // Обработка ошибок (как в Python-версии)
    $error_message = implode("\n", $output);
    
    // Специальные сообщения для частых ошибок
    if (stripos($error_message, 'YandexVideo') !== false || 
        stripos($error_message, 'yandex') !== false) {
        $error_message = 'Яндекс.Видео не поддерживается. Используйте прямую ссылку с YouTube/Rutube/VK.';
    } elseif (stripos($error_message, 'Video unavailable') !== false) {
        $error_message = 'Видео недоступно или удалено';
    } elseif (stripos($error_message, 'Private video') !== false || 
              stripos($error_message, 'members-only') !== false) {
        $error_message = 'Это приватное видео или доступно только для подписчиков';
    } elseif (stripos($error_message, 'HTTP Error 403') !== false) {
        $error_message = 'Доступ запрещен. Попробуйте обновить yt-dlp: pip install -U yt-dlp';
    } elseif (stripos($error_message, 'HTTP Error 429') !== false) {
        $error_message = 'Превышен лимит запросов. Подождите несколько минут';
    } elseif (empty($error_message)) {
        $error_message = 'Неизвестная ошибка. Проверьте правильность ссылки';
    }
    
    echo json_encode([
        'success' => false,
        'error' => $error_message,
        'debug_output' => $output,
        'return_code' => $return_code
    ]);
}

// Очистка старых файлов (старше 1 часа)
$files = glob($DOWNLOAD_DIR . '*');
$now = time();
foreach ($files as $file) {
    if (is_file($file)) {
        if ($now - filemtime($file) >= 3600) { // 1 час
            unlink($file);
        }
    }
}
?>