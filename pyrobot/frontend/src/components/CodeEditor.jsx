import React, {memo, useCallback} from 'react';
import {Button, Typography} from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';

Prism.languages.kumir = {
	keyword: /\b(использовать|Робот|алг|нач|кон|влево|вправо|вверх|вниз|закрасить|если|иначе|для|пока|температура|радиация)\b/g,
	comment: /#.*/g,
	string: /".*?"/g,
	number: /\b\d+\b/g,
	operator: /\b(==|!=|<=|>=|<|>|\+|\-|\*|\/)\b/g,
};

const CodeEditor = memo(
	({code, setCode, isRunning, onClearCode, onStop, onStart, onReset}) => {
		const highlightCode = useCallback((inputCode) => {
			return Prism.highlight(inputCode, Prism.languages.kumir, 'kumir');
		}, []);

		return (
			<div className="card code-editor">
				<Typography variant="h5" gutterBottom style={{color: '#fff'}}>
					Редактор Кода
				</Typography>
				<Editor
					value={code}
					onValueChange={setCode}
					highlight={highlightCode}
					padding={10}
					className="react-simple-code-editor"
					style={{
						fontFamily: '"Fira Code", monospace',
						fontSize: 14,
						flex: '1 1 auto',
						overflow: 'auto',
					}}
				/>
				<div className="editor-controls">
					<Button variant="contained" color="secondary" onClick={onClearCode} fullWidth>
						Очистить
					</Button>
					<Button variant="contained" color="error" onClick={onStop} disabled={!isRunning} fullWidth>
						Стоп
					</Button>
					<Button variant="contained" color="success" onClick={onStart} disabled={isRunning} fullWidth>
						Пуск
					</Button>
					<Button variant="outlined" color="primary" onClick={onReset} fullWidth>
						Сбросить симулятор
					</Button>
				</div>
			</div>
		);
	}
);

export default CodeEditor;