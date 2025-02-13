/**
 * @file RobotSimulator.jsx
 * @description Главный компонент симулятора робота. Этот компонент объединяет редактор кода, панель управления и игровое поле.
 * Компонент использует Material‑UI тему, отображает подробные статусные сообщения и выводит результаты работы сервера в консоль.
 * В режиме редактирования изменения поля (размер, стены, маркеры, окрашенные клетки) не отправляются на сервер в реальном времени.
 * При отключении режима редактирования (переход editMode с true на false) текущее состояние поля передаётся на сервер.
 */

import React, {memo, useCallback, useEffect, useReducer, useRef} from 'react';
import {ThemeProvider} from '@mui/material/styles';
import CodeEditor from './CodeEditor/CodeEditor';
import ControlPanel from './ControlPanel/ControlPanel';
import Field from './Field/Field';
import theme from '../styles/theme';
import {getHint} from './hints';

/**
 * Начальное состояние симулятора.
 */
const initialState = {
	// Исходный код программы для робота
	code: `использовать Робот\nалг\nнач\n  вправо\n  вниз\n  вправо\nкон`, // Флаг выполнения программы
	isRunning: false, // Текст статусного сообщения
	statusMessage: getHint('initial'), // Вывод от сервера (например, результат выполнения кода)
	consoleOutput: "", // Параметры поля: ширина, высота и размер клетки
	width: 7, height: 7, cellSize: 50, // Начальная позиция робота на поле
	robotPos: {x: 0, y: 0}, // Множество временных стен (редактируемых)
	walls: new Set(), // Множество постоянных стен (например, границы поля)
	permanentWalls: new Set(), // Объект для хранения маркеров на поле
	markers: {}, // Множество закрашенных клеток
	coloredCells: new Set(), // Флаг, определяющий, включён ли режим редактирования
	editMode: false,
};

/**
 * Редьюсер для управления состоянием симулятора.
 *
 * @param {Object} state - Текущее состояние симулятора.
 * @param {Object} action - Объект действия с типом и полезной нагрузкой.
 * @returns {Object} Новое состояние после применения действия.
 */
