import React, {memo, useCallback, useEffect, useReducer, useRef, useState} from 'react';
import {ThemeProvider} from '@mui/material';
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

// Helper Functions (clampRobotPos, setupPermanentWalls) should be placed here
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


function reducer(state, action) {
	switch (action.type) {
		case 'SET_CODE':
			return {...state, code: action.payload};
		case 'SET_IS_RUNNING':
			return {...state, isRunning: action.payload};
		case 'SET_STATUS_MESSAGE':
			return {...state, statusMessage: action.payload};
		case 'SET_ROBOT_POS':
			// Clamp position whenever it's set via reducer to be safe
			const clampedPos = clampRobotPos(action.payload, state.width, state.height);
			return {...state, robotPos: clampedPos};
		case 'SET_WIDTH':
			const newWidth = Math.max(1, action.payload); // Ensure width is at least 1
			// Ensure robot stays within bounds after width change
			const robotAfterWidthChange = clampRobotPos(state.robotPos, newWidth, state.height);
			return {
				...state,
				width: newWidth,
				robotPos: robotAfterWidthChange, // Update robot pos immediately
				permanentWalls: setupPermanentWalls(newWidth, state.height) // Update walls immediately
			};
		case 'SET_HEIGHT':
			const newHeight = Math.max(1, action.payload); // Ensure height is at least 1
			// Ensure robot stays within bounds after height change
			const robotAfterHeightChange = clampRobotPos(state.robotPos, state.width, newHeight);
			return {
				...state,
				height: newHeight,
				robotPos: robotAfterHeightChange, // Update robot pos immediately
				permanentWalls: setupPermanentWalls(state.width, newHeight) // Update walls immediately
			};
		case 'SET_CELL_SIZE':
			return {...state, cellSize: Math.max(10, action.payload)}; // Ensure minimum cell size
		case 'SET_WALLS':
			return {
				...state,
				walls: typeof action.payload === 'function' ? action.payload(state.walls) : new Set(action.payload),
			};
		case 'SET_PERMANENT_WALLS':
			// Should generally not be set directly, derived from width/height
			return {...state, permanentWalls: new Set(action.payload)};
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
		case 'RESET_STATE':
			// Reset to initial state values, recompute permanent walls
			const resetWidth = initialState.width;
			const resetHeight = initialState.height;
			return {
				...initialState,
				width: resetWidth,
				height: resetHeight,
				permanentWalls: setupPermanentWalls(resetWidth, resetHeight),
				robotPos: clampRobotPos(initialState.robotPos, resetWidth, resetHeight), // Ensure clamped initial pos
				statusMessage: 'Симулятор сброшен в начальное состояние.',
			};
		default:
			throw new Error(`Unknown action type: ${action.type}`);
	}
}

