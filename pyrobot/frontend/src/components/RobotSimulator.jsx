// FILE START: RobotSimulator.jsx

/**
 * @file RobotSimulator.jsx
 * @description Корневой компонент симулятора робота.
 * Управляет общим состоянием приложения (код, состояние поля, статус выполнения),
 * обрабатывает взаимодействие пользователя с компонентами CodeEditor, ControlPanel, Field,
 * взаимодействует с бэкендом для выполнения кода и обновления состояния,
 * а также управляет анимацией трассировки выполнения.
 */

import React, {memo, useCallback, useEffect, useReducer, useRef, useState} from 'react';
// Импорт дочерних компонентов
import CodeEditor from './CodeEditor/CodeEditor';        // Редактор кода
import ControlPanel from './ControlPanel/ControlPanel';  // Панель управления
import Field from './Field/Field';                    // Игровое поле
// Импорт стилей и утилит
import {getHint} from './hints';                      // Функция для получения подсказок
import logger from '../Logger';                       // Логгер фронтенда (путь исправлен)
// Импорт клиента Socket.IO
import io from 'socket.io-client';

// URL бэкенда, берется из переменных окружения или по умолчанию
const backendUrl = process.env.REACT_APP_BACKEND_URL || `http://${window.location.hostname}:5000`;

/**
 * @typedef {object} RobotPosition
 * @property {number} x - Координата X робота (0-based).
 * @property {number} y - Координата Y робота (0-based).
 */

/**
 * @typedef {object} InputRequestData
 * @property {string} var_name - Имя переменной, для которой требуется ввод.
 * @property {string} prompt - Текст подсказки для пользователя.
 * @property {string} target_type - Ожидаемый тип данных ('цел', 'вещ', 'лог', 'лит', 'сим').
 */

/**
 * @typedef {object} AppState
 * @property {string} code - Текущий код в редакторе.
 * @property {boolean} isRunning - Флаг: идет ли выполнение кода или анимация.
 * @property {boolean} isAwaitingInput - Флаг: ожидается ли ввод от пользователя (из-за команды 'ввод').
 * @property {string} statusMessage - Текущее сообщение для пользователя в строке статуса.
 * @property {number} width - Ширина поля в клетках.
 * @property {number} height - Высота поля в клетках.
 * @property {number} cellSize - Размер клетки в пикселях для отрисовки.
 * @property {RobotPosition} robotPos - Текущая позиция робота.
 * @property {Set<string>} walls - Набор пользовательских стен (ключ: "x1,y1,x2,y2").
 * @property {Set<string>} permanentWalls - Набор стен-границ поля (ключ: "x1,y1,x2,y2").
 * @property {object.<string, number>} markers - Маркеры на поле (ключ: "x,y", значение: 1).
 * @property {Set<string>} coloredCells - Набор закрашенных клеток (ключ: "x,y").
 * @property {object.<string, {upper?: string, lower?: string}>} symbols - Символы в клетках (ключ: "x,y").
 * @property {object.<string, number>} radiation - Уровни радиации (ключ: "x,y", значение: число).
 * @property {object.<string, number>} temperature - Уровни температуры (ключ: "x,y", значение: число).
 * @property {boolean} editMode - Флаг: включен ли режим редактирования поля.
 * @property {InputRequestData | null} inputRequestData - Данные для активного запроса ввода (или null).
 */

/**
 * Начальное состояние приложения.
 * @type {AppState}
 */
const initialState = {
	code: `использовать Робот\nалг\nнач\n  вправо\n  вниз\n  вправо\nкон`, // Пример кода по умолчанию
	isRunning: false,           // Изначально ничего не выполняется
	isAwaitingInput: false,     // Изначально ввод не ожидается
	statusMessage: getHint('initial'), // Начальная подсказка
	width: 7,                   // Ширина поля по умолчанию
	height: 7,                  // Высота поля по умолчанию
	cellSize: 50,               // Размер клетки по умолчанию
	robotPos: {x: 0, y: 0},   // Начальная позиция робота
	walls: new Set(),           // Пользовательских стен нет
	permanentWalls: new Set(),  // Границы поля будут вычислены при инициализации
	markers: {},                // Маркеров нет
	coloredCells: new Set(),    // Закрашенных клеток нет
	symbols: {},                // Символов нет
	radiation: {},              // Радиации нет
	temperature: {},            // Температуры нет
	robotErrorDirection: null,  // Направление ошибки движения робота (для визуализации)
	editMode: false,            // Режим редактирования выключен
	inputRequestData: null,     // Нет активного запроса ввода
};

