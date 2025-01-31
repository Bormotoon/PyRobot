import React, {memo, useCallback} from 'react';
import {Button, Typography} from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';

/* Иконки MUI */
import {Delete, Stop, PlayArrow, Refresh} from '@mui/icons-material';

import './CodeEditor.css';

/**
 * Определение языка Кумир для Prism
 */
Prism.languages.kumir = {
	keyword: /\b(использовать|Робот|алг|нач|кон|влево|вправо|вверх|вниз|закрасить|если|иначе|для|пока|температура|радиация)\b/g,
	comment: /#.*/g,
	string: /".*?"/g,
	number: /\b\d+\b/g,
	operator: /\b(==|!=|<=|>=|<|>|\+|\-|\*|\/)\b/g,
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
