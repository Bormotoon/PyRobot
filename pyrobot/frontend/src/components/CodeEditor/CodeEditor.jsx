/**
 * @file CodeEditor.jsx
 * @description Компонент редактора кода для симулятора робота.
 */

import React, {memo, useCallback, useState} from 'react';
import {
    Button, 
    Card, 
    CardContent, 
    Typography, 
    Slider, 
    Box,
    Paper,
    IconButton,
    Tooltip,
    Divider
} from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import {
    Delete, 
    PlayArrow, 
    Refresh, 
    Stop, 
    Code,
    Speed
} from '@mui/icons-material';
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
	                         speedLevel = 2,
	                         onSpeedChange,
	                         steps = [],
	                         error = '',
                         }) => {
	const highlightCode = useCallback((inputCode) => {
		return Prism.highlight(inputCode, Prism.languages.kumir, 'kumir');
	}, []);

	const handleSpeedChange = (event, newValue) => {
		if (onSpeedChange) {
			onSpeedChange(newValue);
		}
	};

	return (
		<Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, height: '100%' }}>
			{/* Заголовок с иконкой */}
			<Card elevation={2} sx={{ borderRadius: 3, display: 'flex', flexDirection: 'column' }}>
				<CardContent sx={{ 
					pb: { xs: 1, sm: 1.5 }, 
					px: { xs: 2, sm: 3 },
					display: 'flex',
					flexDirection: 'column',
					flexGrow: 1
				}}>
					<Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: { xs: 1, sm: 1.5 } }}>
						<Code color="primary" sx={{ fontSize: { xs: '1.2rem', sm: '1.5rem' } }} />
						<Typography 
							variant="h6" 
							component="h2" 
							fontWeight={600}
							sx={{ fontSize: { xs: '1rem', sm: '1.25rem' } }}
						>
							Редактор Кода
						</Typography>
					</Box>

					{/* Редактор кода */}
					<Paper 
						elevation={1} 
						sx={{ 
							borderRadius: 2, 
							overflow: 'hidden',
							border: '1px solid',
							borderColor: 'divider',
							flexGrow: 1,
							display: 'flex',
							flexDirection: 'column',
							minHeight: 'clamp(120px, 15vh, 180px)',
							maxHeight: 'clamp(180px, 25vh, 280px)',
						}}
					>
						<Editor
							value={code}
							onValueChange={setCode}
							highlight={highlightCode}
							padding={16}
							className="react-simple-code-editor"
							style={{
								fontFamily: 'var(--font-family-monospace)',
								fontSize: 'clamp(12px, 2vw, 14px)',
								lineHeight: '1.5',
								height: '100%',
								backgroundColor: 'var(--background-color-code-editor)',
							}}
						/>
					</Paper>

					{/* Кнопки управления */}
					<Box sx={{ 
						display: 'flex', 
						gap: { xs: 0.3, sm: 0.5, md: 0.8 }, 
						mt: 1.5, 
						flexWrap: 'nowrap',
						alignItems: 'center',
						justifyContent: 'center',
						overflowX: 'auto',
						pb: 0.5,
						flexShrink: 0
					}}>
						<Tooltip title="Очистить код">
							<Button 
								variant="outlined" 
								color="secondary" 
								startIcon={<Delete />}
								onClick={onClearCode}
								disabled={isRunning}
								sx={{ 
									borderRadius: 2, 
									minWidth: 'auto', 
									px: { xs: 0.5, sm: 1 },
									fontSize: { xs: '0.7rem', sm: '0.75rem' },
									'& .MuiButton-startIcon': {
										marginRight: { xs: 0.3, sm: 0.5 }
									}
								}}
								size="small"
							>
								<Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>
									Очистить
								</Box>
							</Button>
						</Tooltip>
						
						<Tooltip title="Остановить выполнение">
							<Button 
								variant="contained" 
								color="error" 
								startIcon={<Stop />}
								onClick={onStop}
								disabled={!isRunning}
								sx={{ 
									borderRadius: 2, 
									minWidth: 'auto', 
									px: { xs: 0.5, sm: 1 },
									fontSize: { xs: '0.7rem', sm: '0.75rem' },
									'& .MuiButton-startIcon': {
										marginRight: { xs: 0.3, sm: 0.5 }
									}
								}}
								size="small"
							>
								<Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>
									Стоп
								</Box>
							</Button>
						</Tooltip>
						
						<Tooltip title="Запустить код">
							<Button 
								variant="contained" 
								color="success" 
								startIcon={<PlayArrow />}
								onClick={onStart}
								disabled={isRunning}
								sx={{ 
									borderRadius: 2, 
									minWidth: 'auto', 
									px: { xs: 0.5, sm: 1 },
									fontSize: { xs: '0.7rem', sm: '0.75rem' },
									'& .MuiButton-startIcon': {
										marginRight: { xs: 0.3, sm: 0.5 }
									}
								}}
								size="small"
							>
								<Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>
									Запуск
								</Box>
							</Button>
						</Tooltip>
						
						<Tooltip title="Сбросить состояние">
							<Button 
								variant="outlined" 
								color="warning" 
								startIcon={<Refresh />}
								onClick={onReset}
								disabled={isRunning}
								sx={{ 
									borderRadius: 2, 
									minWidth: 'auto', 
									px: { xs: 0.5, sm: 1 },
									fontSize: { xs: '0.7rem', sm: '0.75rem' },
									'& .MuiButton-startIcon': {
										marginRight: { xs: 0.3, sm: 0.5 }
									}
								}}
								size="small"
							>
								<Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>
									Сброс
								</Box>
							</Button>
						</Tooltip>
					</Box>
				</CardContent>
			</Card>

			{/* Контроль скорости */}
			<Card elevation={1} sx={{ borderRadius: 3, flexShrink: 0 }}>
				<CardContent sx={{ 
					pb: { xs: 1.5, sm: 2 }, 
					px: { xs: 2, sm: 3 },
					py: { xs: 1.5, sm: 2 }
				}}>
					<Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: { xs: 1, sm: 1.5 } }}>
						<Speed color="primary" fontSize="small" />
						<Typography 
							variant="subtitle2" 
							fontWeight={500}
							sx={{ fontSize: { xs: '0.8rem', sm: '0.875rem' } }}
						>
							Скорость выполнения
						</Typography>
					</Box>
					
					<Box sx={{ px: { xs: 0.5, sm: 1 } }}>
						<Slider
							value={speedLevel}
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
							sx={{
								'& .MuiSlider-mark': {
									backgroundColor: 'primary.main',
								},
								'& .MuiSlider-markLabel': {
									fontSize: { xs: '10px', sm: '11px' },
									'@media (max-width: 400px)': {
										fontSize: '9px',
									}
								},
								'& .MuiSlider-thumb': {
									width: { xs: 16, sm: 20 },
									height: { xs: 16, sm: 20 },
								},
								'& .MuiSlider-track': {
									height: { xs: 2, sm: 3 },
								},
								'& .MuiSlider-rail': {
									height: { xs: 2, sm: 3 },
								},
							}}
						/>
					</Box>
				</CardContent>
			</Card>

			{/* Консоль выполнения */}
			<Box sx={{ 
				height: '25vh',
				minHeight: '150px',
				maxHeight: '400px',
				flexShrink: 0,
				display: 'flex',
				flexDirection: 'column'
			}}>
				<UserLog steps={steps} error={error} />
			</Box>
		</Box>
	);
});

export default CodeEditor;