/**
 * Генерирует набор строк, представляющих внешние границы поля.
 * @param {number} width - Ширина поля.
 * @param {number} height - Высота поля.
 * @returns {Set<string>} Набор строк-ключей для граничных стен.
 */
function setupPermanentWalls(width, height) {
	const nw = new Set();
	// Горизонтальные границы (верхняя и нижняя)
	for (let x = 0; x < width; x++) {
		nw.add(`${x},0,${x + 1},0`);         // Верхняя линия клетки (x,0)
		nw.add(`${x},${height},${x + 1},${height}`); // Нижняя линия клетки (x, height-1)
	}
	// Вертикальные границы (левая и правая)
	for (let y = 0; y < height; y++) {
		nw.add(`0,${y},0,${y + 1}`);         // Левая линия клетки (0,y)
		nw.add(`${width},${y},${width},${y + 1}`); // Правая линия клетки (width-1, y)
	}
	return nw;
}

/**
 * Ограничивает позицию робота границами поля [0..width-1, 0..height-1].
 * @param {RobotPosition | null | undefined} robotPos - Текущая или предполагаемая позиция робота.
 * @param {number} width - Ширина поля.
 * @param {number} height - Высота поля.
 * @returns {RobotPosition} Скорректированная позиция робота.
 */
function clampRobotPos(robotPos, width, height) {
	const currentX = robotPos?.x ?? 0; // Используем 0, если позиция не определена
	const currentY = robotPos?.y ?? 0;
	// Применяем Math.min и Math.max для ограничения координат
	const clampedX = Math.min(Math.max(currentX, 0), width - 1);
	const clampedY = Math.min(Math.max(currentY, 0), height - 1);
	// Возвращаем новый объект только если позиция действительно изменилась
	if (currentX !== clampedX || currentY !== clampedY) {
		return {x: clampedX, y: clampedY};
	}
	// Иначе возвращаем исходный объект для оптимизации ререндера
	return robotPos;
}

/**
 * Редьюсер для управления состоянием симулятора.
 * Обрабатывает действия (actions) и возвращает новое состояние.
 * Обеспечивает иммутабельность состояния.
 * @param {AppState} state - Текущее состояние.
 * @param {object} action - Действие для изменения состояния.
 * @param {string} action.type - Тип действия (e.g., 'SET_CODE', 'SET_ROBOT_POS').
 * @param {*} action.payload - Данные, связанные с действием.
 * @returns {AppState} Новое состояние.
 */
