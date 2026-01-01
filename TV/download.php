<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// Путь к yt-dlp (измените на свой)
$YT_DLP_PATH = '/usr/local/bin/yt-dlp'; // или 'yt-dlp' если в PATH

// Папка для загрузок
$DOWNLOAD_DIR = __DIR__ . '/downloads/';

// Создаем папку если не существует
if (!file_exists($DOWNLOAD_DIR)) {
    mkdir($DOWNLOAD_DIR, 0755, true);
}

// Получаем данные из POST запроса
$data = json_decode(file_get_contents('php://input'), true);

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

// Формируем формат для загрузки
if ($quality === 'best') {
    $format = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best';
} else {
    $format = "bestvideo[height<={$quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={$quality}][ext=mp4]/best";
}

// Генерируем уникальное имя файла
$filename = uniqid('video_') . '.mp4';
$output_path = $DOWNLOAD_DIR . $filename;
$output_template = $DOWNLOAD_DIR . '%(title)s_' . uniqid() . '.%(ext)s';

// Команда для yt-dlp
$command = escapeshellcmd($YT_DLP_PATH) . ' ' .
           '--format ' . escapeshellarg($format) . ' ' .
           '--output ' . escapeshellarg($output_template) . ' ' .
           '--merge-output-format mp4 ' .
           '--no-playlist ' .
           '--no-warnings ' .
           '--quiet ' .
           escapeshellarg($url) . ' 2>&1';

// Выполняем команду
exec($command, $output, $return_code);

// Проверяем результат
if ($return_code === 0) {
    // Ищем загруженный файл
    $files = glob($DOWNLOAD_DIR . '*');
    if (count($files) > 0) {
        // Берем последний загруженный файл
        $downloaded_file = array_pop($files);
        $public_filename = basename($downloaded_file);
        
        echo json_encode([
            'success' => true,
            'message' => 'Видео успешно загружено',
            'download_url' => 'downloads/' . $public_filename,
            'filename' => $public_filename
        ]);
    } else {
        echo json_encode([
            'success' => false,
            'error' => 'Файл не найден после загрузки'
        ]);
    }
} else {
    $error_message = implode("\n", $output);
    
    // Специальное сообщение для частых ошибок
    if (strpos($error_message, 'YandexVideo') !== false) {
        $error_message = 'Яндекс.Видео не поддерживается. Используйте прямую ссылку с оригинального источника.';
    } elseif (strpos($error_message, 'Video unavailable') !== false) {
        $error_message = 'Видео недоступно или удалено';
    } elseif (strpos($error_message, 'Private video') !== false) {
        $error_message = 'Это приватное видео, скачать нельзя';
    }
    
    echo json_encode([
        'success' => false,
        'error' => 'Ошибка загрузки: ' . $error_message,
        'command_output' => $output
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