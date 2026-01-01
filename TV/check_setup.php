#!/usr/bin/env php
<?php
/**
 * Скрипт проверки конфигурации YouTube Downloader
 */

echo "╔═══════════════════════════════════════════════════════════╗\n";
echo "║     🔍 Проверка конфигурации YouTube Downloader          ║\n";
echo "╚═══════════════════════════════════════════════════════════╝\n\n";

// Цвета для терминала
function success($text) {
    return "✅ " . $text;
}

function error($text) {
    return "❌ " . $text;
}

function warning($text) {
    return "⚠️  " . $text;
}

function info($text) {
    return "ℹ️  " . $text;
}

// 1. Проверка PHP
echo "1. Проверка PHP...\n";
if (version_compare(PHP_VERSION, '7.0.0', '>=')) {
    echo success("PHP версия: " . PHP_VERSION) . "\n";
} else {
    echo error("PHP версия слишком старая: " . PHP_VERSION . " (требуется >= 7.0)") . "\n";
}

// 2. Проверка yt-dlp
echo "\n2. Проверка yt-dlp...\n";

$yt_dlp_paths = ['yt-dlp', '/usr/local/bin/yt-dlp', 'C:\\Python\\Scripts\\yt-dlp.exe'];
$yt_dlp_found = false;
$yt_dlp_path = null;

foreach ($yt_dlp_paths as $path) {
    $check = shell_exec("$path --version 2>&1");
    if ($check && !stripos($check, 'not found') && !stripos($check, 'not recognized')) {
        $yt_dlp_found = true;
        $yt_dlp_path = $path;
        echo success("yt-dlp найден: $path") . "\n";
        echo info("Версия: " . trim($check)) . "\n";
        break;
    }
}

if (!$yt_dlp_found) {
    echo error("yt-dlp не найден!") . "\n";
    echo info("Установите: pip install yt-dlp") . "\n";
} else {
    // Проверим обновления
    echo info("Проверка обновлений...") . "\n";
    $update_check = shell_exec("$yt_dlp_path -U 2>&1");
    if (stripos($update_check, 'Updated') !== false) {
        echo warning("Доступна новая версия. Обновите: pip install -U yt-dlp") . "\n";
    }
}

// 3. Проверка папки downloads
echo "\n3. Проверка папки downloads...\n";
$download_dir = __DIR__ . '/downloads/';

if (file_exists($download_dir)) {
    echo success("Папка downloads существует") . "\n";
    if (is_writable($download_dir)) {
        echo success("Папка доступна для записи") . "\n";
    } else {
        echo error("Папка НЕ доступна для записи!") . "\n";
        echo info("Выполните: chmod 755 downloads/") . "\n";
    }
} else {
    echo warning("Папка downloads не существует, создаём...") . "\n";
    if (mkdir($download_dir, 0755, true)) {
        echo success("Папка downloads создана") . "\n";
    } else {
        echo error("Не удалось создать папку downloads") . "\n";
    }
}

// 4. Проверка файлов
echo "\n4. Проверка необходимых файлов...\n";
$required_files = ['index.html', 'download.php'];
foreach ($required_files as $file) {
    if (file_exists(__DIR__ . '/' . $file)) {
        echo success("$file найден") . "\n";
    } else {
        echo error("$file НЕ найден!") . "\n";
    }
}

// 5. Проверка download.php конфигурации
echo "\n5. Проверка конфигурации download.php...\n";
$download_php = file_get_contents(__DIR__ . '/download.php');

// Ищем путь к yt-dlp в файле
if (preg_match('/\$YT_DLP_PATH\s*=\s*[\'"](.+?)[\'"]/', $download_php, $matches)) {
    $configured_path = $matches[1];
    echo info("Настроенный путь: $configured_path") . "\n";
    
    // Проверяем, работает ли этот путь
    $check = shell_exec("$configured_path --version 2>&1");
    if ($check && !stripos($check, 'not found') && !stripos($check, 'not recognized')) {
        echo success("Путь в download.php правильный") . "\n";
    } else {
        echo error("Путь в download.php НЕ работает!") . "\n";
        if ($yt_dlp_path) {
            echo info("Измените на: \$YT_DLP_PATH = '$yt_dlp_path';") . "\n";
        }
    }
}

// 6. Тест загрузки (опционально)
echo "\n6. Тестовая загрузка (пропущено)...\n";
echo info("Для теста откройте index.html и попробуйте скачать видео") . "\n";

// 7. Информация для запуска
echo "\n╔═══════════════════════════════════════════════════════════╗\n";
echo "║                    🚀 КАК ЗАПУСТИТЬ                      ║\n";
echo "╚═══════════════════════════════════════════════════════════╝\n\n";

if ($yt_dlp_found) {
    echo success("Всё готово к работе!") . "\n\n";
    echo "Запуск веб-сервера:\n";
    echo "   php -S localhost:8000\n\n";
    echo "Откройте в браузере:\n";
    echo "   http://localhost:8000/index.html\n\n";
} else {
    echo error("Требуется установка yt-dlp!") . "\n\n";
    echo "Установка:\n";
    echo "   pip install yt-dlp\n\n";
    echo "После установки запустите этот скрипт снова:\n";
    echo "   php check_setup.php\n\n";
}

echo "╔═══════════════════════════════════════════════════════════╗\n";
echo "║              📚 Документация: README_SETUP.md            ║\n";
echo "╚═══════════════════════════════════════════════════════════╝\n";

?>
