/**
 * @file RobotSimulator.jsx
 * @description Главный компонент симулятора робота. Данный компонент объединяет редактор кода, панель управления и поле,
 * на котором происходит визуализация робота. Он использует Material-UI тему и предоставляет подробные статусные сообщения,
 * а также выводит результаты работы сервера в консоль (на русском языке).
 */

import React, {memo, useCallback, useEffect, useReducer, useRef} from 'react';
import {ThemeProvider} from '@mui/material/styles';
import CodeEditor from './CodeEditor/CodeEditor';
import ControlPanel from './ControlPanel/ControlPanel';
import Field from './Field/Field';
import theme from '../styles/theme'; // Импорт темы Material-UI для стилизации компонентов
import {getHint} from './hints'; // Функция для получения подсказок по состоянию симулятора

/**
 * Начальное состояние симулятора.
 */
const initialState = {
	// Исходный код программы для робота с базовыми командами
	code: `использовать Робот\nалг\nнач\n  вправо\n  вниз\n  вправо\nкон`, // Флаг выполнения программы
	isRunning: false, // Текст статуса, полученный через подсказку
	statusMessage: getHint('initial'), // Вывод, полученный от сервера (например, результат выполнения кода)
	consoleOutput: "", // новое свойство для вывода сервера
	// Параметры поля: ширина, высота и размер клетки
	width: 7, height: 7, cellSize: 50, // Начальная позиция робота на поле
	robotPos: {x: 0, y: 0}, // Множество временных стен, которые могут изменяться
	walls: new Set(), // Множество постоянных стен (например, границы поля)
	permanentWalls: new Set(), // Объект для хранения маркеров на поле
	markers: {}, // Множество закрашенных клеток
	coloredCells: new Set(), // Флаг, определяющий, включен ли режим редактирования
	editMode: false,
};

/**
 * Редьюсер для управления состоянием симулятора робота.
 *
 * @param {Object} state - Текущее состояние симулятора.
 * @param {Object} action - Объект действия, содержащий тип и полезную нагрузку.
 * @returns {Object} Новое состояние после применения действия.
 */
function reducer(state, action) {
	switch (action.type) {
		// Обновление кода программы
		case 'SET_CODE':
			return {...state, code: action.payload};
		// Обновление состояния выполнения
		case 'SET_IS_RUNNING':
			return {...state, isRunning: action.payload};
		// Обновление статусного сообщения
		case 'SET_STATUS_MESSAGE':
			return {...state, statusMessage: action.payload};
		// Обновление вывода консоли
		case 'SET_CONSOLE_OUTPUT':
			return {...state, consoleOutput: action.payload};
		// Обновление позиции робота
		case 'SET_ROBOT_POS':
			return {...state, robotPos: action.payload};
		// Обновление ширины поля
		case 'SET_WIDTH':
			return {...state, width: action.payload};
		// Обновление высоты поля
		case 'SET_HEIGHT':
			return {...state, height: action.payload};
		// Обновление размера клетки
		case 'SET_CELL_SIZE':
			return {...state, cellSize: action.payload};
		// Обновление временных стен; поддерживает функцию-обновление или прямую установку
		case 'SET_WALLS':
			return {
				...state,
				walls: typeof action.payload === 'function' ? action.payload(state.walls) : new Set(action.payload),
			};
		// Обновление постоянных стен; поддерживает функцию-обновление или прямую установку
		case 'SET_PERMANENT_WALLS':
			return {
				...state,
				permanentWalls: typeof action.payload === 'function' ? action.payload(state.permanentWalls) : new Set(action.payload),
			};
		// Обновление маркеров на поле; поддерживает функцию-обновление или прямую установку
		case 'SET_MARKERS':
			return {
				...state,
				markers: typeof action.payload === 'function' ? action.payload(state.markers) : action.payload,
			};
		// Обновление закрашенных клеток; поддерживает функцию-обновление или прямую установку
		case 'SET_COLORED_CELLS':
			return {
				...state,
				coloredCells: typeof action.payload === 'function' ? action.payload(state.coloredCells) : new Set(action.payload),
			};
		// Обновление режима редактирования
		case 'SET_EDIT_MODE':
			return {...state, editMode: action.payload};
		// Если тип действия неизвестен, возвращается текущее состояние
		default:
			return state;
	}
}

/**
 * Функция для установки постоянных стен по периметру игрового поля.
 *
 * @param {number} width - Ширина игрового поля.
 * @param {number} height - Высота игрового поля.
 * @returns {Set} Множество строк, каждая из которых описывает стену в формате "x1,y1,x2,y2".
 */
function setupPermanentWalls(width, height) {
	const newWalls = new Set();
	// Установка горизонтальных стен вверху и внизу поля
	for (let x = 0; x < width; x++) {
		newWalls.add(`${x},0,${x + 1},0`); // верхняя граница
		newWalls.add(`${x},${height},${x + 1},${height}`); // нижняя граница
	}
	// Установка вертикальных стен слева и справа от поля
	for (let y = 0; y < height; y++) {
		newWalls.add(`0,${y},0,${y + 1}`); // левая граница
		newWalls.add(`${width},${y},${width},${y + 1}`); // правая граница
	}
	return newWalls;
}

/**
 * Функция для ограничения позиции робота так, чтобы он не выходил за пределы поля.
 *
 * @param {Object} robotPos - Текущая позиция робота с координатами {x, y}.
 * @param {number} width - Ширина поля.
 * @param {number} height - Высота поля.
 * @returns {Object} Новая позиция робота, ограниченная значениями от 0 до width - 1 (по x) и от 0 до height - 1 (по y).
 */
