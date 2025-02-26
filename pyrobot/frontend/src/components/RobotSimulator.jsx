import React, {memo, useCallback, useEffect, useReducer, useRef, useState} from 'react';
import {ThemeProvider, Typography} from '@mui/material';
import CodeEditor from './CodeEditor/CodeEditor';
import ControlPanel from './ControlPanel/ControlPanel';
import Field from './Field/Field';
import theme from '../styles/theme';
import {getHint} from './hints';
import logger from '../Logger';
import io from 'socket.io-client';

const initialState = {
	code: `использовать Робот\nалг\nнач\n  вправо\n  вниз\n  вправо\nкон`,
	isRunning: false,
	statusMessage: getHint('initial'),
	width: 7,
	height: 7,
	cellSize: 50,
	robotPos: {x: 0, y: 0},
	walls: new Set(),
	permanentWalls: new Set(),
	markers: {},
	coloredCells: new Set(),
	editMode: false,
};

function reducer(state, action) {
	switch (action.type) {
		case 'SET_CODE':
			return {...state, code: action.payload};
		case 'SET_IS_RUNNING':
			return {...state, isRunning: action.payload};
		case 'SET_STATUS_MESSAGE':
			return {...state, statusMessage: action.payload};
		case 'SET_ROBOT_POS':
			return {...state, robotPos: action.payload};
		case 'SET_WIDTH':
			return {...state, width: action.payload};
		case 'SET_HEIGHT':
			return {...state, height: action.payload};
		case 'SET_CELL_SIZE':
			return {...state, cellSize: action.payload};
		case 'SET_WALLS':
			return {
				...state,
				walls: typeof action.payload === 'function' ? action.payload(state.walls) : new Set(action.payload),
			};
		case 'SET_PERMANENT_WALLS':
			return {
				...state,
				permanentWalls: typeof action.payload === 'function' ? action.payload(state.permanentWalls) : new Set(action.payload),
			};
		case 'SET_MARKERS':
			return {
				...state,
				markers: typeof action.payload === 'function' ? action.payload(state.markers) : action.payload,
			};
		case 'SET_COLORED_CELLS':
			return {
				...state,
				coloredCells: typeof action.payload === 'function' ? action.payload(state.coloredCells) : new Set(action.payload),
			};
		case 'SET_EDIT_MODE':
			return {...state, editMode: action.payload};
		default:
			return state;
	}
}

function setupPermanentWalls(width, height) {
	const newWalls = new Set();
	for (let x = 0; x < width; x++) {
		newWalls.add(`${x},0,${x + 1},0`);
		newWalls.add(`${x},${height},${x + 1},${height}`);
	}
	for (let y = 0; y < height; y++) {
		newWalls.add(`0,${y},0,${y + 1}`);
		newWalls.add(`${width},${y},${width},${y + 1}`);
	}
	return newWalls;
}

function clampRobotPos(robotPos, width, height) {
	const clampedX = Math.min(Math.max(robotPos.x, 0), width - 1);
	const clampedY = Math.min(Math.max(robotPos.y, 0), height - 1);
	return {x: clampedX, y: clampedY};
}

