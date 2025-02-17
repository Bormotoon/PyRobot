/**
 * @file CodeEditor.jsx
 * @description Компонент редактора кода для симулятора робота.
 * Обеспечивает возможность редактирования программ на языке KUMIR, подсвечивает синтаксис с помощью Prism.js,
 * а также отображает статус программы и вывод консоли. Теперь вывод консоли заменён на компонент UserLog,
 * который рендерится внутри карточки с классом "console-card".
 */

import React, {memo, useCallback} from 'react';
import {Button, Card, Typography} from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import {Delete, PlayArrow, Refresh, Stop} from '@mui/icons-material';

import './CodeEditor.css';
// Импорт компонента логирования, который теперь рендерится внутри карточки консоли
import UserLog from '../UserLog/UserLog';

/**
 * Списки ключевых слов для подсветки синтаксиса языка KUMIR.
 */
const structuralKeywords = ["алг", "нач", "кон", "исп", "кон_исп", "использовать"];
const typeKeywords = ["дано", "надо", "арг", "рез", "аргрез", "знач", "цел", "вещ", "лог", "сим", "лит", "таб", "целтаб", "вещтаб", "логтаб", "симтаб", "литтаб"];
const booleanKeywords = ["и", "или", "не", "да", "нет"];
const ioKeywords = ["утв", "ввод", "вывод", "выход"];
const flowKeywords = ["нс", "если", "то", "иначе", "все", "выбор", "при", "нц", "кц", "кц_при", "раз", "пока", "для", "от", "до", "шаг"];
const robotCommands = ["Робот", "влево", "вправо", "вверх", "вниз", "закрасить", "слева свободно", "справа свободно", "сверху свободно", "снизу свободно", "слева стена", "справа стена", "сверху стена", "снизу стена", "клетка закрашена", "клетка чистая", "температура", "радиация"];

/**
 * Функция для генерации регулярного выражения для подсветки ключевых слов.
 * @param {string[]} words - Массив ключевых слов.
 * @returns {Object} Объект с полем pattern (регулярное выражение) и флагом lookbehind.
 */
function makeKumirRegex(words) {
	const alternatives = words.join("|"); // Объединяем ключевые слова через "|"
	return {
		pattern: new RegExp(`(^|\\s)(?:${alternatives})(?=$|\\s)`, "i"), lookbehind: true
	};
}

// Определяем язык "kumir" для Prism.js с использованием сгенерированных регулярных выражений.
Prism.languages.kumir = {
	"keyword-struct": makeKumirRegex(structuralKeywords),
	"keyword-type": makeKumirRegex(typeKeywords),
	"keyword-bool": makeKumirRegex(booleanKeywords),
	"keyword-io": makeKumirRegex(ioKeywords),
	"keyword-flow": makeKumirRegex(flowKeywords),
	"robot-command": makeKumirRegex(robotCommands),
	comment: /#.*/, // Комментарии начинаются с символа "#"
	string: {
		pattern: /(["'])(?:(?!\1).)*\1/, greedy: true
	},
	number: {
		pattern: /-?\$[0-9A-Fa-f]+|-?\d+(?:\.\d+)?(?:[еeЕE][-+]?\d+)?/
	},
	operator: /(?:\*\*|<=|>=|<>|!=|==|[+\-*/<>=])/
};

/**
 * Компонент редактора кода.
 *
 * @param {Object} props - Свойства компонента:
 *   - code (string): Исходный код программы.
 *   - setCode (function): Функция для обновления кода.
 *   - isRunning (boolean): Флаг выполнения программы.
 *   - onClearCode (function): Функция для очистки кода.
 *   - onStop (function): Функция для остановки выполнения.
 *   - onStart (function): Функция для запуска выполнения.
 *   - onReset (function): Функция для сброса состояния.
 *   - statusText (string): Текст текущего статуса симулятора.
 *   - consoleOutput (string): Вывод консоли (теперь не используется напрямую).
 * @returns {JSX.Element} Разметка редактора кода.
 */
const CodeEditor = memo(({
	                         code, setCode, isRunning, onClearCode, onStop, onStart, onReset, statusText, consoleOutput
                         }) => {
	/**
	 * Функция подсветки синтаксиса с использованием Prism.js.
	 * @param {string} inputCode - Исходный код.
	 * @returns {string} HTML с подсвеченным синтаксисом.
	 */
	const highlightCode = useCallback((inputCode) => {
		return Prism.highlight(inputCode, Prism.languages.kumir, 'kumir');
	}, []);

	return (<div className="code-editor">
			{/* Заголовок редактора */}
			<Typography variant="h5" gutterBottom>
				Редактор Кода
			</Typography>

			{/* Редактор с подсветкой синтаксиса */}
			<Editor
				value={code}
				onValueChange={setCode}
				highlight={highlightCode}
				padding={10}
				className="react-simple-code-editor"
			/>

			{/* Панель управления редактором */}
			<div className="editor-controls">
				<Button variant="contained" color="info" className="editor-button" onClick={onClearCode}>
					<Delete/>
				</Button>
				<Button variant="contained" color="error" className="editor-button" onClick={onStop}
				        disabled={!isRunning}>
					<Stop/>
				</Button>
				<Button variant="contained" color="success" className="editor-button" onClick={onStart}
				        disabled={isRunning}>
					<PlayArrow/>
				</Button>
				<Button variant="outlined" color="warning" className="editor-button" onClick={onReset}>
					<Refresh/>
				</Button>
			</div>

			{/* Карточка статуса симулятора */}
			<Card className="status-card">
				<Typography variant="body2" className="status-text">
					{statusText}
				</Typography>
			</Card>

			{/* Карточка консоли с выводом лога через компонент UserLog */}
			<Card className="console-card">
				<UserLog/>
			</Card>
		</div>);
});

export default CodeEditor;
