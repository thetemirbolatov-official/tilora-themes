const vscode = require('vscode');

// Глобальные переменные
let statusBarItem;
let isAnimationsEnabled = true;

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Активация TILORA Cosmic Theme...');

    // Инициализация конфигурации
    const config = vscode.workspace.getConfiguration('tiloraThemes');
    isAnimationsEnabled = config.get('enableAnimations', true);

    // Создание статус-бара
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(stars) TILORA";
    statusBarItem.tooltip = "TILORA Cosmic Theme\nРазработчик: thetemirbolatov";
    statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    
    // Команда для показа информации
    let showInfoCommand = vscode.commands.registerCommand('tilora-themes.showInfo', () => {
        showInformationMessage();
    });

    // Команда для переключения анимаций
    let toggleAnimationsCommand = vscode.commands.registerCommand('tilora-themes.toggleAnimations', () => {
        toggleAnimations();
    });

    // Команда для применения пресетов
    let applyPresetCommand = vscode.commands.registerCommand('tilora-themes.applyPreset', async () => {
        applyThemePreset();
    });

    // Показать приветственное сообщение
    setTimeout(() => {
        if (config.get('showWelcome', true)) {
            showWelcomeMessage();
        }
    }, 2000);

    // Подписка на изменения конфигурации
    vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('tiloraThemes')) {
            updateStatusBar();
        }
    });

    // Добавление команд в контекст
    context.subscriptions.push(
        showInfoCommand,
        toggleAnimationsCommand,
        applyPresetCommand,
        statusBarItem
    );

    // Показать статус-бар
    statusBarItem.show();
    
    // Инициализация кастомных CSS (если поддерживается)
    injectCustomCSS();
    
    console.log('TILORA Cosmic Theme активирована!');
}

/**
 * Показать информационное сообщение
 */
function showInformationMessage() {
    const message = `🎨 **TILORA Cosmic Theme** 
    
**Разработчик:** thetemirbolatov
**Версия:** 1.0.0
**Год выпуска:** 2026

✨ Особенности:
• Космический дизайн с градиентами
• Плавные анимации
• Свечение элементов
• Оптимизировано для слабых ПК
• 2 версии: Dark & Light

[Открыть настройки темы](command:workbench.action.openSettings?{"query":"tiloraThemes"})`;

    vscode.window.showInformationMessage(message, { modal: true });
}

/**
 * Показать приветственное сообщение
 */
function showWelcomeMessage() {
    const message = `🚀 **Добро пожаловать в TILORA Cosmic Theme!**
    
Спасибо за установку премиум-темы от **thetemirbolatov**!
Тема автоматически активирована. Настройки можно найти в разделе "TILORA Themes".

**Быстрые команды:**
• F1 → "TILORA: Показать информацию"
• F1 → "TILORA: Включить/выключить анимации"

Разработано с ❤️ для идеального опыта кодирования!`;

    vscode.window.showInformationMessage(message, 
        { modal: false },
        "Открыть настройки",
        "Понятно"
    ).then(selection => {
        if (selection === "Открыть настройки") {
            vscode.commands.executeCommand('workbench.action.openSettings', 'tiloraThemes');
        }
    });
}

/**
 * Переключить анимации
 */
function toggleAnimations() {
    const config = vscode.workspace.getConfiguration('tiloraThemes');
    const currentValue = config.get('enableAnimations', true);
    
    config.update('enableAnimations', !currentValue, vscode.ConfigurationTarget.Global)
        .then(() => {
            vscode.window.showInformationMessage(
                `Анимации ${!currentValue ? 'включены' : 'выключены'}!`,
                { timeout: 1500 }
            );
            updateStatusBar();
        });
}

/**
 * Применить пресет темы
 */
async function applyThemePreset() {
    const presets = [
        'Cosmic Purple',
        'Nebula Blue', 
        'Galaxy Pink',
        'Star Gold',
        'Black Hole'
    ];
    
    const selected = await vscode.window.showQuickPick(presets, {
        placeHolder: 'Выберите цветовой пресет',
        title: 'TILORA Theme Presets'
    });
    
    if (selected) {
        let accentColor;
        switch(selected) {
            case 'Cosmic Purple':
                accentColor = '#7B61FF';
                break;
            case 'Nebula Blue':
                accentColor = '#00D4FF';
                break;
            case 'Galaxy Pink':
                accentColor = '#FF00C7';
                break;
            case 'Star Gold':
                accentColor = '#FFB800';
                break;
            case 'Black Hole':
                accentColor = '#00FF94';
                break;
        }
        
        const config = vscode.workspace.getConfiguration('tiloraThemes');
        await config.update('customAccentColor', accentColor, vscode.ConfigurationTarget.Global);
        
        vscode.window.showInformationMessage(
            `Пресет "${selected}" применен!`,
            { timeout: 1500 }
        );
    }
}

/**
 * Обновить статус-бар
 */
function updateStatusBar() {
    const config = vscode.workspace.getConfiguration('tiloraThemes');
    const animationsEnabled = config.get('enableAnimations', true);
    
    statusBarItem.text = animationsEnabled ? 
        "$(play-circle) TILORA" : 
        "$(stop-circle) TILORA";
    
    statusBarItem.tooltip = `TILORA Cosmic Theme\n` +
        `Анимации: ${animationsEnabled ? 'ВКЛ' : 'ВЫКЛ'}\n` +
        `Разработчик: thetemirbolatov`;
}

/**
 * Внедрение кастомных CSS стилей
 */
function injectCustomCSS() {
    // Этот метод использует недокументированные возможности
    // В реальном расширении нужно быть осторожным
    console.log('CSS injection prepared');
}

/**
 * Деактивация расширения
 */
function deactivate() {
    console.log('Деактивация TILORA Cosmic Theme...');
    if (statusBarItem) {
        statusBarItem.dispose();
    }
}

module.exports = {
    activate,
    deactivate
};