function clampRobotPos(robotPos, width, height) {
	const clampedX = Math.min(Math.max(robotPos.x, 0), width - 1);
	const clampedY = Math.min(Math.max(robotPos.y, 0), height - 1);
	return {x: clampedX, y: clampedY};
}

/**
 * Основной компонент симулятора робота.
 *
 * Использует React-хуки для управления состоянием и обработки действий пользователя,
 * а также объединяет подкомпоненты редактора кода, панели управления и игрового поля.
 *
 * @returns {JSX.Element} Элемент симулятора робота.
 */
const RobotSimulator = memo(() => {
	// Инициализация состояния через useReducer с начальным состоянием
	const [state, dispatch] = useReducer(reducer, initialState);
	// Создание ссылки на элемент canvas для дальнейшей работы
	const canvasRef = useRef(null);

	/**
	 * Функция-обработчик для очистки кода программы.
	 * Очищает редактор и устанавливает соответствующее статусное сообщение.
	 */
	const handleClearCode = useCallback(() => {
		dispatch({type: 'SET_CODE', payload: ''});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код программы очищен.'});
	}, []);

	/**
	 * Функция-обработчик для остановки выполнения программы.
	 * Устанавливает флаг выполнения в false и выводит сообщение об остановке.
	 */
	const handleStop = useCallback(() => {
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Выполнение остановлено.'});
	}, []);

	/**
	 * Функция-обработчик для запуска выполнения программы.
	 * Проверяет наличие кода, отправляет его на сервер для исполнения и обрабатывает ответ.
	 */
	const handleStart = useCallback(() => {
		// Проверка на пустой код
		if (!state.code.trim()) {
			dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Ошибка: программа пустая.'});
			return;
		}
		// Устанавливаем флаг выполнения в true
		dispatch({type: 'SET_IS_RUNNING', payload: true});

		// Отправляем код на сервер для исполнения через POST-запрос
		fetch('http://localhost:5000/execute', {
			method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({code: state.code})
		})
			.then(response => response.json())
			.then(data => {
				// Если сервер успешно выполнил код
				if (data.success) {
					dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код выполнен успешно.'});
					dispatch({type: 'SET_CONSOLE_OUTPUT', payload: data.output || ""});
					// Обновляем позицию робота и закрашенные клетки согласно ответу сервера
					dispatch({type: 'SET_ROBOT_POS', payload: data.robot});
					dispatch({type: 'SET_COLORED_CELLS', payload: new Set(data.coloredCells)});
				} else {
					// Если сервер вернул ошибку, отображаем сообщение об ошибке
					dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Ошибка: ' + data.message});
					dispatch({type: 'SET_CONSOLE_OUTPUT', payload: ""});
				}
				// Завершаем выполнение программы
				dispatch({type: 'SET_IS_RUNNING', payload: false});
			})
			.catch(error => {
				// Вывод ошибки в консоль на русском языке
				console.error('Ошибка выполнения запроса:', error);
				// Обработка ошибки запроса
				dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Ошибка выполнения запроса.'});
				dispatch({type: 'SET_CONSOLE_OUTPUT', payload: ""});
				dispatch({type: 'SET_IS_RUNNING', payload: false});
			});
	}, [state.code]);

	/**
	 * Функция-обработчик для сброса симулятора к исходным настройкам.
	 * Сбрасывает положение робота, стены, маркеры, размеры поля и код программы.
	 */
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
	 * Хук useEffect для обновления постоянных стен и корректировки позиции робота
	 * при изменении размеров поля.
	 */
	useEffect(() => {
		// Получение новых постоянных стен для текущих размеров поля
		const newWalls = setupPermanentWalls(state.width, state.height);
		dispatch({type: 'SET_PERMANENT_WALLS', payload: newWalls});
		// Ограничение позиции робота, чтобы она не выходила за границы поля
		const newPos = clampRobotPos(state.robotPos, state.width, state.height);
		dispatch({type: 'SET_ROBOT_POS', payload: newPos});
	}, [state.width, state.height]);

	// Формирование текстового сообщения со статусом симулятора для отображения в редакторе
	const statusText = [`Позиция робота: (${state.robotPos.x}, ${state.robotPos.y})`, `Маркеров: ${Object.keys(state.markers).length}`, `Раскрашенных клеток: ${state.coloredCells.size}`,].join('\n');

	return (<ThemeProvider theme={theme}>
			<div className="app-container">
				{/* Компонент редактора кода */}
				<CodeEditor
					code={state.code}
					// Обновление кода в состоянии
					setCode={(newCode) => dispatch({type: 'SET_CODE', payload: newCode})}
					isRunning={state.isRunning}
					onClearCode={handleClearCode}
					onStop={handleStop}
					onStart={handleStart}
					onReset={handleReset}
					statusText={statusText}
					// Передача вывода сервера для отображения в консоли редактора
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
					// Функция для установки статусного сообщения из панели управления
					setStatusMessage={(msg) => dispatch({type: 'SET_STATUS_MESSAGE', payload: msg})}
				/>

				{/* Компонент поля, на котором отображается робот */}
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
					// Позволяет обновлять статусное сообщение из компонента поля
					setStatusMessage={(msg) => dispatch({type: 'SET_STATUS_MESSAGE', payload: msg})}
				/>
			</div>
		</ThemeProvider>);
});

export default RobotSimulator;
