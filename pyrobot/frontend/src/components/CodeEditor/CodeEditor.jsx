import React, {memo, useCallback} from 'react';
import {Button, Typography} from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';

/* Иконки MUI */
import {Delete, Stop, PlayArrow, Refresh} from '@mui/icons-material';

import './CodeEditor.css';

// Группы ключевых слов
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
	// Название исполнителя
	"Робот",

	// Команды-действия
	"влево", "вправо", "вверх", "вниз", "закрасить",

	// Команды-проверки (логические)
	"слева свободно", "справа свободно", "сверху свободно", "снизу свободно",
	"слева стена", "справа стена", "сверху стена", "снизу стена",
	"клетка закрашена", "клетка чистая",

	// Команды-измерения
	"температура", "радиация"
];


// Функция, которая генерирует RegExp для массива слов:
function makeKumirRegex(words) {
	// Пример: (?:алг|нач|кон|...) - без скобок
	const alternatives = words.join("|");
	// lookbehind: true => обязательно (^) или пробел захватывается "позади"
// 'i' — флаг нестрогого регистра (если нужно),
// можно убрать, если хотим строго строчные
	return {
		pattern: new RegExp(`(^|\\s)(?:${alternatives})(?=$|\\s)`, "i"),
		lookbehind: true
	};
}

Prism.languages.kumir = {
	// 1) Структурные ключевые слова
	"keyword-struct": makeKumirRegex(structuralKeywords),

	// 2) Типы, декларации
	"keyword-type": makeKumirRegex(typeKeywords),

	// 3) Логика, булевы значения
	"keyword-bool": makeKumirRegex(booleanKeywords),

	// 4) Ввод/вывод
	"keyword-io": makeKumirRegex(ioKeywords),

	// 5) Управление потоком
	"keyword-flow": makeKumirRegex(flowKeywords),

	// 6) Исполнитель Робот
	"robot-command": makeKumirRegex(robotCommands),

	// Комментарии
	comment: /#.*/,

	// Строки (одинарные/двойные кавычки)
	string: {
		pattern: /(["'])(?:(?!\1).)*\1/,
		greedy: true
	},

	// Числа: десятичные, отрицательные, шестнадцатеричные с '$', + «e/E/е/Е»
	number: {
		pattern: /-?\$[0-9A-Fa-f]+|-?\d+(?:\.\d+)?(?:[еeЕE][-+]?\d+)?/
	},

	// Операторы
	operator: /(?:\*\*|<=|>=|<>|!=|==|[+\-*/<>=])/

};


const CodeEditor = memo(({
	                         code,
	                         setCode,
	                         isRunning,
	                         onClearCode,
	                         onStop,
	                         onStart,
	                         onReset
                         }) => {

	// Функция подсветки кода
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
				{/* Очистить */}
				<Button
					variant="contained"
					color="info"
					className="editor-button"
					onClick={onClearCode}
					fullWidth
				>
					<Delete/>
					Очистить
				</Button>

				{/* Стоп */}
				<Button
					variant="contained"
					color="error"
					className="editor-button"
					onClick={onStop}
					disabled={!isRunning}
					fullWidth
				>
					<Stop/>
					Стоп
				</Button>

				{/* Пуск */}
				<Button
					variant="contained"
					color="success"
					className="editor-button"
					onClick={onStart}
					disabled={isRunning}
					fullWidth
				>
					<PlayArrow/>
					Пуск
				</Button>

				{/* Сброс */}
				<Button
					variant="outlined"
					color="warning"
					className="editor-button"
					onClick={onReset}
					fullWidth
				>
					<Refresh/>
					Сброс
				</Button>
			</div>
		</div>
	);
});

export default CodeEditor;