function reducer(state, action) {
	let nextState; // Переменная для нового состояния

	switch (action.type) {
		case 'SET_CODE': // Изменение кода в редакторе
			nextState = {...state, code: action.payload};
			break;
		case 'SET_IS_RUNNING': // Установка/снятие флага выполнения
			nextState = {...state, isRunning: action.payload};
			break;
		case 'SET_IS_AWAITING_INPUT': // Установка/снятие флага ожидания ввода
			nextState = {...state, isAwaitingInput: action.payload};
			// Если перестали ждать ввода, очищаем данные запроса
			if (!action.payload) {
				nextState.inputRequestData = null;
			}
			break;
		case 'SET_INPUT_REQUEST_DATA': // Сохранение информации о запросе ввода
			nextState = {...state, inputRequestData: action.payload};
			break;
		case 'SET_STATUS_MESSAGE': // Установка нового сообщения в строке статуса
			nextState = {...state, statusMessage: action.payload};
			break;
		case 'SET_ROBOT_POS': // Установка новой позиции робота (с проверкой границ)
			nextState = {...state, robotPos: clampRobotPos(action.payload, state.width, state.height)};
			break;
		case 'SET_WIDTH': { // Изменение ширины поля
			const newWidth = Math.max(1, action.payload); // Минимальная ширина 1
			// Корректируем позицию робота и границы поля
			const newRobotPos = clampRobotPos(state.robotPos, newWidth, state.height);
			nextState = {
				...state,
				width: newWidth,
				robotPos: newRobotPos,
				permanentWalls: setupPermanentWalls(newWidth, state.height)
			};
			break;
		}
		case 'SET_HEIGHT': { // Изменение высоты поля
			const newHeight = Math.max(1, action.payload); // Минимальная высота 1
			const newRobotPos = clampRobotPos(state.robotPos, state.width, newHeight);
			nextState = {
				...state,
				height: newHeight,
				robotPos: newRobotPos,
				permanentWalls: setupPermanentWalls(state.width, newHeight)
			};
			break;
		}
		case 'SET_CELL_SIZE': // Изменение размера клетки
			nextState = {...state, cellSize: Math.max(10, action.payload)}; // Минимальный размер 10
			break;
		case 'SET_WALLS': // Обновление набора пользовательских стен
			// Поддерживает передачу функции обновления или нового Set/массива
			nextState = {
				...state,
				walls: typeof action.payload === 'function' ? action.payload(state.walls) : new Set(action.payload)
			};
			break;
		case 'SET_PERMANENT_WALLS': // Установка граничных стен (обычно при изменении размера)
			nextState = {...state, permanentWalls: new Set(action.payload)};
			break;
		case 'SET_MARKERS': // Обновление объекта маркеров
			// Поддерживает передачу функции обновления или нового объекта
			nextState = {
				...state,
				markers: typeof action.payload === 'function' ? action.payload(state.markers) : {...action.payload}
			};
			break;
		case 'SET_COLORED_CELLS': // Обновление набора закрашенных клеток
			nextState = {
				...state,
				coloredCells: typeof action.payload === 'function' ? action.payload(state.coloredCells) : new Set(action.payload)
			};
			break;
		case 'SET_SYMBOLS': // Обновление объекта символов
			nextState = {
				...state,
				symbols: typeof action.payload === 'function' ? action.payload(state.symbols) : {...action.payload}
			};
			break;
		case 'SET_RADIATION': // Обновление объекта радиации
			nextState = {
				...state,
				radiation: typeof action.payload === 'function' ? action.payload(state.radiation) : {...action.payload}
			};
			break;
		case 'SET_TEMPERATURE': // Обновление объекта температуры
			nextState = {
				...state,
				temperature: typeof action.payload === 'function' ? action.payload(state.temperature) : {...action.payload}
			};
			break;
		case 'SET_ROBOT_ERROR_DIRECTION': // Установка направления ошибки движения робота
			nextState = {...state, robotErrorDirection: action.payload};
			break;
		case 'SET_EDIT_MODE': // Переключение режима редактирования
			nextState = {...state, editMode: action.payload};
			break;
		case 'RESET_STATE': { // Сброс всего состояния к начальному
			const initialWidth = initialState.width;
			const initialHeight = initialState.height;
			nextState = {
				...initialState, // Копируем все начальные значения
				width: initialWidth,
				height: initialHeight,
				permanentWalls: setupPermanentWalls(initialWidth, initialHeight), // Пересчитываем границы
				robotPos: clampRobotPos(initialState.robotPos, initialWidth, initialHeight), // Проверяем позицию
				statusMessage: getHint('reset'), // Сообщение о сбросе
				isRunning: false, // Сбрасываем флаги
				isAwaitingInput: false,
				inputRequestData: null,
				robotErrorDirection: null, // Очищаем ошибку движения
			};
			break;
		}
		default: // Обработка неизвестного типа действия
			logger.log_error(`Unknown reducer action type: ${action.type}`);
			throw new Error(`Unknown action type: ${action.type}`);
	}
	return nextState; // Возвращаем обновленное состояние
}


/**
 * Основной компонент симулятора.
 * Оборачивает все дочерние компоненты и управляет их взаимодействием и состоянием.
 */
