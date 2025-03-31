import React, {memo, useCallback, useEffect, useReducer, useRef, useState} from 'react';
import {ThemeProvider} from '@mui/material';
import CodeEditor from './CodeEditor/CodeEditor';
import ControlPanel from './ControlPanel/ControlPanel';
import Field from './Field/Field';
import theme from '../styles/theme';
import {getHint} from './hints';
import logger from '../Logger';
import io from 'socket.io-client';

const backendUrl = process.env.REACT_APP_BACKEND_URL || `http://${window.location.hostname}:5000`;

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
	symbols: {}, // { "x,y": { upper: 'A', lower: 'Б' } }
	// --- NEW State fields ---
	radiation: {}, // { "x,y": value }
	temperature: {}, // { "x,y": value }
	// ------------------------
	editMode: false,
};

// Helper Functions (clampRobotPos, setupPermanentWalls)
function setupPermanentWalls(width, height) { /* ... */
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

function clampRobotPos(robotPos, width, height) { /* ... */
	const cX = Math.min(Math.max(robotPos.x, 0), width - 1);
	const cY = Math.min(Math.max(robotPos.y, 0), height - 1);
	if (robotPos.x !== cX || robotPos.y !== cY) {
		return {x: cX, y: cY};
	}
	return robotPos;
}

// Reducer function
function reducer(state, action) {
	console.groupCollapsed(`%cReducer Action: ${action.type}`, 'color: red;'); /* ... logging ... */
	console.groupEnd();
	let nextState;
	switch (action.type) {
		/* ... other cases ... */
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
			nextState = {
				...state,
				symbols: typeof action.payload === 'function' ? action.payload(state.symbols) : action.payload
			};
			break;
		// --- NEW ACTIONS ---
		case 'SET_RADIATION':
			nextState = {
				...state,
				radiation: typeof action.payload === 'function' ? action.payload(state.radiation) : action.payload
			};
			break;
		case 'SET_TEMPERATURE':
			nextState = {
				...state,
				temperature: typeof action.payload === 'function' ? action.payload(state.temperature) : action.payload
			};
			break;
		// -------------------
		case 'SET_EDIT_MODE':
			nextState = {...state, editMode: action.payload};
			break;
		case 'RESET_STATE': {
			const rw = initialState.width;
			const rh = initialState.height;
			nextState = {
				...initialState, // Includes radiation:{}, temperature:{}
				width: rw,
				height: rh,
				permanentWalls: setupPermanentWalls(rw, rh),
				robotPos: clampRobotPos(initialState.robotPos, rw, rh),
				statusMessage: 'Сброшено.'
			};
			break;
		}
		default:
			throw new Error(`Unknown action type: ${action.type}`);
	}
	console.log('State After:', JSON.parse(JSON.stringify(nextState, (key, value) => value instanceof Set ? Array.from(value) : value)));
	console.groupEnd();
	return nextState;
}

// Component Definition
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

	const stateToLog = JSON.stringify(state, (k, v) => v instanceof Set ? [...v] : v, 2);
	console.log('%cRender State:', 'color: blue; bold;', JSON.parse(stateToLog));

	useEffect(() => { /* ... WebSocket setup ... */
		isMountedRef.current = true;
		socketRef.current = io('http://localhost:5000');
		socketRef.current.on('connection_ack', (d) => {
			if (isMountedRef.current) logger.log_event(`WS OK SID:${d.sid}`);
		});
		socketRef.current.on('execution_progress', (d) => {
			console.debug("WS Prog:", d);
			if (isMountedRef.current && state.isRunning && !animationControllerRef.current.isRunning) {
				const m = d.error ? `WS Ошибка ${d.commandIndex}-${d.error}` : `WS:${d.phase} ш.${d.commandIndex}`;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: m});
			}
		});
		return () => {
			isMountedRef.current = false;
			animationControllerRef.current.stop();
			if (socketRef.current) {
				socketRef.current.disconnect();
				logger.log_event('WS откл.');
			}
		};
	}, []);

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
		logger.log_event('Сброшено.');
		fetch('http://localhost:5000/reset', {
			method: 'POST',
			credentials: 'include'
		}).catch(e => logger.log_error(`/reset err:${e.message}`));
	}, []);

	// Animation function
	const animateTrace = useCallback(async (trace) => { /* ... as before ... */
		if (!trace?.length) {
			return {completed: true};
		}
		let c = true;
		const s = () => {
			c = false;
		};
		animationControllerRef.current = {stop: s, isRunning: true};
		const d = Math.max(50, 2000 - animationSpeedLevel * 480);
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация...'});
		console.groupCollapsed(`%cAnimation (Speed:${animationSpeedLevel},Delay:${d}ms)`, 'color:green');
		console.log("Trace:", trace);
		console.groupEnd();
		for (let i = 0; i < trace.length; i++) {
			const e = trace[i];
			console.debug(`%cAnim Step ${i + 1}/${trace.length}`, 'color:darkcyan', e);
			if (!isMountedRef.current || !c) {
				logger.log_event('Anim прервана.');
				animationControllerRef.current.isRunning = false;
				return {completed: false};
			}
			if (e.stateAfter) {
				console.debug("Apply state:", e.stateAfter);
				if (e.stateAfter.robot) dispatch({type: 'SET_ROBOT_POS', payload: e.stateAfter.robot});
				if (e.stateAfter.coloredCells) dispatch({
					type: 'SET_COLORED_CELLS',
					payload: new Set(e.stateAfter.coloredCells)
				});
				if (e.stateAfter.symbols !== undefined) dispatch({type: 'SET_SYMBOLS', payload: e.stateAfter.symbols});
				// --- NEW: Update radiation/temp if present in trace ---
				if (e.stateAfter.radiation !== undefined) dispatch({
					type: 'SET_RADIATION',
					payload: e.stateAfter.radiation
				});
				if (e.stateAfter.temperature !== undefined) dispatch({
					type: 'SET_TEMPERATURE',
					payload: e.stateAfter.temperature
				});
				// -------------------------------------------------------
				const msg = e.error ? `Ошибка:${e.error}(Шаг ${i + 1})` : `Шаг ${i + 1}/${trace.length}: ${e.command || ''}`;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: msg});
			} else {
				console.warn("Event stateAfter missing:", e);
			}
			if (animationSpeedLevel < 4 && d > 0) await new Promise(r => setTimeout(r, d));
			if (e.error) {
				logger.log_error(`Anim стоп(err ${i + 1}):${e.error}`);
				animationControllerRef.current.isRunning = false;
				return {completed: false, error: true};
			}
		}
		animationControllerRef.current.isRunning = false;
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация OK.'});
		console.log("%cAnim OK", 'color:green;bold;');
		return {completed: true};
	}, [animationSpeedLevel]);

	// Start execution handler
	const handleStart = useCallback(() => { /* ... */
		if (state.isRunning) {
			return;
		}
		if (!state.code.trim()) {
			dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код пуст.'});
			return;
		}
		dispatch({type: 'SET_IS_RUNNING', payload: true});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Выполнение...'});
		// Send current state, including new fields
		const currentFieldState = {
			width: state.width,
			height: state.height,
			robotPos: state.robotPos,
			walls: Array.from(state.walls),
			markers: state.markers,
			coloredCells: Array.from(state.coloredCells),
			symbols: state.symbols,
			radiation: state.radiation,
			temperature: state.temperature
		};
		console.log("%cPOST /execute state:", 'color:orange;', currentFieldState);
		fetch('http://localhost:5000/execute', {
			method: 'POST',
			credentials: 'include',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({code: state.code, fieldState: currentFieldState}),
		})
			.then(async (r) => {
				if (!r.ok) {
					let e = `HTTP ${r.status}`;
					try {
						const d = await r.json();
						e = d.message || e;
					} catch (_) {
					}
					throw new Error(e);
				}
				return r.json();
			})
			.then(async (data) => {
				console.log("%cGET /execute response:", 'color:purple;', data);
				if (!isMountedRef.current) return;
				let animRes = {completed: true};
				try {
					if (data.trace?.length) animRes = await animateTrace(data.trace);
				} catch (aE) {
					console.error("Anim err:", aE);
				}
				if (!isMountedRef.current) return;
				if (data.success) { // Success
					console.log("Apply final success state");
					dispatch({type: 'SET_ROBOT_POS', payload: data.robot});
					dispatch({type: 'SET_COLORED_CELLS', payload: new Set(data.coloredCells)});
					dispatch({type: 'SET_SYMBOLS', payload: data.symbols || {}});
					dispatch({type: 'SET_RADIATION', payload: data.radiation || {}}); // <-- Apply final radiation
					dispatch({type: 'SET_TEMPERATURE', payload: data.temperature || {}}); // <-- Apply final temperature
					if (animRes.completed) dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Успешно.'});
					logger.log_event('Успешно (бэк).');
				} else { // Error
					const eMsg = `Ошибка:${data.message || '?'} ${data.output || ''}`;
					console.log("Apply final error state");
					if (data.robot) dispatch({type: 'SET_ROBOT_POS', payload: data.robot});
					if (data.coloredCells) dispatch({type: 'SET_COLORED_CELLS', payload: new Set(data.coloredCells)});
					if (data.symbols) dispatch({type: 'SET_SYMBOLS', payload: data.symbols});
					if (data.radiation) dispatch({type: 'SET_RADIATION', payload: data.radiation}); // <-- Apply error radiation
					if (data.temperature) dispatch({type: 'SET_TEMPERATURE', payload: data.temperature}); // <-- Apply error temperature
					dispatch({type: 'SET_STATUS_MESSAGE', payload: eMsg});
					logger.log_error(`Ошибка бэка:${eMsg}`);
				}
				dispatch({type: 'SET_IS_RUNNING', payload: false});
			})
			.catch((error) => {
				if (!isMountedRef.current) return;
				console.error('Fetch /execute:', error);
				dispatch({type: 'SET_STATUS_MESSAGE', payload: `Сеть:${error.message}`});
				logger.log_error(`Fetch /execute:${error.message}`);
				dispatch({type: 'SET_IS_RUNNING', payload: false});
			});
	}, [state.isRunning, state.code, state.width, state.height, state.robotPos, state.walls, state.markers, state.coloredCells, state.symbols, state.radiation, state.temperature, animateTrace]); // Added radiation/temperature to deps

	// Effect to update field state on backend (debounced)
	useEffect(() => {
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
			}; // <-- Send new fields
			const stateToLog = JSON.stringify(fieldState, (k, v) => v instanceof Set ? [...v] : v, 2);
			console.log('%cPOST /updateField (debounced):', 'color:#f5a623;', JSON.parse(stateToLog));
			fetch(`${backendUrl}/updateField`, {
				method: 'POST',
				credentials: 'include',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify(fieldState),
			}).then(r => {
				if (isMountedRef.current && !r.ok) logger.log_warning(`Update field ${r.status}`);
			}).catch((e) => {
				if (isMountedRef.current) logger.log_error(`Update field fetch:${e.message}`);
			});
		}, 500);
		return () => clearTimeout(handler);
	}, [state.width, state.height, state.cellSize, state.robotPos, state.walls, state.markers, state.coloredCells, state.symbols, state.radiation, state.temperature]); // Added radiation/temperature to deps

	// Effect to update permanent walls
	useEffect(() => {
		const eW = setupPermanentWalls(state.width, state.height);
		if (JSON.stringify([...state.permanentWalls].sort()) !== JSON.stringify([...eW].sort())) {
			dispatch({type: 'SET_PERMANENT_WALLS', payload: eW});
		}
	}, [state.width, state.height, state.permanentWalls]);

	const statusText = `Поз: (${state.robotPos.x},${state.robotPos.y})|${state.width}x${state.height}|${state.editMode ? 'Ред' : 'Упр'}`;

	return (
		<ThemeProvider theme={theme}>
			<div className="app-container">
				<CodeEditor /* Props */ code={state.code} setCode={c => dispatch({type: 'SET_CODE', payload: c})}
				                        isRunning={state.isRunning} onClearCode={handleClearCode} onStop={handleStop}
				                        onStart={handleStart} onReset={handleReset} statusText={statusText}
				                        speedLevel={animationSpeedLevel} onSpeedChange={setAnimationSpeedLevel}/>
				<ControlPanel /* Props */
					robotPos={state.robotPos} setRobotPos={p => dispatch({type: 'SET_ROBOT_POS', payload: p})}
					walls={state.walls} setWalls={w => dispatch({type: 'SET_WALLS', payload: w})}
					permanentWalls={state.permanentWalls}
					markers={state.markers} setMarkers={m => dispatch({type: 'SET_MARKERS', payload: m})}
					coloredCells={state.coloredCells}
					setColoredCells={c => dispatch({type: 'SET_COLORED_CELLS', payload: c})}
					symbols={state.symbols} setSymbols={s => dispatch({type: 'SET_SYMBOLS', payload: s})}
					radiation={state.radiation}
					setRadiation={r => dispatch({type: 'SET_RADIATION', payload: r})} // <-- Pass rad state/setter
					temperature={state.temperature}
					setTemperature={t => dispatch({type: 'SET_TEMPERATURE', payload: t})} // <-- Pass temp state/setter
					width={state.width} setWidth={v => dispatch({type: 'SET_WIDTH', payload: v})}
					height={state.height} setHeight={v => dispatch({type: 'SET_HEIGHT', payload: v})}
					editMode={state.editMode} setEditMode={v => dispatch({type: 'SET_EDIT_MODE', payload: v})}
					setStatusMessage={m => dispatch({type: 'SET_STATUS_MESSAGE', payload: m})}/>
				<Field /* Props */
					canvasRef={canvasRef} robotPos={state.robotPos}
					setRobotPos={p => dispatch({type: 'SET_ROBOT_POS', payload: p})}
					walls={state.walls} setWalls={w => dispatch({type: 'SET_WALLS', payload: w})}
					permanentWalls={state.permanentWalls}
					markers={state.markers} setMarkers={m => dispatch({type: 'SET_MARKERS', payload: m})}
					coloredCells={state.coloredCells}
					setColoredCells={c => dispatch({type: 'SET_COLORED_CELLS', payload: c})}
					symbols={state.symbols} // Pass symbols for drawing
					// radiation={state.radiation} temperature={state.temperature} // Pass to Field if needed for drawing
					width={state.width} height={state.height} cellSize={state.cellSize}
					setCellSize={v => dispatch({type: 'SET_CELL_SIZE', payload: v})}
					editMode={state.editMode} statusMessage={state.statusMessage}
					setStatusMessage={m => dispatch({type: 'SET_STATUS_MESSAGE', payload: m})}
					// Field doesn't need setters for symbols, radiation, temperature
				/>
			</div>
		</ThemeProvider>
	);
});

export default RobotSimulator;