<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// Получаем данные из POST запроса
$data = json_decode(file_get_contents('php://input'), true);

if (!isset($data['path']) || empty($data['path'])) {
    echo json_encode([
        'success' => false,
        'error' => 'Путь не указан'
    ]);
    exit;
}

$path = $data['path'];

// Проверяем, что путь существует
if (!file_exists($path)) {
    echo json_encode([
        'success' => false,
        'error' => 'Путь не существует: ' . $path
    ]);
    exit;
}

// Определяем ОС и открываем папку
if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
    // Windows - используем explorer
    $command = 'explorer ' . escapeshellarg($path);
} elseif (PHP_OS === 'Darwin') {
    // macOS - используем open
    $command = 'open ' . escapeshellarg($path);
} else {
    // Linux - используем xdg-open
    $command = 'xdg-open ' . escapeshellarg($path);
}

// Выполняем команду
exec($command . ' 2>&1', $output, $return_code);

if ($return_code === 0) {
    echo json_encode([
        'success' => true,
        'message' => 'Папка открыта'
    ]);
} else {
    echo json_encode([
        'success' => false,
        'error' => 'Не удалось открыть папку',
        'debug_output' => implode("\n", $output)
    ]);
}
?>
