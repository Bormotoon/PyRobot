/**
 * @file CodeEditor.jsx
 * @description Компонент редактора кода для симулятора робота.
 * Этот компонент предоставляет возможность редактирования программ на языке "kumir",
 * осуществляет подсветку синтаксиса с помощью Prism.js и включает панель управления с кнопками для очистки,
 * запуска, остановки и сброса кода. Также отображаются статус программы и вывод консоли с ответами сервера.
 */

import React, {memo, useCallback} from 'react';
import {Button, Card, Typography} from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import {Delete, PlayArrow, Refresh, Stop} from '@mui/icons-material';

import './CodeEditor.css';

// --- Списки ключевых слов (отображаемые пользователю, должны оставаться на русском языке) ---

// Список ключевых слов для структурных элементов языка
const structuralKeywords = ["алг", "нач", "кон", "исп", "кон_исп", "использовать"];
// Список ключевых слов для типов данных и объявления переменных
const typeKeywords = ["дано", "надо", "арг", "рез", "аргрез", "знач", "цел", "вещ", "лог", "сим", "лит", "таб", "целтаб", "вещтаб", "логтаб", "симтаб", "литтаб"];
// Список ключевых слов для булевых операций
const booleanKeywords = ["и", "или", "не", "да", "нет"];
// Список ключевых слов для ввода-вывода
const ioKeywords = ["утв", "ввод", "вывод", "выход"];
// Список ключевых слов для управления потоком выполнения программы
const flowKeywords = ["нс", "если", "то", "иначе", "все", "выбор", "при", "нц", "кц", "кц_при", "раз", "пока", "для", "от", "до", "шаг"];
// Список команд для управления роботом
const robotCommands = ["Робот", "влево", "вправо", "вверх", "вниз", "закрасить", "слева свободно", "справа свободно", "сверху свободно", "снизу свободно", "слева стена", "справа стена", "сверху стена", "снизу стена", "клетка закрашена", "клетка чистая", "температура", "радиация"];

/**
 * Функция для генерации регулярного выражения для подсветки ключевых слов.
 *
 * @param {string[]} words - Массив ключевых слов.
 * @returns {Object} Объект, содержащий сгенерированное регулярное выражение (pattern) и флаг lookbehind.
 */
function makeKumirRegex(words) {
	const alternatives = words.join("|"); // Объединение ключевых слов в строку через символ "|"
	return {
		pattern: new RegExp(`(^|\\s)(?:${alternatives})(?=$|\\s)`, "i"), // Регулярное выражение для поиска ключевых слов
		lookbehind: true
	};
}

// Определение языка "kumir" для подсветки синтаксиса в Prism.js
Prism.languages.kumir = {
	"keyword-struct": makeKumirRegex(structuralKeywords),  // Подсветка структурных ключевых слов
	"keyword-type": makeKumirRegex(typeKeywords),            // Подсветка ключевых слов типов
	"keyword-bool": makeKumirRegex(booleanKeywords),         // Подсветка булевых ключевых слов
	"keyword-io": makeKumirRegex(ioKeywords),                // Подсветка ключевых слов ввода-вывода
	"keyword-flow": makeKumirRegex(flowKeywords),            // Подсветка ключевых слов управления потоком
	"robot-command": makeKumirRegex(robotCommands),          // Подсветка команд робота
	// Подсветка комментариев (начинаются с символа #)
	comment: /#.*/, // Подсветка строк, заключенных в одинарные или двойные кавычки
	string: {
		pattern: /(["'])(?:(?!\1).)*\1/, greedy: true
	}, // Подсветка числовых литералов, включая шестнадцатеричные и экспоненциальную запись
	number: {
		pattern: /-?\$[0-9A-Fa-f]+|-?\d+(?:\.\d+)?(?:[еeЕE][-+]?\d+)?/
	}, // Подсветка операторов
	operator: /(?:\*\*|<=|>=|<>|!=|==|[+\-*/<>=])/
};

/**
 * Компонент редактора кода.
 * Отображает редактор кода, панель управления с кнопками для очистки, запуска, остановки и сброса кода,
 * а также выводит текущий статус и консоль с ответами сервера.
 *
 * @param {Object} props - Свойства компонента.
 * @param {string} props.code - Текущий текст программы.
 * @param {function} props.setCode - Функция для обновления кода.
 * @param {boolean} props.isRunning - Флаг, указывающий на то, что программа выполняется.
 * @param {function} props.onClearCode - Функция для очистки кода.
 * @param {function} props.onStop - Функция для остановки выполнения программы.
 * @param {function} props.onStart - Функция для запуска выполнения программы.
 * @param {function} props.onReset - Функция для сброса состояния редактора.
 * @param {string} props.statusText - Текст статуса, например, позиция робота или количество маркеров.
 * @param {string} props.consoleOutput - Вывод консоли с ответами от сервера.
 * @returns {JSX.Element} Разметка редактора кода.
 */
const CodeEditor = memo(({
	                         code, setCode, isRunning, onClearCode, onStop, onStart, onReset, statusText,    // Текущий статус (например, позиция робота, маркеры и т.д.)
	                         consoleOutput  // Вывод консоли (ответы сервера)
                         }) => {
	/**
	 * Функция для подсветки синтаксиса в редакторе.
	 * Использует Prism для выделения синтаксиса на основе языка "kumir".
	 *
	 * @param {string} inputCode - Код, который необходимо подсветить.
	 * @returns {string} Подсвеченный HTML-код.
	 */
	const highlightCode = useCallback((inputCode) => {
		return Prism.highlight(inputCode, Prism.languages.kumir, 'kumir');
	}, []);

	return (<div className="code-editor">
			{/* Заголовок редактора кода */}
			<Typography variant="h5" gutterBottom>
				Редактор Кода
			</Typography>

			{/* Основной редактор кода с подсветкой синтаксиса */}
			<Editor
				value={code}                   // Значение кода из состояния
				onValueChange={setCode}         // Функция обновления кода при изменении
				highlight={highlightCode}       // Функция подсветки синтаксиса
				padding={10}                    // Отступы внутри редактора
				className="react-simple-code-editor"  // CSS-класс для стилизации редактора
			/>

			{/* Панель управления: кнопки для различных действий */}
			<div className="editor-controls">
				{/* Кнопка для очистки кода */}
				<Button
					variant="contained"
					color="info"
					className="editor-button"
					onClick={onClearCode}
				>
					<Delete/>
				</Button>

				{/* Кнопка для остановки выполнения программы */}
				<Button
					variant="contained"
					color="error"
					className="editor-button"
					onClick={onStop}
					disabled={!isRunning} // Отключена, если программа не выполняется
				>
					<Stop/>
				</Button>

				{/* Кнопка для запуска выполнения программы */}
				<Button
					variant="contained"
					color="success"
					className="editor-button"
					onClick={onStart}
					disabled={isRunning}  // Отключена, если программа уже выполняется
				>
					<PlayArrow/>
				</Button>

				{/* Кнопка для сброса состояния редактора и симулятора */}
				<Button
					variant="outlined"
					color="warning"
					className="editor-button"
					onClick={onReset}
				>
					<Refresh/>
				</Button>
			</div>

			{/* Карточка для отображения текущего статуса симулятора */}
			<Card className="status-card">
				<Typography variant="body2" className="status-text">
					{statusText}
				</Typography>
			</Card>

			{/* Карточка для отображения консольного вывода (ответов от сервера) */}
			<Card className="console-card">
				<Typography variant="body2" className="console-text">
					{consoleOutput}
				</Typography>
			</Card>
		</div>);
});

export default CodeEditor;
