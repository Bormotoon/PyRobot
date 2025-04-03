// FILE START: RobotSimulator.jsx
import React, {memo, useCallback, useEffect, useReducer, useRef, useState} from 'react';
import {ThemeProvider} from '@mui/material';
import CodeEditor from './CodeEditor/CodeEditor';        // Уточните путь
import ControlPanel from './ControlPanel/ControlPanel';  // Уточните путь
import Field from './Field/Field';                    // Уточните путь
import theme from '../styles/theme';                    // Уточните путь
import {getHint} from './hints';                      // Уточните путь
import logger from '../Logger';                    // Уточните путь
import io from 'socket.io-client';

const backendUrl = process.env.REACT_APP_BACKEND_URL || `http://${window.location.hostname}:5000`;

const initialState = {
	code: `использовать Робот\nалг\nнач\n  вправо\n  вниз\n  вправо\nкон`,
	isRunning: false,
	isAwaitingInput: false,
	statusMessage: getHint('initial'),
	width: 7, height: 7, cellSize: 50,
	robotPos: {x: 0, y: 0},
	walls: new Set(), permanentWalls: new Set(), markers: {}, coloredCells: new Set(),
	symbols: {}, radiation: {}, temperature: {},
	editMode: false,
	inputRequestData: null,
};

// Вспомогательные функции setupPermanentWalls, clampRobotPos без изменений
function setupPermanentWalls(width, height) {
	const nw = new Set();
	for (let x = 0; x < width; x++) {
		nw.add(`${x},0,${x + 1},0`);
		nw.add(`${x},${height},${x + 1},${height}`);
	}
	for (let y = 0; y < height; y++) {
		nw.add(`0,${y},0,${y + 1}`);
		nw.add(`${width},${y},${width},${y + 1}`);
	}
	return nw;
}

function clampRobotPos(robotPos, width, height) {
	const currentX = robotPos?.x ?? 0;
	const currentY = robotPos?.y ?? 0;
	const clampedX = Math.min(Math.max(currentX, 0), width - 1);
	const clampedY = Math.min(Math.max(currentY, 0), height - 1);
	if (currentX !== clampedX || currentY !== clampedY) {
		return {x: clampedX, y: clampedY};
	}
	return robotPos;
}

// Редьюсер без изменений в логике, только добавлены новые actions
function reducer(state, action) {
	let nextState;
	switch (action.type) {
		case 'SET_CODE':
			nextState = {...state, code: action.payload};
			break;
		case 'SET_IS_RUNNING':
			nextState = {...state, isRunning: action.payload};
			break;
		case 'SET_IS_AWAITING_INPUT':
			nextState = {...state, isAwaitingInput: action.payload};
			if (!action.payload) {
				nextState.inputRequestData = null;
			}
			break;
		case 'SET_INPUT_REQUEST_DATA':
			nextState = {...state, inputRequestData: action.payload};
			break;
		case 'SET_STATUS_MESSAGE':
			nextState = {...state, statusMessage: action.payload};
			break;
		case 'SET_ROBOT_POS':
			nextState = {...state, robotPos: clampRobotPos(action.payload, state.width, state.height)};
			break;
		case 'SET_WIDTH': {
			const nw = Math.max(1, action.payload);
			const r = clampRobotPos(state.robotPos, nw, state.height);
			nextState = {...state, width: nw, robotPos: r, permanentWalls: setupPermanentWalls(nw, state.height)};
			break;
		}
		case 'SET_HEIGHT': {
			const nh = Math.max(1, action.payload);
			const r = clampRobotPos(state.robotPos, state.width, nh);
			nextState = {...state, height: nh, robotPos: r, permanentWalls: setupPermanentWalls(state.width, nh)};
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
				markers: typeof action.payload === 'function' ? action.payload(state.markers) : {...action.payload}
			};
			break;
		case 'SET_COLORED_CELLS':
			nextState = {
				...state,
				coloredCells: typeof action.payload === 'function' ? action.payload(state.coloredCells) : new Set(action.payload)
			};
			break;
		case 'SET_SYMBOLS':
			nextState = {
				...state,
				symbols: typeof action.payload === 'function' ? action.payload(state.symbols) : {...action.payload}
			};
			break;
		case 'SET_RADIATION':
			nextState = {
				...state,
				radiation: typeof action.payload === 'function' ? action.payload(state.radiation) : {...action.payload}
			};
			break;
		case 'SET_TEMPERATURE':
			nextState = {
				...state,
				temperature: typeof action.payload === 'function' ? action.payload(state.temperature) : {...action.payload}
			};
			break;
		case 'SET_EDIT_MODE':
			nextState = {...state, editMode: action.payload};
			break;
		case 'RESET_STATE': {
			const iw = initialState.width;
			const ih = initialState.height;
			nextState = {
				...initialState,
				width: iw,
				height: ih,
				permanentWalls: setupPermanentWalls(iw, ih),
				robotPos: clampRobotPos(initialState.robotPos, iw, ih),
				statusMessage: 'Симулятор сброшен.',
				isRunning: false,
				isAwaitingInput: false,
				inputRequestData: null
			};
			break;
		}
		default:
			logger.log_error(`Unknown reducer action type: ${action.type}`);
			throw new Error(`Unknown action type: ${action.type}`);
	}
	return nextState;
}


