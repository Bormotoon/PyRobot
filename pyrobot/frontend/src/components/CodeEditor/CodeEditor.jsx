import React, {memo, useCallback} from 'react';
import {Button, Typography} from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
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
				{/* Очистка кода */}
				<Button
					variant="contained"
					color="info"
					className="control-button"
					onClick={onClearCode}
					fullWidth
				>
					Очистить
				</Button>

				{/* Стоп */}
				<Button
					variant="contained"
					color="error"
					className="control-button"
					onClick={onStop}
					disabled={!isRunning}
					fullWidth
				>
					Стоп
				</Button>

				{/* Пуск */}
				<Button
					variant="contained"
					color="success"
					className="control-button"
					onClick={onStart}
					disabled={isRunning}
					fullWidth
				>
					Пуск
				</Button>

				{/* Сброс */}
				<Button
					variant="outlined"
					color="warning"
					className="control-button"
					onClick={onReset}
					fullWidth
				>
					Сброс
				</Button>
			</div>
		</div>
	);
});

export default CodeEditor;