// Component Definition
const RobotSimulator = memo(() => {
	const [state, dispatch] = useReducer(reducer, initialState, (init) => ({
		...init,
		permanentWalls: setupPermanentWalls(init.width, init.height)
	}));

	// Separate state for animation speed, not part of main reducer state
	const [animationSpeedLevel, setAnimationSpeedLevel] = useState(2);
	const canvasRef = useRef(null);
	const socketRef = useRef(null);
	const isMountedRef = useRef(true);
	// Use a ref to track if an animation is currently supposed to be running
	const animationControllerRef = useRef({
		stop: () => {
		}
	});


	useEffect(() => {
		isMountedRef.current = true;
		socketRef.current = io('http://localhost:5000');

		// Connection acknowledgment handler (useful for debugging)
		socketRef.current.on('connection_ack', (data) => {
			if (isMountedRef.current) {
				logger.log_event(`WebSocket подключен успешно. SID: ${data.sid}`);
				// You could potentially store the SID from here if session method fails,
				// but it requires backend changes to use it.
			}
		});

		socketRef.current.on('execution_progress', (data) => {
			// IMPORTANT: This progress update is primarily for displaying live info,
			// *not* for driving the animation itself, as message delivery is not guaranteed timely or ordered.
			// The main animation relies on the trace received via HTTP.
			if (isMountedRef.current && state.isRunning) {
				// Update status message with progress *if* animation isn't providing it
				if (animationControllerRef.current.isRunning) {
					return;
				} // Let animation update status
				const progressMsg = data.error
					? `Прогресс: Ошибка на шаге ${data.commandIndex} (${data.phase}) - ${data.error}`
					: `Прогресс: Фаза ${data.phase}, Команда ${data.commandIndex}`;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: progressMsg});
				logger.log_event(`Прогресс WebSocket: ${progressMsg}`);
			}
		});

		return () => {
			isMountedRef.current = false;
			animationControllerRef.current.stop(); // Signal any ongoing animation to stop
			if (socketRef.current) {
				socketRef.current.disconnect();
				logger.log_event('WebSocket отключен при размонтировании.');
			}
		};
	}, [state.isRunning]); // Re-run if isRunning changes? Maybe not needed, connect once.

	// Clear code handler
	const handleClearCode = useCallback(() => {
		dispatch({type: 'SET_CODE', payload: `использовать Робот\nалг\nнач\n  \nкон`});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код программы очищен.'});
		logger.log_event('Код программы очищен.');
	}, []);

	// Stop handler
	const handleStop = useCallback(() => {
		animationControllerRef.current.stop(); // Tell animation to stop
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Выполнение остановлено пользователем.'});
		logger.log_event('Выполнение остановлено пользователем.');
		// Consider backend interruption if needed
	}, []);

	// Animation function
	const animateTrace = useCallback(async (trace) => {
		// Return early if trace is empty
		if (!trace || trace.length === 0) {
			return {completed: true}; // Nothing to animate
		}

		let shouldContinue = true;
		const stopAnimation = () => {
			shouldContinue = false;
		};
		animationControllerRef.current = {stop: stopAnimation, isRunning: true}; // Expose stop function

		const delayForLevel = (level) => Math.max(50, 2000 - level * 480); // Min 50ms delay
		const stepDelay = delayForLevel(animationSpeedLevel);

		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация выполнения...'});

		for (let i = 0; i < trace.length; i++) {
			const event = trace[i];

			if (!isMountedRef.current || !shouldContinue) {
				logger.log_event('Анимация прервана (компонент/остановка).');
				animationControllerRef.current.isRunning = false;
				return {completed: false}; // Indicate interruption
			}

			// Apply state changes from the 'stateAfter' of the event
			if (event.stateAfter) {
				if (event.stateAfter.robot) {
					dispatch({type: 'SET_ROBOT_POS', payload: event.stateAfter.robot});
				}
				if (event.stateAfter.coloredCells) {
					dispatch({type: 'SET_COLORED_CELLS', payload: new Set(event.stateAfter.coloredCells)});
				}
				// Update status based on command or error
				const message = event.error
					? `Ошибка: ${event.error} (Команда: ${event.command || 'N/A'})`
					: `Выполняется: ${event.command || 'шаг'} (${i + 1}/${trace.length})`;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: message});
			} else {
				// Should not happen if trace generation is correct, but handle defensively
				dispatch({type: 'SET_STATUS_MESSAGE', payload: `Обработка шага ${i + 1}/${trace.length}...`});
			}


			// Introduce delay if not max speed and delay > 0
			if (animationSpeedLevel < 4 && stepDelay > 0) {
				await new Promise(resolve => setTimeout(resolve, stepDelay));
			}

			// If an error occurred in this step, stop the animation AFTER showing the error state
			if (event.error) {
				logger.log_error(`Анимация остановлена из-за ошибки: ${event.error}`);
				// Status message already set above
				animationControllerRef.current.isRunning = false;
				return {completed: false, error: true}; // Indicate error stop
			}
		}

		// Animation completed normally
		animationControllerRef.current.isRunning = false;
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация завершена.'});
		return {completed: true}; // Indicate normal completion
	}, [animationSpeedLevel]); // Dependency: speed level

	// Start execution handler
	const handleStart = useCallback(() => {
		if (state.isRunning) { // Prevent double clicks
			logger.log_warning("Попытка запуска во время выполнения.");
			return;
		}
		if (!state.code.trim()) {
			dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Ошибка: программа пустая.'});
			logger.log_error('Попытка запуска пустой программы.');
			return;
		}

		dispatch({type: 'SET_IS_RUNNING', payload: true});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Запрос выполнения...'});

		// Send current field state from React state
		const currentFieldState = {
			width: state.width, height: state.height,
			robotPos: state.robotPos,
			walls: Array.from(state.walls),
			markers: state.markers,
			coloredCells: Array.from(state.coloredCells),
		};

		fetch('http://localhost:5000/execute', {
			method: 'POST',
			credentials: 'include',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({code: state.code, fieldState: currentFieldState}),
		})
			.then(async (response) => { // Mark as async to use await inside
				if (!response.ok) {
					let errorMsg = `HTTP ошибка ${response.status}`;
					try {
						const errorData = await response.json();
						errorMsg = errorData.message || errorMsg;
					} catch (e) { /* ignore */
					}
					throw new Error(errorMsg);
				}
				return response.json();
			})
			.then(async (data) => { // Mark as async
				if (!isMountedRef.current) return; // Check if still mounted

				// --- Central Change Here ---
				let animationResult = {completed: true}; // Assume completion if no trace
				try {
					if (data.trace && data.trace.length > 0) {
						animationResult = await animateTrace(data.trace); // Wait for animation attempt
					} else {
						logger.log_event("Нет данных трассировки для анимации.");
					}
				} catch (animError) {
					console.error("Ошибка во время анимации:", animError);
					logger.log_error(`Ошибка JS во время анимации: ${animError}`);
					// Decide how to proceed, maybe just log and continue to final state update
				}

				// --- Update FINAL state AFTER animation attempt ---
				// Check mount status again after await
				if (!isMountedRef.current) return;

				// If animation was stopped manually, don't apply backend's final state?
				// Let's apply it for now, assuming backend result is canonical.
				// if (!animationResult.completed && !animationResult.error) {
				//     // Manual stop, keep UI state as is?
				//     dispatch({ type: 'SET_IS_RUNNING', payload: false });
				//     return;
				// }

				if (data.success) {
					// Success: Set final state from backend data
					dispatch({type: 'SET_ROBOT_POS', payload: data.robot});
					dispatch({type: 'SET_COLORED_CELLS', payload: new Set(data.coloredCells)});
					// Set status only if animation didn't end with error message
					if (animationResult.completed) {
						dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код выполнен успешно.'});
					}
					logger.log_event('Код выполнен успешно (согласно бэкенду).');
				} else {
					// Error during execution on backend: Set state to where error occurred
					const errorMsg = `Ошибка бэкенда: ${data.message || 'Неизвестная ошибка'}` + (data.output ? `\nВывод: ${data.output}` : "");
					// Apply the state reported by the backend (which should be state *at the point of error*)
					if (data.robot) dispatch({type: 'SET_ROBOT_POS', payload: data.robot});
					if (data.coloredCells) dispatch({type: 'SET_COLORED_CELLS', payload: new Set(data.coloredCells)});
					// Set error status (animation might have already set a similar message)
					dispatch({type: 'SET_STATUS_MESSAGE', payload: errorMsg});
					logger.log_error(`Ошибка бэкенда: ${errorMsg}`);
				}

				// Ensure running state is set to false after everything
				dispatch({type: 'SET_IS_RUNNING', payload: false});
				// --- End Central Change ---
			})
			.catch((error) => {
				if (!isMountedRef.current) return;
				console.error('Ошибка fetch запроса /execute:', error);
				const errorPayload = `Ошибка сети или сервера: ${error.message}`;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: errorPayload});
				logger.log_error(`Ошибка fetch /execute: ${error.message}`);
				dispatch({type: 'SET_IS_RUNNING', payload: false});
			});
	}, [state.isRunning, state.code, state.width, state.height, state.robotPos, state.walls, state.markers, state.coloredCells, animateTrace]); // Dependencies for start handler

	// Reset handler
	const handleReset = useCallback(() => {
		animationControllerRef.current.stop(); // Stop any animation
		dispatch({type: 'RESET_STATE'}); // Use simple reset action
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		logger.log_event('Симулятор сброшен в начальное состояние.');
		fetch('http://localhost:5000/reset', {method: 'POST', credentials: 'include'})
			.catch(e => logger.log_error(`Ошибка сброса на сервере: ${e.message}`));
	}, []);

	// Effect to update field state on backend (debounced)
	useEffect(() => {
		const handler = setTimeout(() => {
			if (!isMountedRef.current) return;

			const fieldState = {
				width: state.width, height: state.height, cellSize: state.cellSize,
				robotPos: state.robotPos, walls: Array.from(state.walls),
				markers: state.markers, coloredCells: Array.from(state.coloredCells),
			};
			fetch('http://localhost:5000/updateField', {
				method: 'POST', credentials: 'include',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify(fieldState),
			})
				.then(response => {
					if (isMountedRef.current && !response.ok) {
						logger.log_warning(`Ошибка обновления поля на сервере: ${response.status}`);
					}
				})
				.catch((e) => {
					if (isMountedRef.current) {
						logger.log_error(`Ошибка сети при обновлении поля: ${e.message}`);
					}
				});
		}, 300); // Debounce

		return () => clearTimeout(handler);
	}, [
		state.width, state.height, state.cellSize, state.robotPos,
		state.walls, state.markers, state.coloredCells, // Exclude permanentWalls
	]);

	// Effect to ensure permanent walls match dimensions (simpler than in reducer)
	useEffect(() => {
		const expectedWalls = setupPermanentWalls(state.width, state.height);
		// Quick check if they are different (Set comparison is tricky, stringify is simple)
		if (JSON.stringify(Array.from(state.permanentWalls).sort()) !== JSON.stringify(Array.from(expectedWalls).sort())) {
			dispatch({type: 'SET_PERMANENT_WALLS', payload: expectedWalls});
		}
	}, [state.width, state.height]); // Only depends on dimensions


	// Status text displayed in CodeEditor
	const statusText = `Позиция: (${state.robotPos.x}, ${state.robotPos.y}) | Размер: ${state.width}x${state.height} | Режим: ${state.editMode ? 'Редакт.' : 'Управл.'}`;

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
					speedLevel={animationSpeedLevel}
					onSpeedChange={setAnimationSpeedLevel}
				/>
				<ControlPanel
					robotPos={state.robotPos}
					setRobotPos={(pos) => dispatch({type: 'SET_ROBOT_POS', payload: pos})}
					walls={state.walls}
					setWalls={(payload) => dispatch({type: 'SET_WALLS', payload: payload})}
					permanentWalls={state.permanentWalls}
					markers={state.markers}
					setMarkers={(payload) => dispatch({type: 'SET_MARKERS', payload: payload})}
					coloredCells={state.coloredCells}
					setColoredCells={(payload) => dispatch({type: 'SET_COLORED_CELLS', payload: payload})}
					width={state.width}
					setWidth={(val) => dispatch({type: 'SET_WIDTH', payload: val})}
					height={state.height}
					setHeight={(val) => dispatch({type: 'SET_HEIGHT', payload: val})}
					editMode={state.editMode}
					setEditMode={(val) => dispatch({type: 'SET_EDIT_MODE', payload: val})}
					setStatusMessage={(msg) => dispatch({type: 'SET_STATUS_MESSAGE', payload: msg})}
				/>
				<Field
					canvasRef={canvasRef}
					robotPos={state.robotPos}
					setRobotPos={(pos) => dispatch({type: 'SET_ROBOT_POS', payload: pos})}
					walls={state.walls}
					setWalls={(payload) => dispatch({type: 'SET_WALLS', payload: payload})}
					permanentWalls={state.permanentWalls}
					markers={state.markers}
					setMarkers={(payload) => dispatch({type: 'SET_MARKERS', payload: payload})}
					coloredCells={state.coloredCells}
					setColoredCells={(payload) => dispatch({type: 'SET_COLORED_CELLS', payload: payload})}
					width={state.width}
					height={state.height}
					cellSize={state.cellSize}
					setCellSize={(val) => dispatch({type: 'SET_CELL_SIZE', payload: val})}
					editMode={state.editMode}
					statusMessage={state.statusMessage}
					setStatusMessage={(msg) => dispatch({type: 'SET_STATUS_MESSAGE', payload: msg})}
				/>
			</div>
		</ThemeProvider>
	);
});

export default RobotSimulator;