const RobotSimulator = memo(() => {
	const [state, dispatch] = useReducer(reducer, initialState, (init) => ({
		...init, permanentWalls: setupPermanentWalls(init.width, init.height)
	}));
	const [animationSpeedLevel, setAnimationSpeedLevel] = useState(2);
	const canvasRef = useRef(null);
	const socketRef = useRef(null);
	const isMountedRef = useRef(true);
	const animationControllerRef = useRef({
		stop: () => {
		}, isRunning: false
	});

	// WebSocket useEffect без изменений
	useEffect(() => {
		isMountedRef.current = true;
		logger.log_event('Connecting WebSocket...');
		const socket = io(backendUrl, {reconnectionAttempts: 5, timeout: 10000});
		socketRef.current = socket;
		socket.on('connect', () => {
			if (isMountedRef.current) logger.log_event(`WS Connected: ${socket.id}`);
		});
		socket.on('disconnect', (reason) => {
			if (isMountedRef.current) logger.log_warning(`WS Disconnected: ${reason}`);
		});
		socket.on('connect_error', (err) => {
			if (isMountedRef.current) logger.log_error(`WS Connect Error: ${err.message}`);
		});
		socket.on('connection_ack', (data) => {
			if (isMountedRef.current) logger.log_event(`WS Connection ACK SID:${data.sid}`);
		});
		socket.on('execution_progress', (data) => {
			if (isMountedRef.current && state.isRunning && !animationControllerRef.current.isRunning) {
				const msgPrefix = data.error ? `[Ошибка шаг ${data.commandIndex}]` : `[Шаг ${data.commandIndex}]`;
				const outputLines = data.output ? data.output.trim().split('\n') : [];
				const msgOutput = outputLines.length > 0 ? ` Вывод: ${outputLines.slice(-2).join(' \\n ')}` : '';
				const msgError = data.error ? ` ${data.error}` : '';
				dispatch({type: 'SET_STATUS_MESSAGE', payload: `${msgPrefix}${msgError}${msgOutput}`});
				if (data.robotPos) {
					dispatch({type: 'SET_ROBOT_POS', payload: data.robotPos});
				}
			}
		});
		return () => {
			isMountedRef.current = false;
			animationControllerRef.current.stop();
			if (socketRef.current) {
				logger.log_event('Disconnecting WebSocket...');
				socketRef.current.disconnect();
			}
		};
	}, [backendUrl]); // Убрали state.isRunning из зависимостей

	// Обработчики кнопок (handleClearCode, handleStop, handleReset) без изменений
	const handleClearCode = useCallback(() => {
		dispatch({type: 'SET_CODE', payload: `использовать Робот\nалг\nнач\n  \nкон`});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код очищен.'});
		logger.log_event('Code cleared by user.');
	}, []);
	const handleStop = useCallback(() => {
		animationControllerRef.current.stop();
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Выполнение остановлено.'});
		logger.log_event('Execution stopped by user.');
	}, []);
	const handleReset = useCallback(() => {
		animationControllerRef.current.stop();
		dispatch({type: 'RESET_STATE'});
		logger.log_event('Simulator state reset by user.');
		fetch(`${backendUrl}/reset`, {method: 'POST', credentials: 'include'}).then(res => {
			if (!res.ok) logger.log_warning(`/reset request failed with status ${res.status}`); else logger.log_event('/reset request successful.');
		}).catch(e => logger.log_error(`/reset fetch error: ${e.message}`));
	}, [backendUrl]);

	// Функция анимации animateTrace без изменений
	const animateTrace = useCallback(async (trace) => {
		if (!trace || !Array.isArray(trace) || trace.length === 0) {
			logger.log_event('Animation skipped: No trace data.');
			return {completed: true};
		}
		let continueAnimation = true;
		const stopAnimation = () => {
			logger.log_event('Animation stop requested.');
			continueAnimation = false;
		};
		animationControllerRef.current = {stop: stopAnimation, isRunning: true};
		const delay = [2000, 1000, 500, 250, 0][animationSpeedLevel];
		dispatch({type: 'SET_STATUS_MESSAGE', payload: `Анимация трассировки (шаг 1/${trace.length})...`});
		console.groupCollapsed(`%cAnimation (Speed Level: ${animationSpeedLevel}, Delay: ${delay}ms)`, 'color:green');
		console.log("Trace data:", trace);
		console.groupEnd();
		for (let i = 0; i < trace.length; i++) {
			const event = trace[i];
			if (!isMountedRef.current || !continueAnimation) {
				logger.log_event('Animation interrupted.');
				animationControllerRef.current.isRunning = false;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация прервана.'});
				return {completed: false};
			}
			if (event.stateAfter) {
				if (event.stateAfter.robot) dispatch({type: 'SET_ROBOT_POS', payload: event.stateAfter.robot});
				if (event.stateAfter.coloredCells) dispatch({
					type: 'SET_COLORED_CELLS',
					payload: new Set(event.stateAfter.coloredCells)
				});
				if (event.stateAfter.symbols !== undefined) dispatch({
					type: 'SET_SYMBOLS',
					payload: event.stateAfter.symbols || {}
				});
				if (event.stateAfter.walls) dispatch({type: 'SET_WALLS', payload: new Set(event.stateAfter.walls)});
				if (event.stateAfter.markers) dispatch({type: 'SET_MARKERS', payload: event.stateAfter.markers || {}});
				if (event.stateAfter.radiation !== undefined) dispatch({
					type: 'SET_RADIATION',
					payload: event.stateAfter.radiation || {}
				});
				if (event.stateAfter.temperature !== undefined) dispatch({
					type: 'SET_TEMPERATURE',
					payload: event.stateAfter.temperature || {}
				});
				const commandText = event.command ? `: ${event.command}` : '';
				const message = event.error ? `Ошибка на шаге ${event.commandIndex + 1}${commandText}: ${event.error}` : `Шаг ${event.commandIndex + 1}/${trace.length}${commandText}`;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: message});
			} else {
				console.warn("Trace event missing stateAfter:", event);
				dispatch({
					type: 'SET_STATUS_MESSAGE',
					payload: `Шаг ${event.commandIndex + 1}: Ошибка - нет данных о состоянии`
				});
			}
			if (delay > 0) {
				await new Promise(resolve => setTimeout(resolve, delay));
			}
			if (event.error) {
				logger.log_error(`Animation stopped due to error at step ${event.commandIndex + 1}: ${event.error}`);
				animationControllerRef.current.isRunning = false;
				return {completed: false, error: true};
			}
		}
		animationControllerRef.current.isRunning = false;
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация трассировки завершена.'});
		console.log("%cAnimation completed successfully", 'color:green;bold;');
		return {completed: true};
	}, [animationSpeedLevel]);

	// Обработчик handleStart без изменений в логике, но использует полные пропсы
	const handleStart = useCallback(() => {
		if (state.isRunning || state.isAwaitingInput) {
			logger.log_warning(`Start prevented: isRunning=${state.isRunning}, isAwaitingInput=${state.isAwaitingInput}`);
			dispatch({
				type: 'SET_STATUS_MESSAGE',
				payload: state.isAwaitingInput ? 'Ожидание ввода...' : 'Выполнение уже идет...'
			});
			return;
		}
		if (!state.code.trim()) {
			dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код для выполнения пуст.'});
			return;
		}
		dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false});
		dispatch({type: 'SET_INPUT_REQUEST_DATA', payload: null});
		dispatch({type: 'SET_IS_RUNNING', payload: true});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Запрос на выполнение...'});
		logger.log_event('Requesting code execution...');
		const currentFieldState = {
			width: state.width,
			height: state.height,
			cellSize: state.cellSize,
			robotPos: state.robotPos,
			walls: Array.from(state.walls),
			markers: state.markers,
			coloredCells: Array.from(state.coloredCells),
			symbols: state.symbols,
			radiation: state.radiation,
			temperature: state.temperature
		};
		fetch(`${backendUrl}/execute`, {
			method: 'POST',
			credentials: 'include',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({code: state.code, fieldState: currentFieldState}),
		})
			.then(async (response) => {
				if (!response.ok) {
					let errorMsg = `HTTP ${response.status} ${response.statusText}`;
					try {
						const errorData = await response.json();
						errorMsg = errorData.message || errorMsg;
					} catch (_) {
					}
					throw new Error(errorMsg);
				}
				return response.json();
			})
			.then(async (data) => {
				if (!isMountedRef.current) return;
				if (data.input_required) {
					logger.log_event(`Input required for variable: ${data.var_name}`);
					dispatch({type: 'SET_IS_RUNNING', payload: false});
					dispatch({type: 'SET_IS_AWAITING_INPUT', payload: true});
					dispatch({
						type: 'SET_INPUT_REQUEST_DATA',
						payload: {var_name: data.var_name, prompt: data.prompt, target_type: data.target_type}
					});
					dispatch({
						type: 'SET_STATUS_MESSAGE',
						payload: data.message || `Требуется ввод для ${data.var_name}...`
					});
					const userInput = window.prompt(data.prompt || `Введите значение для ${data.var_name} (тип ${data.target_type || 'неизв.'}):`);
					if (!isMountedRef.current) return;
					if (userInput === null) {
						dispatch({
							type: 'SET_STATUS_MESSAGE',
							payload: 'Ввод отменен. Запустите код снова, если нужно.'
						});
						dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false});
						logger.log_warning('User cancelled the input prompt.');
					} else {
						dispatch({
							type: 'SET_STATUS_MESSAGE',
							payload: `Значение '${userInput}' для '${data.var_name}' принято. Для продолжения запустите код снова.`
						});
						dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false});
						logger.log_event(`User provided input '${userInput}' for ${data.var_name}. Manual re-run required.`);
					}
					if (data.finalState) {
						if (data.finalState.robot) dispatch({type: 'SET_ROBOT_POS', payload: data.finalState.robot});
						if (data.finalState.coloredCells) dispatch({
							type: 'SET_COLORED_CELLS',
							payload: new Set(data.finalState.coloredCells)
						});
						if (data.finalState.symbols !== undefined) dispatch({
							type: 'SET_SYMBOLS',
							payload: data.finalState.symbols || {}
						});
						if (data.finalState.radiation !== undefined) dispatch({
							type: 'SET_RADIATION',
							payload: data.finalState.radiation || {}
						});
						if (data.finalState.temperature !== undefined) dispatch({
							type: 'SET_TEMPERATURE',
							payload: data.finalState.temperature || {}
						});
						if (data.finalState.walls) dispatch({
							type: 'SET_WALLS',
							payload: new Set(data.finalState.walls)
						});
						if (data.finalState.markers) dispatch({
							type: 'SET_MARKERS',
							payload: data.finalState.markers || {}
						});
					}
					return;
				}
				let animationResult = {completed: true};
				try {
					if (data.trace?.length > 0) {
						dispatch({type: 'SET_IS_RUNNING', payload: true});
						animationResult = await animateTrace(data.trace);
						if (animationControllerRef.current.isRunning === false) {
							dispatch({type: 'SET_IS_RUNNING', payload: false});
						}
					} else {
						dispatch({type: 'SET_IS_RUNNING', payload: false});
						dispatch({
							type: 'SET_STATUS_MESSAGE',
							payload: data.message || (data.success ? 'Выполнено (нет шагов).' : 'Ошибка (нет шагов).')
						});
					}
				} catch (animError) {
					console.error("Animation error:", animError);
					logger.log_error(`Animation failed: ${animError.message}`);
					dispatch({type: 'SET_STATUS_MESSAGE', payload: `Ошибка анимации: ${animError.message}`});
					dispatch({type: 'SET_IS_RUNNING', payload: false});
				}
				if (!isMountedRef.current) return;
				if (data.finalState) {
					logger.log_event("Applying final state from server response.");
					if (data.finalState.robot) dispatch({type: 'SET_ROBOT_POS', payload: data.finalState.robot});
					if (data.finalState.coloredCells) dispatch({
						type: 'SET_COLORED_CELLS',
						payload: new Set(data.finalState.coloredCells)
					});
					if (data.finalState.symbols !== undefined) dispatch({
						type: 'SET_SYMBOLS',
						payload: data.finalState.symbols || {}
					});
					if (data.finalState.radiation !== undefined) dispatch({
						type: 'SET_RADIATION',
						payload: data.finalState.radiation || {}
					});
					if (data.finalState.temperature !== undefined) dispatch({
						type: 'SET_TEMPERATURE',
						payload: data.finalState.temperature || {}
					});
					if (data.finalState.walls) dispatch({type: 'SET_WALLS', payload: new Set(data.finalState.walls)});
					if (data.finalState.markers) dispatch({
						type: 'SET_MARKERS',
						payload: data.finalState.markers || {}
					});
					if (animationControllerRef.current.isRunning === false) {
						const finalMessage = data.message || (data.success ? 'Выполнение успешно завершено.' : 'Выполнение завершено с ошибкой.');
						const finalOutput = data.finalState.output ? `\nВывод:\n${data.finalState.output.trim()}` : "";
						dispatch({type: 'SET_STATUS_MESSAGE', payload: `${finalMessage}${finalOutput}`});
					}
				} else {
					logger.log_warning("No finalState received from server in successful/error response.");
					if (animationControllerRef.current.isRunning === false) {
						dispatch({
							type: 'SET_STATUS_MESSAGE',
							payload: data.message || 'Нет финального состояния от сервера.'
						});
					}
				}
				if (data.success) {
					logger.log_event('Execution successful (server).');
				} else {
					logger.log_error(`Execution failed (server): ${data.message || '?'}`);
				}
				if (animationControllerRef.current.isRunning === false) {
					dispatch({type: 'SET_IS_RUNNING', payload: false});
				}
			})
			.catch((error) => {
				if (!isMountedRef.current) return;
				console.error('Error during fetch /execute:', error);
				const errorText = error.message || 'Неизвестная сетевая ошибка';
				dispatch({type: 'SET_STATUS_MESSAGE', payload: `Ошибка сети: ${errorText}`});
				logger.log_error(`Fetch /execute failed: ${errorText}`);
				dispatch({type: 'SET_IS_RUNNING', payload: false});
				dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false});
			});
	}, [state.isRunning, state.isAwaitingInput, state.code, state.width, state.height, state.robotPos, state.walls, state.markers, state.coloredCells, state.symbols, state.radiation, state.temperature, animateTrace, backendUrl]);

	// useEffect для обновления состояния поля на бэкенде (debounced) без изменений
	useEffect(() => {
		const debounceTimeout = 500;
		const handler = setTimeout(() => {
			if (!isMountedRef.current) return;
			const fieldState = {
				width: state.width,
				height: state.height,
				cellSize: state.cellSize,
				robotPos: state.robotPos,
				walls: Array.from(state.walls),
				markers: state.markers,
				coloredCells: Array.from(state.coloredCells),
				symbols: state.symbols,
				radiation: state.radiation,
				temperature: state.temperature
			};
			fetch(`${backendUrl}/updateField`, {
				method: 'POST',
				credentials: 'include',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify(fieldState),
			}).then(response => {
				if (isMountedRef.current && !response.ok) {
					logger.log_warning(`/updateField responded with status ${response.status}`);
				}
			}).catch((error) => {
				if (isMountedRef.current) {
					logger.log_error(`/updateField fetch error: ${error.message}`);
				}
			});
		}, debounceTimeout);
		return () => clearTimeout(handler);
	}, [state.width, state.height, state.cellSize, state.robotPos, state.walls, state.markers, state.coloredCells, state.symbols, state.radiation, state.temperature, backendUrl]);

	// useEffect для обновления постоянных стен без изменений
	useEffect(() => {
		const expectedPermanentWalls = setupPermanentWalls(state.width, state.height);
		if (JSON.stringify([...state.permanentWalls].sort()) !== JSON.stringify([...expectedPermanentWalls].sort())) {
			dispatch({type: 'SET_PERMANENT_WALLS', payload: expectedPermanentWalls});
			logger.log_event(`Permanent walls updated for size ${state.width}x${state.height}`);
		}
	}, [state.width, state.height, state.permanentWalls]);

	const statusText = `Поз: (${state.robotPos?.x ?? '?'},${state.robotPos?.y ?? '?'}) | ${state.width}x${state.height} | ${state.editMode ? 'Ред.' : 'Упр.'}`;

	return (
		<ThemeProvider theme={theme}>
			<div className="app-container">
				<CodeEditor
					code={state.code}
					setCode={c => dispatch({type: 'SET_CODE', payload: c})}
					isRunning={state.isRunning || state.isAwaitingInput}
					onClearCode={handleClearCode}
					onStop={handleStop}
					onStart={handleStart}
					onReset={handleReset}
					statusText={statusText}
					speedLevel={animationSpeedLevel}
					onSpeedChange={setAnimationSpeedLevel}
				/>
				<ControlPanel
					robotPos={state.robotPos} setRobotPos={p => dispatch({type: 'SET_ROBOT_POS', payload: p})}
					walls={state.walls} setWalls={w => dispatch({type: 'SET_WALLS', payload: w})}
					permanentWalls={state.permanentWalls}
					markers={state.markers} setMarkers={m => dispatch({type: 'SET_MARKERS', payload: m})}
					coloredCells={state.coloredCells}
					setColoredCells={c => dispatch({type: 'SET_COLORED_CELLS', payload: c})}
					symbols={state.symbols} setSymbols={s => dispatch({type: 'SET_SYMBOLS', payload: s})}
					radiation={state.radiation} setRadiation={r => dispatch({type: 'SET_RADIATION', payload: r})}
					temperature={state.temperature}
					setTemperature={t => dispatch({type: 'SET_TEMPERATURE', payload: t})}
					width={state.width} setWidth={v => dispatch({type: 'SET_WIDTH', payload: v})}
					height={state.height} setHeight={v => dispatch({type: 'SET_HEIGHT', payload: v})}
					editMode={state.editMode} setEditMode={v => dispatch({type: 'SET_EDIT_MODE', payload: v})}
					setStatusMessage={m => dispatch({type: 'SET_STATUS_MESSAGE', payload: m})}
				/>
				<Field
					canvasRef={canvasRef}
					robotPos={state.robotPos}
					walls={state.walls}
					permanentWalls={state.permanentWalls}
					markers={state.markers}
					coloredCells={state.coloredCells}
					symbols={state.symbols}
					width={state.width}
					height={state.height}
					cellSize={state.cellSize}
					editMode={state.editMode}
					statusMessage={state.statusMessage}
					setRobotPos={p => dispatch({type: 'SET_ROBOT_POS', payload: p})}
					setWalls={w => dispatch({type: 'SET_WALLS', payload: w})}
					setMarkers={m => dispatch({type: 'SET_MARKERS', payload: m})}
					setColoredCells={c => dispatch({type: 'SET_COLORED_CELLS', payload: c})}
					setCellSize={v => dispatch({type: 'SET_CELL_SIZE', payload: v})}
					setStatusMessage={m => dispatch({type: 'SET_STATUS_MESSAGE', payload: m})}
				/>
			</div>
		</ThemeProvider>
	);
});

export default RobotSimulator;
// FILE END: RobotSimulator.jsx