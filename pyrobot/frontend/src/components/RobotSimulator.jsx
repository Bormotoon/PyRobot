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
	markers: {}, // { "x,y": 1 }
	coloredCells: new Set(), // { "x,y" }
	symbols: {}, // { "x,y": { upper: 'A', lower: 'Б' } } <-- Initial empty symbols
	editMode: false,
};

// Helper Functions (clampRobotPos, setupPermanentWalls)
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
	if (robotPos.x !== clampedX || robotPos.y !== clampedY) {
		return {x: clampedX, y: clampedY};
	}
	return robotPos;
}

// Reducer function
function reducer(state, action) {
	// <<< Add Logging inside Reducer >>>
	// Use a structured log for better readability in console
	console.groupCollapsed(`%cReducer Action: ${action.type}`, 'color: red;');
	console.log('Payload:', action.payload);
	console.log('State Before:', JSON.parse(JSON.stringify(state, (key, value) => value instanceof Set ? Array.from(value) : value)));
	// <<< --------------------------- >>>

	let nextState; // Calculate next state before logging it

	switch (action.type) {
		case 'SET_CODE':
			nextState = {...state, code: action.payload};
			break;
		case 'SET_IS_RUNNING':
			nextState = {...state, isRunning: action.payload};
			break;
		case 'SET_STATUS_MESSAGE':
			nextState = {...state, statusMessage: action.payload};
			break;
		case 'SET_ROBOT_POS':
			const clampedPos = clampRobotPos(action.payload, state.width, state.height);
			nextState = {...state, robotPos: clampedPos};
			break;
		case 'SET_WIDTH': {
			const newWidth = Math.max(1, action.payload);
			const robotAfterWidthChange = clampRobotPos(state.robotPos, newWidth, state.height);
			nextState = {
				...state, width: newWidth, robotPos: robotAfterWidthChange,
				permanentWalls: setupPermanentWalls(newWidth, state.height)
			};
			break;
		}
		case 'SET_HEIGHT': {
			const newHeight = Math.max(1, action.payload);
			const robotAfterHeightChange = clampRobotPos(state.robotPos, state.width, newHeight);
			nextState = {
				...state, height: newHeight, robotPos: robotAfterHeightChange,
				permanentWalls: setupPermanentWalls(state.width, newHeight)
			};
			break;
		}
		case 'SET_CELL_SIZE':
			nextState = {...state, cellSize: Math.max(10, action.payload)};
			break;
		case 'SET_WALLS':
			nextState = {
				...state,
				walls: typeof action.payload === 'function' ? action.payload(state.walls) : new Set(action.payload)
			};
			break;
		case 'SET_PERMANENT_WALLS':
			nextState = {...state, permanentWalls: new Set(action.payload)};
			break;
		case 'SET_MARKERS':
			nextState = {
				...state,
				markers: typeof action.payload === 'function' ? action.payload(state.markers) : action.payload
			};
			break;
		case 'SET_COLORED_CELLS':
			nextState = {
				...state,
				coloredCells: typeof action.payload === 'function' ? action.payload(state.coloredCells) : new Set(action.payload)
			};
			break;
		case 'SET_SYMBOLS':
			// Log specifically when symbols are set
			console.log('%cSetting Symbols:', 'color: magenta; font-weight: bold;', action.payload);
			nextState = {
				...state,
				symbols: typeof action.payload === 'function' ? action.payload(state.symbols) : action.payload
			};
			break;
		case 'SET_EDIT_MODE':
			nextState = {...state, editMode: action.payload};
			break;
		case 'RESET_STATE': {
			const resetWidth = initialState.width;
			const resetHeight = initialState.height;
			nextState = {
				...initialState,
				width: resetWidth, height: resetHeight,
				permanentWalls: setupPermanentWalls(resetWidth, resetHeight),
				robotPos: clampRobotPos(initialState.robotPos, resetWidth, resetHeight),
				statusMessage: 'Симулятор сброшен.',
			};
			break;
		}
		default:
			throw new Error(`Unknown action type: ${action.type}`);
	}
	// <<< Log State After and End Group >>>
	console.log('State After:', JSON.parse(JSON.stringify(nextState, (key, value) => value instanceof Set ? Array.from(value) : value)));
	console.groupEnd();
	// <<< ----------------------------- >>>
	return nextState; // Return the calculated next state
}

