/**
 * @file CodeEditor.jsx
 * @description Компонент редактора кода для симулятора робота.
 * Обеспечивает возможность редактирования программ на языке KUMIR, подсвечивает синтаксис с помощью Prism.js,
 * а также отображает статус программы и вывод консоли. Теперь над выводом лога добавлен слайдер регулировки скорости.
 */

import React, {memo, useCallback} from 'react';
import {Button, Card, Slider, Typography} from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import {Delete, PlayArrow, Refresh, Stop} from '@mui/icons-material';

import './CodeEditor.css';
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
	const alternatives = words.join("|");
	return {
		pattern: new RegExp(`(^|\\s)(?:${alternatives})(?=$|\\s)`, "i"),
		lookbehind: true
	};
}

Prism.languages.kumir = {
	"keyword-struct": makeKumirRegex(structuralKeywords),
	"keyword-type": makeKumirRegex(typeKeywords),
	"keyword-bool": makeKumirRegex(booleanKeywords),
	"keyword-io": makeKumirRegex(ioKeywords),
	"keyword-flow": makeKumirRegex(flowKeywords),
	"robot-command": makeKumirRegex(robotCommands),
	comment: /#.*/,
	string: {
		pattern: /(["'])(?:(?!\1).)*\1/,
		greedy: true
	},
	number: {
		pattern: /-?\$[0-9A-Fa-f]+|-?\d+(?:\.\d+)?(?:[еeЕE][-+]?\d+)?/
	},
	operator: /(?:\*\*|<=|>=|<>|!=|==|[+\-*/<>=])/
};

/**
 * Компонент редактора кода.
 *
 * Новые пропсы:
 *   - speedLevel (number): текущее значение слайдера скорости (0–4)
 *   - onSpeedChange (function): callback для изменения значения слайдера скорости
 *
 * @param {Object} props
 * @returns {JSX.Element}
 */
const CodeEditor = memo(({
	                         code,
	                         setCode,
	                         isRunning,
	                         onClearCode,
	                         onStop,
	                         onStart,
	                         onReset,
	                         statusText,
	                         consoleOutput,
	                         speedLevel,
	                         onSpeedChange
                         }) => {
	const highlightCode = useCallback((inputCode) => {
		return Prism.highlight(inputCode, Prism.languages.kumir, 'kumir');
	}, []);

	return (
		<div className="code-editor">
			<Typography variant="h5" gutterBottom>
				Редактор Кода
			</Typography>
			<Editor
				value={code}
				onValueChange={setCode}
				highlight={highlightCode}
				padding={10}
				className="react-simple-code-editor"
			/>
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
			{/* Новый блок слайдера */}
			<div className="speed-slider-container" style={{marginTop: '16px', marginBottom: '16px'}}>
				<Typography variant="subtitle1" gutterBottom>
					Скорость исполнения:
				</Typography>
				<Slider
					value={speedLevel}
					onChange={(e, newValue) => onSpeedChange(newValue)}
					step={1}
					marks={[
						{value: 0, label: '2 сек/шаг'},
						{value: 1, label: '1.5 сек/шаг'},
						{value: 2, label: '1 сек/шаг'},
						{value: 3, label: '0.5 сек/шаг'},
						{value: 4, label: 'Мгновенно'},
					]}
					min={0}
					max={4}
					valueLabelDisplay="auto"
				/>
			</div>
			<Card className="status-card">
				<Typography variant="body2" className="status-text">
					{statusText}
				</Typography>
			</Card>
			<Card className="console-card">
				<UserLog/>
			</Card>
		</div>
	);
});

export default CodeEditor;