const RobotSimulator = memo(() => {
	const [state, dispatch] = useReducer(reducer, initialState);
	const [progress, setProgress] = useState(null);
	const canvasRef = useRef(null);
	const socketRef = useRef(null);
	const prevEditMode = useRef(state.editMode);

	// Подключение к WebSocket-серверу
	useEffect(() => {
		socketRef.current = io('http://localhost:5000');
		socketRef.current.on('execution_progress', (data) => {
			// data: { phase, commandIndex, output, robotPos }
			setProgress(data);
			logger.log_event(`Прогресс: Фаза ${data.phase}, Команда ${data.commandIndex}`);
			// Если сервер отправил обновлённую позицию робота, обновляем её
			if (data.robotPos) {
				dispatch({type: 'SET_ROBOT_POS', payload: data.robotPos});
			}
		});
		return () => {
			if (socketRef.current) {
				socketRef.current.disconnect();
			}
		};
	}, []);

	const handleClearCode = useCallback(() => {
		dispatch({type: 'SET_CODE', payload: ''});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код программы очищен.'});
		logger.log_event('Код программы очищен.');
	}, []);

	const handleStop = useCallback(() => {
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Выполнение остановлено.'});
		logger.log_event('Выполнение остановлено.');
	}, []);

	const handleStart = useCallback(() => {
		if (!state.code.trim()) {
			dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Ошибка: программа пустая.'});
			logger.log_error('Программа пустая.');
			return;
		}
		dispatch({type: 'SET_IS_RUNNING', payload: true});
		setProgress(null);
		fetch('http://localhost:5000/execute', {
			method: 'POST',
			credentials: 'include',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({code: state.code}),
		})
			.then((response) => response.json())
			.then((data) => {
				// После завершения выполнения кода обновляем финальное состояние
				if (data.success) {
					dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код выполнен успешно.'});
					logger.log_event('Код выполнен успешно.');
					if (!state.editMode) {
						dispatch({type: 'SET_ROBOT_POS', payload: data.robot});
					}
					dispatch({type: 'SET_COLORED_CELLS', payload: new Set(data.coloredCells)});
				} else {
					const errorMsg = 'Ошибка: ' + data.message + (data.output ? "\n" + data.output : "");
					dispatch({type: 'SET_STATUS_MESSAGE', payload: errorMsg});
					logger.log_error(errorMsg);
				}
				dispatch({type: 'SET_IS_RUNNING', payload: false});
			})
			.catch((error) => {
				console.error('Ошибка выполнения запроса:', error);
				dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Ошибка выполнения запроса.'});
				logger.log_error('Ошибка выполнения запроса.');
				dispatch({type: 'SET_IS_RUNNING', payload: false});
			});
	}, [state.code, state.editMode]);

	const handleReset = useCallback(() => {
		dispatch({type: 'SET_ROBOT_POS', payload: {x: 0, y: 0}});
		dispatch({type: 'SET_WALLS', payload: new Set()});
		dispatch({type: 'SET_COLORED_CELLS', payload: new Set()});
		dispatch({type: 'SET_MARKERS', payload: {}});
		dispatch({type: 'SET_WIDTH', payload: 7});
		dispatch({type: 'SET_HEIGHT', payload: 7});
		dispatch({type: 'SET_CODE', payload: `использовать Робот\nалг\nнач\n  # Ваши команды здесь\nкон`});
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Симулятор сброшен (демо).'});
		logger.log_event('Симулятор сброшен (демо).');
	}, []);

	useEffect(() => {
		const newWalls = setupPermanentWalls(state.width, state.height);
		dispatch({type: 'SET_PERMANENT_WALLS', payload: newWalls});
		const newPos = clampRobotPos(state.robotPos, state.width, state.height);
		if (newPos.x !== state.robotPos.x || newPos.y !== state.robotPos.y) {
			dispatch({type: 'SET_ROBOT_POS', payload: newPos});
		}
	}, [state.width, state.height, state.robotPos]);

	useEffect(() => {
		const timeout = setTimeout(() => {
			const fieldState = {
				width: state.width,
				height: state.height,
				cellSize: state.cellSize,
				robotPos: state.robotPos,
				walls: Array.from(state.walls),
				permanentWalls: Array.from(state.permanentWalls),
				markers: state.markers,
				coloredCells: Array.from(state.coloredCells),
			};
			fetch('http://localhost:5000/updateField', {
				method: 'POST',
				credentials: 'include',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify(fieldState),
			}).catch((e) => console.error("Ошибка обновления поля на сервере:", e));
		}, 200);
		return () => clearTimeout(timeout);
	}, [
		state.width,
		state.height,
		state.cellSize,
		state.robotPos,
		state.walls,
		state.permanentWalls,
		state.markers,
		state.coloredCells,
	]);

	useEffect(() => {
		if (prevEditMode.current && !state.editMode) {
			// Этот эффект не требуется
		}
		prevEditMode.current = state.editMode;
	}, [state.editMode]);

	const statusText = [
		`Позиция робота: (${state.robotPos.x}, ${state.robotPos.y})`,
		`Маркеров: ${Object.keys(state.markers).length}`,
		`Раскрашенных клеток: ${state.coloredCells.size}`,
	].join('\n');

	// Отображение прогресса выполнения
	const renderProgress = () => {
		if (!progress) return null;
		return (
			<div className="progress-bar" style={{padding: '8px', backgroundColor: '#f0f0f0', marginTop: '16px'}}>
				<Typography variant="body2">
					Фаза: {progress.phase}, Команда: {progress.commandIndex}
				</Typography>
				<Typography variant="body2">
					Вывод: {progress.output}
				</Typography>
			</div>
		);
	};

	return (
		<ThemeProvider theme={theme}>
			<div className="app-container">
				<CodeEditor
					code={state.code}
					setCode={(newCode) => dispatch({type: 'SET_CODE', payload: newCode})}
					isRunning={state.isRunning}
					onClearCode={handleClearCode}
					onStop={handleStop}
					onStart={handleStart}
					onReset={handleReset}
					statusText={statusText}
				/>
				<ControlPanel
					robotPos={state.robotPos}
					setRobotPos={(pos) => dispatch({type: 'SET_ROBOT_POS', payload: pos})}
					walls={state.walls}
					setWalls={(newWalls) => dispatch({type: 'SET_WALLS', payload: newWalls})}
					permanentWalls={state.permanentWalls}
					markers={state.markers}
					setMarkers={(m) => dispatch({type: 'SET_MARKERS', payload: m})}
					coloredCells={state.coloredCells}
					setColoredCells={(c) => dispatch({type: 'SET_COLORED_CELLS', payload: c})}
					width={state.width}
					setWidth={(val) => dispatch({type: 'SET_WIDTH', payload: val})}
					height={state.height}
					setHeight={(val) => dispatch({type: 'SET_HEIGHT', payload: val})}
					cellSize={state.cellSize}
					setCellSize={(val) => dispatch({type: 'SET_CELL_SIZE', payload: val})}
					editMode={state.editMode}
					setEditMode={(val) => dispatch({type: 'SET_EDIT_MODE', payload: val})}
					setStatusMessage={(msg) => dispatch({type: 'SET_STATUS_MESSAGE', payload: msg})}
				/>
				<Field
					canvasRef={canvasRef}
					robotPos={state.robotPos}
					setRobotPos={(pos) => dispatch({type: 'SET_ROBOT_POS', payload: pos})}
					walls={state.walls}
					setWalls={(newWalls) => dispatch({type: 'SET_WALLS', payload: newWalls})}
					permanentWalls={state.permanentWalls}
					markers={state.markers}
					setMarkers={(m) => dispatch({type: 'SET_MARKERS', payload: m})}
					coloredCells={state.coloredCells}
					setColoredCells={(c) => dispatch({type: 'SET_COLORED_CELLS', payload: c})}
					width={state.width}
					height={state.height}
					cellSize={state.cellSize}
					editMode={state.editMode}
					statusMessage={state.statusMessage}
					setStatusMessage={(msg) => dispatch({type: 'SET_STATUS_MESSAGE', payload: msg})}
				/>
				{renderProgress()}
			</div>
		</ThemeProvider>
	);
});

export default RobotSimulator;