const RobotSimulator = memo(() => {
	// Инициализация состояния с помощью useReducer и функции инициализатора для permanentWalls
	const [state, dispatch] = useReducer(reducer, initialState, (init) => ({
		...init,
		permanentWalls: setupPermanentWalls(init.width, init.height)
	}));

	// Состояние для скорости анимации (управляется слайдером в CodeEditor)
	const [animationSpeedLevel, setAnimationSpeedLevel] = useState(2); // 0=медленно, 4=мгновенно

	// Рефы для доступа к DOM-элементам и управления асинхронными процессами
	const canvasRef = useRef(null);      // Реф на основной canvas поля
	const socketRef = useRef(null);      // Реф на объект WebSocket соединения
	const isMountedRef = useRef(true);   // Флаг для проверки, смонтирован ли компонент (для асинхронных операций)
	const animationControllerRef = useRef({
		stop: () => {
		}, isRunning: false
	}); // Объект для управления анимацией

	/**
	 * useEffect для установки и управления WebSocket соединением.
	 * Выполняется один раз при монтировании компонента.
	 */
	useEffect(() => {
		isMountedRef.current = true; // Компонент смонтирован
		logger.log_event('Connecting WebSocket...');
		// Устанавливаем соединение с сервером Socket.IO
		const socket = io(backendUrl, {
			reconnectionAttempts: 5, // Попытки переподключения
			timeout: 10000,          // Таймаут подключения
		});
		socketRef.current = socket; // Сохраняем сокет в реф

		// Обработчики событий сокета
		socket.on('connect', () => {
			// Логируем успешное подключение
			if (isMountedRef.current) logger.log_event(`WS Connected: ${socket.id}`);
		});
		socket.on('disconnect', (reason) => {
			// Логируем отключение
			if (isMountedRef.current) logger.log_warning(`WS Disconnected: ${reason}`);
		});
		socket.on('connect_error', (err) => {
			// Логируем ошибку подключения
			if (isMountedRef.current) logger.log_error(`WS Connect Error: ${err.message}`);
		});
		socket.on('connection_ack', (data) => {
			// Получаем подтверждение сессии от сервера
			if (isMountedRef.current) logger.log_event(`WS Connection ACK SID:${data.sid}`);
		});
		socket.on('execution_progress', (data) => {
			// Получаем сообщения о прогрессе выполнения кода на бэкенде
			// Обновляем статус и позицию робота в UI, только если сейчас НЕ идет анимация трассировки
			// (чтобы избежать конфликтов обновления состояния)
			if (isMountedRef.current && state.isRunning && !animationControllerRef.current.isRunning) {
				const msgPrefix = data.error ? `[Ошибка шаг ${data.commandIndex}]` : `[Шаг ${data.commandIndex}]`;
				const outputLines = data.output ? data.output.trim().split('\n') : [];
				const msgOutput = outputLines.length > 0 ? ` Вывод: ${outputLines.slice(-2).join(' \\n ')}` : ''; // Показываем последние 2 строки вывода
				const msgError = data.error ? ` ${data.error}` : '';
				// Обновляем сообщение для пользователя
				dispatch({type: 'SET_STATUS_MESSAGE', payload: `${msgPrefix}${msgError}${msgOutput}`});
				// Обновляем позицию робота, если она пришла
				if (data.robotPos) {
					dispatch({type: 'SET_ROBOT_POS', payload: data.robotPos});
				}
			}
		});

		// Функция очистки при размонтировании компонента
		return () => {
			isMountedRef.current = false; // Компонент размонтирован
			animationControllerRef.current.stop(); // Останавливаем текущую анимацию, если она есть
			if (socketRef.current) {
				logger.log_event('Disconnecting WebSocket...');
				socketRef.current.disconnect(); // Закрываем соединение
			}
		};
		// Зависимость только от URL бэкенда, чтобы эффект выполнился один раз
	}, [state.isRunning]);

	/**
	 * useCallback для обработчика очистки кода.
	 * Мемоизируется, т.к. не зависит от изменяемых переменных.
	 */
	const handleClearCode = useCallback(() => {
		dispatch({type: 'SET_CODE', payload: `использовать Робот\nалг\nнач\n  \nкон`});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: getHint('codeCleared')});
		logger.log_event('Code cleared by user.');
	}, [/* Нет зависимостей */]);

	/**
	 * useCallback для обработчика остановки выполнения/анимации.
	 * Мемоизируется, т.к. не зависит от изменяемых переменных.
	 */
	const handleStop = useCallback(() => {
		animationControllerRef.current.stop(); // Вызываем метод stop у контроллера анимации
		dispatch({type: 'SET_IS_RUNNING', payload: false}); // Снимаем флаг выполнения
		dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false}); // Сбрасываем флаг ожидания ввода
		dispatch({type: 'SET_STATUS_MESSAGE', payload: getHint('executionStoppedByUser')});
		logger.log_event('Execution stopped by user.');
	}, [/* Нет зависимостей */]);

	/**
	 * useCallback для обработчика сброса состояния симулятора.
	 * Использует константное значение backendUrl, поэтому не требует зависимостей.
	 */
	const handleReset = useCallback(() => {
		animationControllerRef.current.stop(); // Останавливаем анимацию
		dispatch({type: 'RESET_STATE'});     // Сбрасываем состояние на фронтенде
		logger.log_event('Simulator state reset by user.');
		// Отправляем запрос на сброс состояния сессии на бэкенде
		fetch(`${backendUrl}/reset`, {method: 'POST', credentials: 'include'})
			.then(res => {
				if (!res.ok) logger.log_warning(`/reset request failed with status ${res.status}`); else logger.log_event('/reset request successful.');
			})
			.catch(e => logger.log_error(`/reset fetch error: ${e.message}`));
	}, []); // Пустой массив зависимостей, так как используются только константы

	/**
	 * useCallback для асинхронной функции анимации трассировки выполнения.
	 * @param {Array<object>} trace - Массив шагов трассировки от бэкенда.
	 * @returns {Promise<{completed: boolean, error?: boolean}>} Промис, который разрешается объектом с результатом анимации.
	 */
	const animateTrace = useCallback(async (trace) => {
		// Проверка наличия данных трассировки
		if (!trace || !Array.isArray(trace) || trace.length === 0) {
			logger.log_event('Animation skipped: No trace data.');
			return {completed: true}; // Считаем завершенной
		}

		let continueAnimation = true; // Флаг для возможности прерывания анимации
		// Функция для прерывания цикла анимации
		const stopAnimation = () => {
			logger.log_event('Animation stop requested.');
			continueAnimation = false;
		};
		// Сохраняем контроллер для возможности остановки извне
		animationControllerRef.current = {stop: stopAnimation, isRunning: true};

		// Определяем задержку между шагами на основе уровня скорости
		const delay = [2000, 1000, 500, 250, 0][animationSpeedLevel]; // мс
		dispatch({type: 'SET_STATUS_MESSAGE', payload: `Анимация трассировки (шаг 1/${trace.length})...`});
		console.groupCollapsed(`%cAnimation (Speed Level: ${animationSpeedLevel}, Delay: ${delay}ms)`, 'color:green');
		console.log("Trace data:", trace);
		console.groupEnd();

		// Асинхронный цикл по шагам трассировки
		for (let i = 0; i < trace.length; i++) {
			const event = trace[i]; // Текущий шаг

			// Проверяем, нужно ли продолжать и смонтирован ли компонент
			if (!isMountedRef.current || !continueAnimation) {
				logger.log_event('Animation interrupted.');
				animationControllerRef.current.isRunning = false; // Снимаем флаг анимации
				dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация прервана.'});
				return {completed: false}; // Возвращаем результат: не завершено
			}

			// Применяем состояние ПОСЛЕ выполнения команды из текущего шага
			if (event.stateAfter) {
				// Обновляем позицию робота, если она есть
				if (event.stateAfter.robot) dispatch({type: 'SET_ROBOT_POS', payload: event.stateAfter.robot});
				// Обновляем закрашенные клетки
				if (event.stateAfter.coloredCells) dispatch({
					type: 'SET_COLORED_CELLS',
					payload: new Set(event.stateAfter.coloredCells)
				});
				// Обновляем символы
				if (event.stateAfter.symbols !== undefined) dispatch({
					type: 'SET_SYMBOLS',
					payload: event.stateAfter.symbols || {}
				});
				// Обновляем стены
				if (event.stateAfter.walls) dispatch({type: 'SET_WALLS', payload: new Set(event.stateAfter.walls)});
				// Обновляем маркеры
				if (event.stateAfter.markers) dispatch({type: 'SET_MARKERS', payload: event.stateAfter.markers || {}});
				// Обновляем радиацию
				if (event.stateAfter.radiation !== undefined) dispatch({
					type: 'SET_RADIATION',
					payload: event.stateAfter.radiation || {}
				});
				// Обновляем температуру
				if (event.stateAfter.temperature !== undefined) dispatch({
					type: 'SET_TEMPERATURE',
					payload: event.stateAfter.temperature || {}
				});
				// Обновляем направление ошибки движения робота
				if (event.stateAfter.robotErrorDirection !== undefined) dispatch({
					type: 'SET_ROBOT_ERROR_DIRECTION',
					payload: event.stateAfter.robotErrorDirection
				});

				// Формируем и устанавливаем сообщение о текущем шаге
				const commandText = event.command ? `: ${event.command}` : '';
				const message = event.error
					? `Ошибка на шаге ${event.commandIndex + 1}${commandText}: ${event.error}`
					: `Шаг ${event.commandIndex + 1}/${trace.length}${commandText}`;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: message});
			} else {
				// Если в шаге трассировки нет stateAfter (не должно быть)
				console.warn("Trace event missing stateAfter:", event);
				dispatch({
					type: 'SET_STATUS_MESSAGE',
					payload: `Шаг ${event.commandIndex + 1}: Ошибка - нет данных о состоянии`
				});
			}

			// Применяем задержку (если скорость не мгновенная)
			if (delay > 0) {
				await new Promise(resolve => setTimeout(resolve, delay));
			}

			// Если на этом шаге была ошибка, прерываем анимацию
			if (event.error) {
				logger.log_error(`Animation stopped due to error at step ${event.commandIndex + 1}: ${event.error}`);
				animationControllerRef.current.isRunning = false; // Снимаем флаг анимации
				// Сообщение об ошибке уже должно быть установлено
				return {completed: false, error: true}; // Возвращаем результат: не завершено, была ошибка
			}
		}

		// Анимация успешно завершена
		animationControllerRef.current.isRunning = false; // Снимаем флаг анимации
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация трассировки завершена.'});
		console.log("%cAnimation completed successfully", 'color:green;bold;');
		return {completed: true}; // Возвращаем результат: завершено
		// Зависит только от уровня скорости (dispatch стабилен)
	}, [animationSpeedLevel]);

	/**
	 * useCallback для основного обработчика запуска выполнения кода.
	 * Отправляет код и состояние поля на бэкенд, получает результат,
	 * обрабатывает запрос ввода или запускает анимацию трассировки.
	 */
	const handleStart = useCallback(() => {
		// Предотвращаем повторный запуск
		if (state.isRunning || state.isAwaitingInput) {
			logger.log_warning(`Start prevented: isRunning=${state.isRunning}, isAwaitingInput=${state.isAwaitingInput}`);
			dispatch({
				type: 'SET_STATUS_MESSAGE',
				payload: state.isAwaitingInput ? getHint('inputRequired') + ` ${state.inputRequestData?.var_name ?? ''}` : 'Выполнение уже идет...'
			});
			return;
		}
		// Проверка на пустой код
		if (!state.code.trim()) {
			dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код для выполнения пуст.'});
			return;
		}

		// Сбрасываем флаги ожидания перед новым запуском
		dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false});
		dispatch({type: 'SET_INPUT_REQUEST_DATA', payload: null});
		// Устанавливаем флаг выполнения и начальное сообщение
		dispatch({type: 'SET_IS_RUNNING', payload: true});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: getHint('executionStartRequest')});
		logger.log_event('Requesting code execution...');

		// Собираем текущее состояние поля для отправки на бэкенд
		const currentFieldState = {
			width: state.width, height: state.height, cellSize: state.cellSize,
			robotPos: state.robotPos, walls: Array.from(state.walls),
			markers: state.markers, coloredCells: Array.from(state.coloredCells),
			symbols: state.symbols, radiation: state.radiation, temperature: state.temperature
		};

		// Отправляем асинхронный запрос на бэкенд
		fetch(`${backendUrl}/execute`, {
			method: 'POST',
			credentials: 'include', // Важно для передачи cookie сессии
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({code: state.code, fieldState: currentFieldState}), // Отправляем код и состояние поля
		})
			.then(async (response) => { // Обработка HTTP ответа
				if (!response.ok) { // Если статус не 2xx
					let errorMsg = `HTTP ${response.status} ${response.statusText}`;
					try {
						const errorData = await response.json();
						errorMsg = errorData.message || errorMsg;
					} catch (_) {
					}
					throw new Error(errorMsg); // Бросаем ошибку для .catch()
				}
				return response.json(); // Парсим тело ответа как JSON
			})
			.then(async (data) => { // Обработка данных ответа
				if (!isMountedRef.current) return; // Проверка, что компонент еще смонтирован

				// --- Обработка ЗАПРОСА ВВОДА от бэкенда ---
				if (data.input_required) {
					logger.log_event(`Input required for variable: ${data.var_name}`);
					dispatch({type: 'SET_IS_RUNNING', payload: false}); // Снимаем флаг выполнения
					dispatch({type: 'SET_IS_AWAITING_INPUT', payload: true}); // Ставим флаг ожидания ввода
					// Сохраняем данные запроса ввода
					dispatch({
						type: 'SET_INPUT_REQUEST_DATA',
						payload: {var_name: data.var_name, prompt: data.prompt, target_type: data.target_type}
					});
					// Устанавливаем сообщение для пользователя
					dispatch({type: 'SET_STATUS_MESSAGE', payload: `${getHint('inputRequired')} ${data.var_name}`});

					// Показываем стандартный prompt для ввода данных
					const userInput = window.prompt(data.prompt || `Введите значение для ${data.var_name} (тип ${data.target_type || 'неизв.'}):`);

					if (!isMountedRef.current) return; // Повторная проверка после prompt

					if (userInput === null) { // Пользователь нажал "Отмена"
						dispatch({type: 'SET_STATUS_MESSAGE', payload: getHint('inputCancelled')});
						dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false}); // Снимаем флаг ожидания
						logger.log_warning('User cancelled the input prompt.');
					} else { // Пользователь ввел значение
						// Сообщаем пользователю, что нужно перезапустить выполнение
						dispatch({
							type: 'SET_STATUS_MESSAGE',
							payload: `${getHint('inputReceivedNeedsRestart')} Значение: '${userInput}'.`
						});
						dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false}); // Снимаем флаг ожидания
						logger.log_event(`User provided input '${userInput}' for ${data.var_name}. Manual re-run required.`);
						// Здесь НЕ отправляем ввод на бэкенд и НЕ продолжаем выполнение автоматически (упрощенная модель)
					}

					// Применяем состояние поля, которое было ДО запроса ввода (из finalState ответа)
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
						// Обновляем направление ошибки движения робота
						if (data.finalState.robotErrorDirection !== undefined) dispatch({
							type: 'SET_ROBOT_ERROR_DIRECTION',
							payload: data.finalState.robotErrorDirection
						});
					}
					return; // Завершаем обработку этого .then()
				}
				// --- Конец обработки ЗАПРОСА ВВОДА ---			// --- Обработка ОБЫЧНОГО завершения (успех или ошибка без ввода) ---
			try {
				// Анимируем трассировку, если она есть
				if (data.trace?.length > 0) {
					dispatch({type: 'SET_IS_RUNNING', payload: true}); // Флаг на время анимации
					await animateTrace(data.trace);
					// Снимаем флаг после анимации, если она не была прервана
					if (animationControllerRef.current.isRunning === false) {
						dispatch({type: 'SET_IS_RUNNING', payload: false});
						}
					} else { // Если трассировки нет
						dispatch({type: 'SET_IS_RUNNING', payload: false}); // Сразу снимаем флаг
						dispatch({
							type: 'SET_STATUS_MESSAGE',
							payload: data.message || (data.success ? getHint('executionFinishedSuccess') : getHint('executionFinishedError') + ' (нет шагов)')
						});
					}
				} catch (animError) { // Ошибка во время анимации
					console.error("Animation error:", animError);
					logger.log_error(`Animation failed: ${animError.message}`);
					dispatch({type: 'SET_STATUS_MESSAGE', payload: `Ошибка анимации: ${animError.message}`});
					dispatch({type: 'SET_IS_RUNNING', payload: false}); // Снимаем флаг
				}

				if (!isMountedRef.current) return; // Повторная проверка

				// Применяем финальное состояние из ответа сервера, если оно есть
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
					// Обновляем направление ошибки движения робота
					if (data.finalState.robotErrorDirection !== undefined) dispatch({
						type: 'SET_ROBOT_ERROR_DIRECTION',
						payload: data.finalState.robotErrorDirection
					});

					// Устанавливаем финальное сообщение, если анимация не была прервана
					if (animationControllerRef.current.isRunning === false) {
						const finalMessage = data.success ? getHint('executionFinishedSuccess') : `${getHint('executionFinishedError')} ${data.message || '?'}`;
						const finalOutput = data.finalState.output ? `\nВывод:\n${data.finalState.output.trim()}` : ""; // Добавляем вывод программы
						dispatch({type: 'SET_STATUS_MESSAGE', payload: `${finalMessage}${finalOutput}`});
					}
				} else { // Если финального состояния нет в ответе (не должно быть при успехе/ошибке)
					logger.log_warning("No finalState received from server in successful/error response.");
					if (animationControllerRef.current.isRunning === false) {
						dispatch({
							type: 'SET_STATUS_MESSAGE',
							payload: data.message || 'Нет финального состояния от сервера.'
						});
					}
				}

				// Логируем результат
				if (data.success) {
					logger.log_event('Execution successful (server).');
				} else {
					logger.log_error(`Execution failed (server): ${data.message || '?'}`);
				}

				// Убеждаемся, что флаг выполнения снят, если анимация завершилась или ее не было
				if (animationControllerRef.current.isRunning === false) {
					dispatch({type: 'SET_IS_RUNNING', payload: false});
				}
			})
			.catch((error) => { // Обработка ошибок сети или HTTP
				if (!isMountedRef.current) return;
				console.error('Error during fetch /execute:', error);
				const errorText = error.message || 'Неизвестная сетевая ошибка';
				dispatch({type: 'SET_STATUS_MESSAGE', payload: `${getHint('networkError')} ${errorText}`});
				logger.log_error(`Fetch /execute failed: ${errorText}`);
				dispatch({type: 'SET_IS_RUNNING', payload: false});       // Снимаем флаги
				dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false});
			});
		// Зависимости useCallback
	}, [
		state.isRunning, state.isAwaitingInput, state.inputRequestData, state.code,
		state.width, state.height, state.cellSize, state.robotPos, state.walls,
		state.markers, state.coloredCells, state.symbols, state.radiation, state.temperature,
		animateTrace // Добавлены все зависимости из state и внешние функции
	]);

	/**
	 * useEffect для отправки состояния поля на бэкенд с задержкой (debounce).
	 * Срабатывает при изменении любого элемента состояния поля.
	 */
	useEffect(() => {
		const debounceTimeout = 500; // Задержка 500 мс
		const handler = setTimeout(() => {
			if (!isMountedRef.current) return; // Проверка монтирования
			// Собираем актуальное состояние поля
			const fieldState = {
				width: state.width, height: state.height, cellSize: state.cellSize,
				robotPos: state.robotPos, walls: Array.from(state.walls),
				markers: state.markers, coloredCells: Array.from(state.coloredCells),
				symbols: state.symbols, radiation: state.radiation, temperature: state.temperature
			};
			// Отправляем на ручку /updateField
			fetch(`${backendUrl}/updateField`, {
				method: 'POST', credentials: 'include',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify(fieldState),
			})
				.then(response => {
					if (isMountedRef.current && !response.ok) {
						logger.log_warning(`/updateField responded with status ${response.status}`);
					}
				})
				.catch((error) => {
					if (isMountedRef.current) {
						logger.log_error(`/updateField fetch error: ${error.message}`);
					}
				});
		}, debounceTimeout);
		// Очистка таймаута при следующем изменении или размонтировании
		return () => clearTimeout(handler);
		// Зависит от всех частей состояния поля и URL бэкенда
	}, [state.width, state.height, state.cellSize, state.robotPos, state.walls, state.markers, state.coloredCells, state.symbols, state.radiation, state.temperature]);

	/**
	 * useEffect для обновления постоянных стен (границ поля) при изменении размеров.
	 */
	useEffect(() => {
		const expectedPermanentWalls = setupPermanentWalls(state.width, state.height);
		// Сравниваем содержимое Set, предварительно отсортировав и преобразовав в JSON
		if (JSON.stringify([...state.permanentWalls].sort()) !== JSON.stringify([...expectedPermanentWalls].sort())) {
			dispatch({type: 'SET_PERMANENT_WALLS', payload: expectedPermanentWalls});
			logger.log_event(`Permanent walls updated for size ${state.width}x${state.height}`);
		}
		// Зависит от размеров и текущего состояния границ
	}, [state.width, state.height, state.permanentWalls]);

	// --- Рендер основного компонента ---
	return (
		<div className="app-container fade-in"> {/* Основной контейнер приложения */}
			<div className="layout-container">
				{/* Левая панель - редактор кода */}
				<div className="left-panel">
					{/* Компонент редактора кода */}
					<CodeEditor
						code={state.code}
						setCode={c => dispatch({type: 'SET_CODE', payload: c})}
						isRunning={state.isRunning || state.isAwaitingInput} // Блокировка кнопок
						onClearCode={handleClearCode}
						onStop={handleStop}
						onStart={handleStart}
						onReset={handleReset}
						speedLevel={animationSpeedLevel} // Уровень скорости
						onSpeedChange={setAnimationSpeedLevel} // Обработчик изменения скорости
					/>
				</div>
				
				{/* Центральная панель - игровое поле */}
				<div className="center-panel">
					{/* Компонент игрового поля */}
					<Field
						canvasRef={canvasRef} // Передаем реф на canvas
						// Передаем состояние поля для отрисовки
						robotPos={state.robotPos} walls={state.walls} permanentWalls={state.permanentWalls}
						markers={state.markers} coloredCells={state.coloredCells} symbols={state.symbols}
						width={state.width} height={state.height} cellSize={state.cellSize}
						robotErrorDirection={state.robotErrorDirection} // Направление ошибки движения робота
						editMode={state.editMode} statusMessage={state.statusMessage} // Сообщение под полем
						// Передаем функции для взаимодействия с полем
						setRobotPos={p => dispatch({type: 'SET_ROBOT_POS', payload: p})}
						setWalls={w => dispatch({type: 'SET_WALLS', payload: w})}
						setMarkers={m => dispatch({type: 'SET_MARKERS', payload: m})}
						setColoredCells={c => dispatch({type: 'SET_COLORED_CELLS', payload: c})}
						setCellSize={v => dispatch({type: 'SET_CELL_SIZE', payload: v})}
						setStatusMessage={m => dispatch({type: 'SET_STATUS_MESSAGE', payload: m})}
					/>
				</div>

				{/* Правая панель - панель управления */}
				<div className="right-panel">
					{/* Компонент панели управления */}
					<ControlPanel
						// Передаем все необходимые части состояния и функции dispatch
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
				</div>
			</div>
		</div>
	);
});

export default RobotSimulator;
// FILE END: RobotSimulator.jsx