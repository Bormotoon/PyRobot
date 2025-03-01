/**
 * @file CodeEditor.jsx
 * @description Компонент редактора кода для симулятора робота.
 */

import React, {memo, useCallback, useState} from 'react';
import {Button, Card, Typography, Slider} from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import {Delete, PlayArrow, Refresh, Stop} from '@mui/icons-material';
import './CodeEditor.css';
import UserLog from '../UserLog/UserLog';

const structuralKeywords = ["алг", "нач", "кон", "исп", "кон_исп", "использовать"];
const typeKeywords = ["дано", "надо", "арг", "рез", "аргрез", "знач", "цел", "вещ", "лог", "сим", "лит", "таб", "целтаб", "вещтаб", "логтаб", "симтаб", "литтаб"];
const booleanKeywords = ["и", "или", "не", "да", "нет"];
const ioKeywords = ["утв", "ввод", "вывод", "выход"];
const flowKeywords = ["нс", "если", "то", "иначе", "все", "выбор", "при", "нц", "кц", "кц_при", "раз", "пока", "для", "от", "до", "шаг"];
const robotCommands = ["Робот", "влево", "вправо", "вверх", "вниз", "закрасить", "слева свободно", "справа свободно", "сверху свободно", "снизу свободно", "слева стена", "справа стена", "сверху стена", "снизу стена", "клетка закрашена", "клетка чистая", "температура", "радиация"];

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
	                         statusText,
	                         steps = [],
	                         error = '', // Добавляем пропс error
                         }) => {
	const highlightCode = useCallback((inputCode) => {
		return Prism.highlight(inputCode, Prism.languages.kumir, 'kumir');
	}, []);

	const [speed, setSpeed] = useState(2);
	const speedValues = [2000, 1000, 500, 250, 0];

	const handleSpeedChange = (event, newValue) => {
		setSpeed(newValue);
	};

	const handleStartWithSpeed = () => {
		onStart(speedValues[speed]);
	};

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
				<Button variant="contained" color="success" className="editor-button" onClick={handleStartWithSpeed}
				        disabled={isRunning}>
					<PlayArrow/>
				</Button>
				<Button variant="outlined" color="warning" className="editor-button" onClick={onReset}>
					<Refresh/>
				</Button>
			</div>

			<Card className="status-card">
				<Typography variant="body2" className="status-text">
					{statusText}
				</Typography>
			</Card>

			<div style={{padding: '10px', width: '100%'}}>
				<Typography gutterBottom>Скорость исполнения</Typography>
				<Slider
					value={speed}
					onChange={handleSpeedChange}
					min={0}
					max={4}
					step={1}
					marks={[
						{value: 0, label: '2с'},
						{value: 1, label: '1с'},
						{value: 2, label: '0.5с'},
						{value: 3, label: '0.25с'},
						{value: 4, label: 'Мгновенно'},
					]}
					disabled={isRunning}
				/>
			</div>

			<Card className="console-card">
				<UserLog steps={steps} error={error}/>
			</Card>
		</div>
	);
});

export default CodeEditor;