function reducer(state, action) {
	switch (action.type) {
		case 'SET_CODE':
			return {...state, code: action.payload};
		case 'SET_IS_RUNNING':
			return {...state, isRunning: action.payload};
		case 'SET_STATUS_MESSAGE':
			return {...state, statusMessage: action.payload};
		case 'SET_CONSOLE_OUTPUT':
			return {...state, consoleOutput: action.payload};
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

/**
 * Функция для установки постоянных стен по периметру игрового поля.
 *
 * @param {number} width - Ширина поля.
 * @param {number} height - Высота поля.
 * @returns {Set} Множество строк, описывающих стены в формате "x1,y1,x2,y2".
 */
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

/**
 * Функция для ограничения позиции робота так, чтобы он не выходил за пределы поля.
 *
 * @param {Object} robotPos - Текущая позиция робота {x, y}.
 * @param {number} width - Ширина поля.
 * @param {number} height - Высота поля.
 * @returns {Object} Новая позиция, ограниченная значениями от 0 до width - 1 и от 0 до height - 1.
 */
function clampRobotPos(robotPos, width, height) {
	const clampedX = Math.min(Math.max(robotPos.x, 0), width - 1);
	const clampedY = Math.min(Math.max(robotPos.y, 0), height - 1);
	return {x: clampedX, y: clampedY};
}

/**
 * Основной компонент симулятора робота.
 *
 * Объединяет подкомпоненты редактора кода, панели управления и игрового поля.
 * В режиме редактирования изменения поля не отправляются на сервер в реальном времени.
 * После отключения режима редактирования (переход editMode с true на false) текущее состояние поля передаётся на сервер.
 * При изменении размеров поля позиция робота корректируется так, чтобы он оставался внутри внешних стен.
 *
 * @returns {JSX.Element} Элемент симулятора робота.
 */
const RobotSimulator = memo(() => {
	const [state, dispatch] = useReducer(reducer, initialState);
	const canvasRef = useRef(null);

	// Реф для отслеживания предыдущего значения editMode
	const prevEditMode = useRef(state.editMode);

	const handleClearCode = useCallback(() => {
		dispatch({type: 'SET_CODE', payload: ''});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код программы очищен.'});
	}, []);

	const handleStop = useCallback(() => {
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Выполнение остановлено.'});
	}, []);

	const handleStart = useCallback(() => {
		if (!state.code.trim()) {
			dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Ошибка: программа пустая.'});
			return;
		}
		dispatch({type: 'SET_IS_RUNNING', payload: true});
		fetch('http://localhost:5000/execute', {
			method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({code: state.code}),
		})
			.then(response => response.json())
			.then(data => {
				if (data.success) {
					dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код выполнен успешно.'});
					dispatch({type: 'SET_CONSOLE_OUTPUT', payload: data.output || ""});
					// Если режим редактирования выключен, обновляем позицию робота с ответа сервера.
					if (!state.editMode) {
						dispatch({type: 'SET_ROBOT_POS', payload: data.robot});
					}
					dispatch({type: 'SET_COLORED_CELLS', payload: new Set(data.coloredCells)});
				} else {
					dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Ошибка: ' + data.message});
					dispatch({type: 'SET_CONSOLE_OUTPUT', payload: ""});
				}
				dispatch({type: 'SET_IS_RUNNING', payload: false});
			})
			.catch(error => {
				console.error('Ошибка выполнения запроса:', error);
				dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Ошибка выполнения запроса.'});
				dispatch({type: 'SET_CONSOLE_OUTPUT', payload: ""});
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
		dispatch({
			type: 'SET_CODE', payload: `использовать Робот\nалг\nнач\n  # Ваши команды здесь\nкон`,
		});
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Симулятор сброшен (демо).'});
		dispatch({type: 'SET_CONSOLE_OUTPUT', payload: ""});
	}, []);

	/**
	 * useEffect для обновления постоянных стен и корректировки позиции робота при изменении размеров поля.
	 * При каждом изменении ширины или высоты поля позиция робота корректируется так, чтобы он оставался внутри.
	 */
	useEffect(() => {
		const newWalls = setupPermanentWalls(state.width, state.height);
		dispatch({type: 'SET_PERMANENT_WALLS', payload: newWalls});
		const newPos = clampRobotPos(state.robotPos, state.width, state.height);
		if (newPos.x !== state.robotPos.x || newPos.y !== state.robotPos.y) {
			dispatch({type: 'SET_ROBOT_POS', payload: newPos});
		}
	}, [state.width, state.height]);

	/**
	 * useEffect для отправки текущего состояния поля на сервер после отключения режима редактирования.
	 * Отслеживает изменение state.editMode: если предыдущим значением было true, а текущим false,
	 * отправляет обновленное состояние поля на сервер через эндпоинт /updateField.
	 */
	useEffect(() => {
		if (prevEditMode.current && !state.editMode) {
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
				method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(fieldState),
			}).catch(e => console.error("Ошибка обновления поля на сервере:", e));
		}
		prevEditMode.current = state.editMode;
	}, [state.editMode, state.width, state.height, state.cellSize, state.robotPos, state.walls, state.permanentWalls, state.markers, state.coloredCells]);

	const statusText = [`Позиция робота: (${state.robotPos.x}, ${state.robotPos.y})`, `Маркеров: ${Object.keys(state.markers).length}`, `Раскрашенных клеток: ${state.coloredCells.size}`,].join('\n');

	return (<ThemeProvider theme={theme}>
			<div className="app-container">
				{/* Компонент редактора кода */}
				<CodeEditor
					code={state.code}
					setCode={(newCode) => dispatch({type: 'SET_CODE', payload: newCode})}
					isRunning={state.isRunning}
					onClearCode={handleClearCode}
					onStop={handleStop}
					onStart={handleStart}
					onReset={handleReset}
					statusText={statusText}
					consoleOutput={state.consoleOutput}
				/>

				{/* Панель управления симулятором */}
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

				{/* Компонент поля, где отображается робот */}
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
			</div>
		</ThemeProvider>);
});

export default RobotSimulator;