// Component Definition
const RobotSimulator = memo(() => {
	const [state, dispatch] = useReducer(reducer, initialState, (init) => ({
		...init,
		permanentWalls: setupPermanentWalls(init.width, init.height)
	}));

	const [animationSpeedLevel, setAnimationSpeedLevel] = useState(2);
	const canvasRef = useRef(null);
	const socketRef = useRef(null);
	const isMountedRef = useRef(true);
	const animationControllerRef = useRef({
		stop: () => {
		}, isRunning: false
	}); // Added isRunning flag

	// <<< Add Component Render Logging >>>
	// Use JSON.stringify with a replacer for Sets to avoid issues with logging complex state
	const stateToLog = JSON.stringify(state, (key, value) => {
		if (value instanceof Set) {
			return Array.from(value);
		} // Convert Sets to Arrays for logging
		return value;
	}, 2); // Indent for readability
	console.log('%cRobotSimulator Render - State:', 'color: blue; font-weight: bold;', JSON.parse(stateToLog)); // Log full state on render
	// <<< ---------------------------- >>>


	useEffect(() => { // WebSocket setup
		isMountedRef.current = true;
		socketRef.current = io('http://localhost:5000');

		socketRef.current.on('connection_ack', (data) => {
			if (isMountedRef.current) {
				logger.log_event(`WS OK SID: ${data.sid}`);
			}
		});

		socketRef.current.on('execution_progress', (data) => {
			// Log all progress messages for debugging
			console.debug("WS execution_progress received:", data);
			if (isMountedRef.current && state.isRunning && !animationControllerRef.current.isRunning) {
				const progressMsg = data.error
					? `WS Прогр: Ошибка ${data.commandIndex} (${data.phase}) - ${data.error}`
					: `WS Прогр: ${data.phase} ш.${data.commandIndex}`;
				// Update status message only if needed, animation might override
				dispatch({type: 'SET_STATUS_MESSAGE', payload: progressMsg});
			}
		});

		return () => { // Cleanup
			isMountedRef.current = false;
			animationControllerRef.current.stop();
			if (socketRef.current) {
				socketRef.current.disconnect();
				logger.log_event('WS откл.');
			}
		};
	}, []); // Run once

	// Handlers
	const handleClearCode = useCallback(() => {
		dispatch({type: 'SET_CODE', payload: `использовать Робот\nалг\nнач\n  \nкон`});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код очищен.'});
		logger.log_event('Код очищен.');
	}, []);
	const handleStop = useCallback(() => {
		animationControllerRef.current.stop();
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Остановлено.'});
		logger.log_event('Остановлено.');
	}, []);
	const handleReset = useCallback(() => {
		animationControllerRef.current.stop();
		dispatch({type: 'RESET_STATE'});
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		logger.log_event('Симулятор сброшен.');
		fetch('http://localhost:5000/reset', {
			method: 'POST',
			credentials: 'include'
		}).catch(e => logger.log_error(`Ошибка /reset: ${e.message}`));
	}, []);

	// Animation function
	const animateTrace = useCallback(async (trace) => {
		if (!trace || trace.length === 0) {
			console.warn("animateTrace called with empty trace.");
			return {completed: true};
		}
		let shouldContinue = true;
		const stop = () => {
			shouldContinue = false;
		};
		animationControllerRef.current = {stop, isRunning: true};
		const delay = Math.max(50, 2000 - animationSpeedLevel * 480);
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация...'});
		console.groupCollapsed(`%cStarting Animation (Speed Level: ${animationSpeedLevel}, Delay: ${delay}ms)`, 'color: green');
		console.log("Trace data:", trace);
		console.groupEnd();

		for (let i = 0; i < trace.length; i++) {
			const event = trace[i];
			console.debug(`%cAnimation Step ${i + 1}/${trace.length}`, 'color: darkcyan', event);

			if (!isMountedRef.current || !shouldContinue) {
				logger.log_event('Анимация прервана.');
				animationControllerRef.current.isRunning = false;
				return {completed: false};
			}

			if (event.stateAfter) {
				console.debug("Applying state:", event.stateAfter);
				if (event.stateAfter.robot) dispatch({type: 'SET_ROBOT_POS', payload: event.stateAfter.robot});
				if (event.stateAfter.coloredCells) dispatch({
					type: 'SET_COLORED_CELLS',
					payload: new Set(event.stateAfter.coloredCells)
				});
				if (event.stateAfter.symbols !== undefined) { // Check specifically for symbols presence
					dispatch({type: 'SET_SYMBOLS', payload: event.stateAfter.symbols}); // Update symbols state
				} else {
					console.warn("Event stateAfter missing 'symbols' field:", event);
				}
				const message = event.error ? `Ошибка: ${event.error} (Шаг ${i + 1})` : `Шаг ${i + 1}/${trace.length}: ${event.command || ''}`;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: message});
			} else {
				console.warn("Trace event missing stateAfter:", event);
				dispatch({type: 'SET_STATUS_MESSAGE', payload: `Обработка шага ${i + 1}... (нет stateAfter)`});
			}

			if (animationSpeedLevel < 4 && delay > 0) await new Promise(r => setTimeout(r, delay));

			if (event.error) {
				logger.log_error(`Анимация стоп (ошибка на шаге ${i + 1}): ${event.error}`);
				animationControllerRef.current.isRunning = false;
				return {completed: false, error: true};
			}
		}
		animationControllerRef.current.isRunning = false;
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация завершена.'});
		console.log("%cAnimation Completed Normally", 'color: green; font-weight: bold');
		return {completed: true};
	}, [animationSpeedLevel]);

	// Start execution handler
	const handleStart = useCallback(() => {
		if (state.isRunning) {
			logger.log_warning("Уже выполняется.");
			return;
		}
		if (!state.code.trim()) {
			dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код пуст.'});
			logger.log_error('Запуск пустого кода.');
			return;
		}
		dispatch({type: 'SET_IS_RUNNING', payload: true});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Выполнение...'});
		const currentFieldState = {
			width: state.width,
			height: state.height,
			robotPos: state.robotPos,
			walls: Array.from(state.walls),
			markers: state.markers,
			coloredCells: Array.from(state.coloredCells),
			symbols: state.symbols
		};
		console.log("%cSending /execute with state:", 'color: orange;', currentFieldState); // Log state sent
		fetch('http://localhost:5000/execute', {
			method: 'POST',
			credentials: 'include',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({code: state.code, fieldState: currentFieldState}),
		})
			.then(async (response) => {
				if (!response.ok) {
					let eM = `HTTP ${response.status}`;
					try {
						const d = await response.json();
						eM = d.message || eM;
					} catch (e) {
					}
					throw new Error(eM);
				}
				return response.json();
			})
			.then(async (data) => {
				console.log("%cReceived /execute response:", 'color: purple;', data); // Log response data
				if (!isMountedRef.current) return;
				let animRes = {completed: true};
				try {
					if (data.trace?.length) {
						console.log("Attempting animation...");
						animRes = await animateTrace(data.trace);
					} else logger.log_event("Нет трассировки.");
				} catch (animE) {
					console.error("Анимация err:", animE);
					logger.log_error(`JS ошибка анимации: ${animE}`);
				}
				if (!isMountedRef.current) return;

				if (data.success) {
					console.log("Applying final success state from backend.");
					dispatch({type: 'SET_ROBOT_POS', payload: data.robot});
					dispatch({type: 'SET_COLORED_CELLS', payload: new Set(data.coloredCells)});
					dispatch({type: 'SET_SYMBOLS', payload: data.symbols || {}}); // Apply final symbols
					if (animRes.completed) dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Выполнено успешно.'});
					logger.log_event('Успешно (бэк).');
				} else {
					const eMsg = `Ошибка бэка: ${data.message || '?'} ${data.output ? '\n' + data.output : ''}`;
					console.log("Applying final error state from backend.");
					if (data.robot) dispatch({type: 'SET_ROBOT_POS', payload: data.robot});
					if (data.coloredCells) dispatch({type: 'SET_COLORED_CELLS', payload: new Set(data.coloredCells)});
					if (data.symbols) dispatch({type: 'SET_SYMBOLS', payload: data.symbols}); // Apply symbols state at error
					dispatch({type: 'SET_STATUS_MESSAGE', payload: eMsg});
					logger.log_error(`Ошибка бэка: ${eMsg}`);
				}
				dispatch({type: 'SET_IS_RUNNING', payload: false});
			})
			.catch((error) => {
				if (!isMountedRef.current) return;
				console.error('Fetch /execute:', error);
				dispatch({type: 'SET_STATUS_MESSAGE', payload: `Ошибка сети: ${error.message}`});
				logger.log_error(`Fetch /execute: ${error.message}`);
				dispatch({type: 'SET_IS_RUNNING', payload: false});
			});
	}, [state.isRunning, state.code, state.width, state.height, state.robotPos, state.walls, state.markers, state.coloredCells, state.symbols, animateTrace]);

	// Effect to update field state on backend (debounced)
	useEffect(() => {
		const handler = setTimeout(() => {
			if (!isMountedRef.current) return;
			// <<< Log state being sent for /updateField >>>
			const fieldState = {
				width: state.width,
				height: state.height,
				cellSize: state.cellSize,
				robotPos: state.robotPos,
				walls: Array.from(state.walls),
				markers: state.markers,
				coloredCells: Array.from(state.coloredCells),
				symbols: state.symbols
			};
			const stateToLogForUpdate = JSON.stringify(fieldState, (key, value) => value instanceof Set ? Array.from(value) : value, 2);
			console.log('%cSending /updateField state (debounced):', 'color: #f5a623;', JSON.parse(stateToLogForUpdate));
			// <<< --------------------------------------- >>>
			fetch('http://localhost:5000/updateField', {
				method: 'POST',
				credentials: 'include',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify(fieldState),
			}).then(r => {
				if (isMountedRef.current && !r.ok) logger.log_warning(`Update field ${r.status}`);
			}).catch((e) => {
				if (isMountedRef.current) logger.log_error(`Update field fetch: ${e.message}`);
			});
		}, 500); // Increased debounce time slightly
		return () => clearTimeout(handler);
	}, [ // Dependencies include symbols now
		state.width, state.height, state.cellSize, state.robotPos,
		state.walls, state.markers, state.coloredCells, state.symbols
	]);

	// Effect to ensure permanent walls match dimensions
	useEffect(() => {
		const expectedWalls = setupPermanentWalls(state.width, state.height);
		if (JSON.stringify([...state.permanentWalls].sort()) !== JSON.stringify([...expectedWalls].sort())) {
			dispatch({type: 'SET_PERMANENT_WALLS', payload: expectedWalls});
		}
	}, [state.width, state.height, state.permanentWalls]);

	const statusText = `Поз: (${state.robotPos.x},${state.robotPos.y}) | ${state.width}x${state.height} | ${state.editMode ? 'Ред.' : 'Упр.'}`;

	return (
		<ThemeProvider theme={theme}>
			<div className="app-container">
				<CodeEditor
					code={state.code} setCode={code => dispatch({type: 'SET_CODE', payload: code})}
					isRunning={state.isRunning} onClearCode={handleClearCode} onStop={handleStop}
					onStart={handleStart} onReset={handleReset} statusText={statusText}
					speedLevel={animationSpeedLevel} onSpeedChange={setAnimationSpeedLevel}
				/>
				<ControlPanel
					/* Props */
					robotPos={state.robotPos} setRobotPos={pos => dispatch({type: 'SET_ROBOT_POS', payload: pos})}
					walls={state.walls} setWalls={payload => dispatch({type: 'SET_WALLS', payload})}
					permanentWalls={state.permanentWalls}
					markers={state.markers} setMarkers={payload => dispatch({type: 'SET_MARKERS', payload})}
					coloredCells={state.coloredCells}
					setColoredCells={payload => dispatch({type: 'SET_COLORED_CELLS', payload})}
					symbols={state.symbols}
					setSymbols={payload => dispatch({type: 'SET_SYMBOLS', payload})} // ControlPanel needs setSymbols
					width={state.width} setWidth={val => dispatch({type: 'SET_WIDTH', payload: val})}
					height={state.height} setHeight={val => dispatch({type: 'SET_HEIGHT', payload: val})}
					editMode={state.editMode} setEditMode={val => dispatch({type: 'SET_EDIT_MODE', payload: val})}
					setStatusMessage={msg => dispatch({type: 'SET_STATUS_MESSAGE', payload: msg})}
				/>
				<Field
					/* Props */
					canvasRef={canvasRef} robotPos={state.robotPos}
					walls={state.walls} permanentWalls={state.permanentWalls} markers={state.markers}
					coloredCells={state.coloredCells} symbols={state.symbols} // Pass symbols for drawing
					width={state.width} height={state.height} cellSize={state.cellSize}
					setRobotPos={pos => dispatch({type: 'SET_ROBOT_POS', payload: pos})}
					setWalls={payload => dispatch({type: 'SET_WALLS', payload})}
					setMarkers={payload => dispatch({type: 'SET_MARKERS', payload})}
					setColoredCells={payload => dispatch({type: 'SET_COLORED_CELLS', payload})}
					// No setSymbols needed for Field
					setCellSize={val => dispatch({type: 'SET_CELL_SIZE', payload: val})}
					editMode={state.editMode} statusMessage={state.statusMessage}
					setStatusMessage={msg => dispatch({type: 'SET_STATUS_MESSAGE', payload: msg})}
				/>
			</div>
		</ThemeProvider>
	);
});

export default RobotSimulator;