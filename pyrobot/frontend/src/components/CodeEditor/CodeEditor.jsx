// CodeEditor.jsx

import React, {memo, useCallback} from 'react';
import {Button, Typography, Card} from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import {Delete, Stop, PlayArrow, Refresh} from '@mui/icons-material';

import './CodeEditor.css';

// --- Списки ключевых слов ---
const structuralKeywords = [
	"алг", "нач", "кон", "исп", "кон_исп", "использовать"
];
const typeKeywords = [
	"дано", "надо", "арг", "рез", "аргрез", "знач",
	"цел", "вещ", "лог", "сим", "лит",
	"таб", "целтаб", "вещтаб", "логтаб", "симтаб", "литтаб"
];
const booleanKeywords = [
	"и", "или", "не", "да", "нет"
];
const ioKeywords = [
	"утв", "ввод", "вывод", "выход"
];
const flowKeywords = [
	"нс", "если", "то", "иначе", "все", "выбор",
	"при", "нц", "кц", "кц_при", "раз", "пока",
	"для", "от", "до", "шаг"
];
const robotCommands = [
	"Робот",
	"влево", "вправо", "вверх", "вниз", "закрасить",
	"слева свободно", "справа свободно", "сверху свободно", "снизу свободно",
	"слева стена", "справа стена", "сверху стена", "снизу стена",
	"клетка закрашена", "клетка чистая",
	"температура", "радиация"
];

// --- Функция генерации RegExp для ключевых слов ---
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

const CodeEditor = memo(({
	                         code,
	                         setCode,
	                         isRunning,
	                         onClearCode,
	                         onStop,
	                         onStart,
	                         onReset,
	                         statusText,    // Строка с текущим статусом (например, позиция робота, маркеры и т.д.)
	                         consoleOutput  // Строка с выводом (ответами сервера)
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

			{/* Панель управления: кнопки */}
			<div className="editor-controls">
				<Button
					variant="contained"
					color="info"
					className="editor-button"
					onClick={onClearCode}
				>
					<Delete/>
				</Button>

				<Button
					variant="contained"
					color="error"
					className="editor-button"
					onClick={onStop}
					disabled={!isRunning}
				>
					<Stop/>
				</Button>

				<Button
					variant="contained"
					color="success"
					className="editor-button"
					onClick={onStart}
					disabled={isRunning}
				>
					<PlayArrow/>
				</Button>

				<Button
					variant="outlined"
					color="warning"
					className="editor-button"
					onClick={onReset}
				>
					<Refresh/>
				</Button>
			</div>

			{/* Статус */}
			<Card className="status-card">
				<Typography variant="body2" className="status-text">
					{statusText}
				</Typography>
			</Card>

			{/* Консоль для вывода ответов сервера */}
			<Card className="console-card">
				<Typography variant="body2" className="console-text">
					{consoleOutput}
				</Typography>
			</Card>
		</div>
	);
});

export default CodeEditor;
