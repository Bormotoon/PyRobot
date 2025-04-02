// FILE START: RobotSimulator.jsx
import React, {memo, useCallback, useEffect, useReducer, useRef, useState} from 'react';
import {ThemeProvider} from '@mui/material';
import CodeEditor from './CodeEditor/CodeEditor'; // Уточните путь
import ControlPanel from './ControlPanel/ControlPanel'; // Уточните путь
import Field from './Field/Field'; // Уточните путь
import theme from '../styles/theme'; // Уточните путь
import {getHint} from './hints'; // Уточните путь
import logger from '../Logger'; // Уточните путь
import io from 'socket.io-client';

// Определяем URL бэкенда из переменных окружения или по умолчанию
const backendUrl = process.env.REACT_APP_BACKEND_URL || `http://${window.location.hostname}:5000`;

// Начальное состояние симулятора
const initialState = {
	code: `использовать Робот\nалг\nнач\n  вправо\n  вниз\n  вправо\nкон`, // Пример кода
	isRunning: false,           // Флаг: идет ли выполнение/анимация
	isAwaitingInput: false,     // Флаг: ожидается ли ввод от пользователя
	statusMessage: getHint('initial'), // Текущее сообщение для пользователя
	// Параметры поля
	width: 7,
	height: 7,
	cellSize: 50,
	// Состояние объектов на поле
	robotPos: {x: 0, y: 0},
	walls: new Set(),           // Пользовательские стены
	permanentWalls: new Set(),  // Границы поля
	markers: {},                // Маркеры { "x,y": 1 }
	coloredCells: new Set(),    // Закрашенные клетки { "x,y" }
	symbols: {},                // Символы { "x,y": { upper: 'A', lower: 'Б' } }
	radiation: {},              // Уровень радиации { "x,y": value }
	temperature: {},            // Температура { "x,y": value }
	// Режим редактирования
	editMode: false,
	// Данные для запроса ввода
	inputRequestData: null,     // { var_name, prompt, target_type }
};

// --- Вспомогательные функции ---

// Создает набор строк, представляющих границы поля
function setupPermanentWalls(width, height) {
	const nw = new Set();
	// Горизонтальные границы
	for (let x = 0; x < width; x++) {
		nw.add(`${x},0,${x + 1},0`);         // Верхняя граница
		nw.add(`${x},${height},${x + 1},${height}`); // Нижняя граница
	}
	// Вертикальные границы
	for (let y = 0; y < height; y++) {
		nw.add(`0,${y},0,${y + 1}`);         // Левая граница
		nw.add(`${width},${y},${width},${y + 1}`); // Правая граница
	}
	return nw;
}

// Ограничивает позицию робота границами поля
function clampRobotPos(robotPos, width, height) {
	const currentX = robotPos?.x ?? 0; // Используем 0, если robotPos не определен
	const currentY = robotPos?.y ?? 0;
	const clampedX = Math.min(Math.max(currentX, 0), width - 1);
	const clampedY = Math.min(Math.max(currentY, 0), height - 1);
	// Возвращаем новый объект только если позиция изменилась
	if (currentX !== clampedX || currentY !== clampedY) {
		return {x: clampedX, y: clampedY};
	}
	return robotPos; // Возвращаем исходный объект, если изменений нет
}

// Редьюсер для управления состоянием симулятора
function reducer(state, action) {
	// Логирование действий редьюсера (можно раскомментировать для отладки)
	// console.groupCollapsed(`%cReducer Action: ${action.type}`, 'color: red;');
	// console.log('Payload:', action.payload);
	// console.log('State Before:', JSON.parse(JSON.stringify(state, (key, value) => value instanceof Set ? Array.from(value) : value)));

	let nextState; // Переменная для нового состояния

	// Обработка различных действий
	switch (action.type) {
		case 'SET_CODE': // Установка нового кода
			nextState = {...state, code: action.payload};
			break;
		case 'SET_IS_RUNNING': // Установка флага выполнения
			nextState = {...state, isRunning: action.payload};
			break;
		case 'SET_IS_AWAITING_INPUT': // Установка флага ожидания ввода
			nextState = {...state, isAwaitingInput: action.payload};
			// Сбрасываем данные запроса, если перестали ждать
			if (!action.payload) {
				nextState.inputRequestData = null;
			}
			break;
		case 'SET_INPUT_REQUEST_DATA': // Сохранение данных для запроса ввода
			nextState = {...state, inputRequestData: action.payload};
			break;
		case 'SET_STATUS_MESSAGE': // Установка статус-сообщения
			nextState = {...state, statusMessage: action.payload};
			break;
		case 'SET_ROBOT_POS': // Установка позиции робота (с ограничением)
			nextState = {...state, robotPos: clampRobotPos(action.payload, state.width, state.height)};
			break;
		case 'SET_WIDTH': { // Установка ширины поля
			const newWidth = Math.max(1, action.payload); // Ширина не меньше 1
			const newRobotPos = clampRobotPos(state.robotPos, newWidth, state.height);
			nextState = {
				...state,
				width: newWidth,
				robotPos: newRobotPos,
				permanentWalls: setupPermanentWalls(newWidth, state.height)
			};
			break;
		}
		case 'SET_HEIGHT': { // Установка высоты поля
			const newHeight = Math.max(1, action.payload); // Высота не меньше 1
			const newRobotPos = clampRobotPos(state.robotPos, state.width, newHeight);
			nextState = {
				...state,
				height: newHeight,
				robotPos: newRobotPos,
				permanentWalls: setupPermanentWalls(state.width, newHeight)
			};
			break;
		}
		case 'SET_CELL_SIZE': // Установка размера клетки
			nextState = {...state, cellSize: Math.max(10, action.payload)}; // Размер не меньше 10
			break;
		case 'SET_WALLS': // Установка пользовательских стен
			// Позволяет передавать функцию для обновления или новый Set/массив
			nextState = {
				...state,
				walls: typeof action.payload === 'function' ? action.payload(state.walls) : new Set(action.payload)
			};
			break;
		case 'SET_PERMANENT_WALLS': // Установка границ поля (обычно вызывается при изменении размера)
			nextState = {...state, permanentWalls: new Set(action.payload)};
			break;
		case 'SET_MARKERS': // Установка маркеров
			nextState = {
				...state,
				markers: typeof action.payload === 'function' ? action.payload(state.markers) : {...action.payload}
			}; // Копируем объект
			break;
		case 'SET_COLORED_CELLS': // Установка закрашенных клеток
			nextState = {
				...state,
				coloredCells: typeof action.payload === 'function' ? action.payload(state.coloredCells) : new Set(action.payload)
			};
			break;
		case 'SET_SYMBOLS': // Установка символов
			nextState = {
				...state,
				symbols: typeof action.payload === 'function' ? action.payload(state.symbols) : {...action.payload}
			}; // Копируем объект
			break;
		case 'SET_RADIATION': // Установка радиации
			nextState = {
				...state,
				radiation: typeof action.payload === 'function' ? action.payload(state.radiation) : {...action.payload}
			}; // Копируем объект
			break;
		case 'SET_TEMPERATURE': // Установка температуры
			nextState = {
				...state,
				temperature: typeof action.payload === 'function' ? action.payload(state.temperature) : {...action.payload}
			}; // Копируем объект
			break;
		case 'SET_EDIT_MODE': // Установка режима редактирования
			nextState = {...state, editMode: action.payload};
			break;
		case 'RESET_STATE': { // Сброс состояния к начальному
			const initialWidth = initialState.width;
			const initialHeight = initialState.height;
			nextState = {
				...initialState, // Копируем все начальные значения
				width: initialWidth,
				height: initialHeight,
				// Пересчитываем границы для начальных размеров
				permanentWalls: setupPermanentWalls(initialWidth, initialHeight),
				// Убеждаемся, что начальная позиция робота в границах
				robotPos: clampRobotPos(initialState.robotPos, initialWidth, initialHeight),
				statusMessage: 'Симулятор сброшен.', // Сообщение о сбросе
				// Сбрасываем флаги выполнения и ожидания
				isRunning: false,
				isAwaitingInput: false,
				inputRequestData: null,
			};
			break;
		}
		default: // Неизвестное действие
			logger.log_error(`Unknown reducer action type: ${action.type}`);
			throw new Error(`Unknown action type: ${action.type}`);
	}

	// Логирование состояния после изменения (можно раскомментировать для отладки)
	// console.log('State After:', JSON.parse(JSON.stringify(nextState, (key, value) => value instanceof Set ? Array.from(value) : value)));
	// console.groupEnd();

	return nextState; // Возвращаем новое состояние
}

// Основной компонент симулятора
const RobotSimulator = memo(() => {
	// Инициализация состояния с помощью редьюсера
	const [state, dispatch] = useReducer(reducer, initialState, (init) => ({
		...init, // Берем начальное состояние
		// Сразу вычисляем границы для начальных размеров
		permanentWalls: setupPermanentWalls(init.width, init.height)
	}));

	// Состояние для скорости анимации
	const [animationSpeedLevel, setAnimationSpeedLevel] = useState(2); // Уровень 0-4

	// Рефы для доступа к DOM элементам и управления состоянием вне рендера
	const canvasRef = useRef(null);      // Реф для canvas
	const socketRef = useRef(null);      // Реф для WebSocket соединения
	const isMountedRef = useRef(true);   // Флаг, смонтирован ли компонент
	const animationControllerRef = useRef({
		stop: () => {
		}, isRunning: false
	}); // Для управления анимацией

	// --- Эффект для установки WebSocket соединения ---
	useEffect(() => {
		isMountedRef.current = true; // Устанавливаем флаг при монтировании
		logger.log_event('Connecting WebSocket...');
		// Создаем соединение
		const socket = io(backendUrl, {
			reconnectionAttempts: 5, // Попробовать переподключиться 5 раз
			timeout: 10000,          // Таймаут подключения 10 секунд
		});
		socketRef.current = socket; // Сохраняем сокет в реф

		// Обработчики событий WebSocket
		socket.on('connect', () => {
			if (isMountedRef.current) logger.log_event(`WS Connected: ${socket.id}`);
		});
		socket.on('disconnect', (reason) => {
			if (isMountedRef.current) logger.log_warning(`WS Disconnected: ${reason}`);
			// Можно добавить логику повторного подключения или уведомления пользователя
		});
		socket.on('connect_error', (err) => {
			if (isMountedRef.current) logger.log_error(`WS Connect Error: ${err.message}`);
		});
		socket.on('connection_ack', (data) => { // Подтверждение от сервера с SID
			if (isMountedRef.current) logger.log_event(`WS Connection ACK SID:${data.sid}`);
			// Здесь можно выполнить действия после успешного подтверждения сессии
		});
		socket.on('execution_progress', (data) => { // Сообщения о прогрессе выполнения
			// Логируем для отладки
			// console.debug("WS Execution Progress:", data);
			// Обновляем статус и позицию робота, только если не идет анимация трассировки
			if (isMountedRef.current && state.isRunning && !animationControllerRef.current.isRunning) {
				const msgPrefix = data.error ? `[Ошибка шаг ${data.commandIndex}]` : `[Шаг ${data.commandIndex}]`;
				// Показываем пару последних строк вывода, если есть
				const outputLines = data.output ? data.output.trim().split('\n') : [];
				const msgOutput = outputLines.length > 0 ? ` Вывод: ${outputLines.slice(-2).join(' \\n ')}` : '';
				const msgError = data.error ? ` ${data.error}` : '';
				dispatch({type: 'SET_STATUS_MESSAGE', payload: `${msgPrefix}${msgError}${msgOutput}`});
				// Обновляем позицию робота во время выполнения
				if (data.robotPos) {
					dispatch({type: 'SET_ROBOT_POS', payload: data.robotPos});
				}
			}
		});

		// Функция очистки при размонтировании компонента
		return () => {
			isMountedRef.current = false; // Снимаем флаг
			animationControllerRef.current.stop(); // Останавливаем анимацию, если идет
			if (socketRef.current) {
				logger.log_event('Disconnecting WebSocket...');
				socketRef.current.disconnect(); // Закрываем соединение
			}
		};
	}, [backendUrl]); // Перезапускаем эффект только если URL бэкенда изменится

	// Перенесли зависимость state.isRunning из useEffect для сокета,
	// т.к. обработчик progress должен работать независимо от флага isRunning,
	// но обновление UI зависит от этого флага внутри обработчика.

	// --- Обработчики действий пользователя ---

	const handleClearCode = useCallback(() => {
		dispatch({type: 'SET_CODE', payload: `использовать Робот\nалг\nнач\n  \nкон`});
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код очищен.'});
		logger.log_event('Code cleared by user.');
	}, []);

	const handleStop = useCallback(() => {
		animationControllerRef.current.stop(); // Останавливаем анимацию
		dispatch({type: 'SET_IS_RUNNING', payload: false});
		dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false}); // Сбрасываем ожидание ввода
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Выполнение остановлено.'});
		logger.log_event('Execution stopped by user.');
		// TODO: Возможно, нужно отправить сигнал остановки на бэкенд, если выполнение там долгое
	}, []);

	const handleReset = useCallback(() => {
		animationControllerRef.current.stop(); // Останавливаем анимацию
		dispatch({type: 'RESET_STATE'}); // Сбрасываем состояние фронтенда
		// dispatch({ type: 'SET_IS_RUNNING', payload: false }); // Уже делается в RESET_STATE
		// dispatch({ type: 'SET_IS_AWAITING_INPUT', payload: false }); // Уже делается в RESET_STATE
		logger.log_event('Simulator state reset by user.');
		// Отправляем запрос на сброс состояния на бэкенде (в сессии)
		fetch(`${backendUrl}/reset`, {method: 'POST', credentials: 'include'})
			.then(res => {
				if (!res.ok) logger.log_warning(`/reset request failed with status ${res.status}`);
				else logger.log_event('/reset request successful.');
			})
			.catch(e => logger.log_error(`/reset fetch error: ${e.message}`));
	}, [backendUrl]); // Добавили backendUrl в зависимости

	// --- Функция анимации трассировки ---
	const animateTrace = useCallback(async (trace) => {
		if (!trace || !Array.isArray(trace) || trace.length === 0) {
			logger.log_event('Animation skipped: No trace data.');
			return {completed: true}; // Считаем завершенной, если трассировки нет
		}

		let continueAnimation = true;
		const stopAnimation = () => {
			logger.log_event('Animation stop requested.');
			continueAnimation = false;
		};
		animationControllerRef.current = {stop: stopAnimation, isRunning: true};

		// Вычисляем задержку на основе уровня скорости
		// Уровни: 0 (2с), 1 (1с), 2 (0.5с), 3 (0.25с), 4 (0с - мгновенно)
		const delay = [2000, 1000, 500, 250, 0][animationSpeedLevel];
		dispatch({type: 'SET_STATUS_MESSAGE', payload: `Анимация трассировки (шаг 1/${trace.length})...`});
		console.groupCollapsed(`%cAnimation (Speed Level: ${animationSpeedLevel}, Delay: ${delay}ms)`, 'color:green');
		console.log("Trace data:", trace);
		console.groupEnd();

		// Проходим по каждому шагу трассировки
		for (let i = 0; i < trace.length; i++) {
			const event = trace[i];
			// console.debug(`%cAnim Step ${i + 1}/${trace.length}`, 'color:darkcyan', event); // Детальное логирование шага

			// Проверяем, нужно ли продолжать анимацию и смонтирован ли компонент
			if (!isMountedRef.current || !continueAnimation) {
				logger.log_event('Animation interrupted.');
				animationControllerRef.current.isRunning = false;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация прервана.'});
				return {completed: false};
			}

			// Применяем состояние ПОСЛЕ выполнения команды из шага трассировки
			if (event.stateAfter) {
				// Обновляем только те части состояния, которые есть в stateAfter
				if (event.stateAfter.robot) dispatch({type: 'SET_ROBOT_POS', payload: event.stateAfter.robot});
				if (event.stateAfter.coloredCells) dispatch({
					type: 'SET_COLORED_CELLS',
					payload: new Set(event.stateAfter.coloredCells)
				});
				if (event.stateAfter.symbols !== undefined) dispatch({
					type: 'SET_SYMBOLS',
					payload: event.stateAfter.symbols || {}
				}); // Учитываем null/undefined
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

				// Обновляем сообщение в статусе
				const commandText = event.command ? `: ${event.command}` : '';
				const message = event.error
					? `Ошибка на шаге ${event.commandIndex + 1}${commandText}: ${event.error}`
					: `Шаг ${event.commandIndex + 1}/${trace.length}${commandText}`;
				dispatch({type: 'SET_STATUS_MESSAGE', payload: message});
			} else {
				// Это не должно происходить, если бэкенд всегда отдает stateAfter
				console.warn("Trace event missing stateAfter:", event);
				dispatch({
					type: 'SET_STATUS_MESSAGE',
					payload: `Шаг ${event.commandIndex + 1}: Ошибка - нет данных о состоянии`
				});
			}

			// Применяем задержку, если скорость не мгновенная
			if (delay > 0) {
				await new Promise(resolve => setTimeout(resolve, delay));
			}

			// Если на этом шаге была ошибка, прерываем анимацию после показа состояния
			if (event.error) {
				logger.log_error(`Animation stopped due to error at step ${event.commandIndex + 1}: ${event.error}`);
				animationControllerRef.current.isRunning = false;
				// Сообщение об ошибке уже установлено
				return {completed: false, error: true};
			}
		}

		// Анимация успешно завершена
		animationControllerRef.current.isRunning = false;
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Анимация трассировки завершена.'});
		console.log("%cAnimation completed successfully", 'color:green;bold;');
		return {completed: true};
	}, [animationSpeedLevel]); // Зависит только от уровня скорости

	// --- Основной обработчик запуска выполнения ---
	const handleStart = useCallback(() => {
		// Предотвращаем запуск, если уже работает или ждет ввода
		if (state.isRunning || state.isAwaitingInput) {
			logger.log_warning(`Start prevented: isRunning=${state.isRunning}, isAwaitingInput=${state.isAwaitingInput}`);
			dispatch({
				type: 'SET_STATUS_MESSAGE',
				payload: state.isAwaitingInput ? 'Ожидание ввода...' : 'Выполнение уже идет...'
			});
			return;
		}
		// Проверяем, есть ли код
		if (!state.code.trim()) {
			dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Код для выполнения пуст.'});
			return;
		}

		// Сбрасываем флаги перед запуском
		dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false});
		dispatch({type: 'SET_INPUT_REQUEST_DATA', payload: null});
		dispatch({type: 'SET_IS_RUNNING', payload: true}); // Устанавливаем флаг выполнения
		dispatch({type: 'SET_STATUS_MESSAGE', payload: 'Запрос на выполнение...'});
		logger.log_event('Requesting code execution...');

		// Собираем текущее состояние поля для отправки
		const currentFieldState = {
			width: state.width, height: state.height, cellSize: state.cellSize, // Включаем cellSize? (Бэкенд его не использует, но для полноты можно)
			robotPos: state.robotPos, walls: Array.from(state.walls),
			markers: state.markers, coloredCells: Array.from(state.coloredCells),
			symbols: state.symbols, radiation: state.radiation, temperature: state.temperature
		};
		// console.log("%cPOST /execute with state:", 'color:orange;', currentFieldState);

		// Отправляем запрос на бэкенд
		fetch(`${backendUrl}/execute`, {
			method: 'POST',
			credentials: 'include', // Для передачи cookies сессии
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({code: state.code, fieldState: currentFieldState}),
		})
			.then(async (response) => { // Обрабатываем HTTP ответ
				if (!response.ok) {
					let errorMsg = `HTTP ошибка: ${response.status} ${response.statusText}`;
					try {
						const errorData = await response.json();
						errorMsg = errorData.message || errorMsg;
					} catch (_) {
					}
					throw new Error(errorMsg); // Бросаем ошибку для .catch()
				}
				return response.json(); // Парсим JSON
			})
			.then(async (data) => { // Обрабатываем данные ответа
				// console.log("%cGET /execute response data:", 'color:purple;', data);
				if (!isMountedRef.current) return; // Проверяем, что компонент все еще активен

				// --- ОБРАБОТКА ЗАПРОСА ВВОДА ---
				if (data.input_required) {
					logger.log_event(`Input required for variable: ${data.var_name}`);
					dispatch({type: 'SET_IS_RUNNING', payload: false});      // Снимаем флаг выполнения
					dispatch({type: 'SET_IS_AWAITING_INPUT', payload: true}); // Ставим флаг ожидания
					dispatch({
						type: 'SET_INPUT_REQUEST_DATA',
						payload: {var_name: data.var_name, prompt: data.prompt, target_type: data.target_type}
					});
					dispatch({
						type: 'SET_STATUS_MESSAGE',
						payload: data.message || `Требуется ввод для ${data.var_name}...`
					}); // Сообщение для пользователя

					// Показываем prompt пользователю
					const userInput = window.prompt(data.prompt || `Введите значение для ${data.var_name} (тип ${data.target_type || 'неизв.'}):`);

					if (!isMountedRef.current) return; // Повторная проверка после prompt

					if (userInput === null) { // Пользователь нажал "Отмена"
						dispatch({
							type: 'SET_STATUS_MESSAGE',
							payload: 'Ввод отменен. Запустите код снова, если нужно.'
						});
						dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false}); // Снимаем флаг ожидания
						logger.log_warning('User cancelled the input prompt.');
					} else { // Пользователь ввел значение
						// ----- УПРОЩЕННЫЙ ВАРИАНТ (А) -----
						// Просто сообщаем, что ввод получен, и нужно перезапустить
						dispatch({
							type: 'SET_STATUS_MESSAGE',
							payload: `Значение '${userInput}' для '${data.var_name}' принято. Для продолжения запустите код снова.`
						});
						dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false}); // Снимаем флаг ожидания
						logger.log_event(`User provided input '${userInput}' for ${data.var_name}. Manual re-run required.`);
						// -------------------------------------
						/* // ----- ВАРИАНТ Б (СЛОЖНЕЕ - требует доработки бэкенда) -----
						logger.log_event(`User provided input '${userInput}' for ${data.var_name}. Sending back to server...`);
						dispatch({ type: 'SET_STATUS_MESSAGE', payload: `Отправка '${userInput}' для ${data.var_name}...` });
						// Отправить userInput и состояние data.finalState на новую ручку /continue_execute
						fetch(`${backendUrl}/continue_execute`, { // НОВАЯ РУЧКА НА БЭКЕНДЕ
							method: 'POST', credentials: 'include', headers: {'Content-Type': 'application/json'},
							body: JSON.stringify({
								userInput: userInput,
								varName: data.var_name,
								interpreterState: data.finalState // Состояние интерпретатора до ввода
							}),
						})
						.then(async (contResponse) => { // Обработать ответ от /continue_execute
							if (!contResponse.ok) { // Ошибка продолжения
								let contErrorMsg = `HTTP ${contResponse.status}`;
								try { const contErrorData = await contResponse.json(); contErrorMsg = contErrorData.message || contErrorMsg; } catch (_) {}
								throw new Error(contErrorMsg);
							}
							return contResponse.json();
						})
						.then(async (contData) => { // Успешное продолжение
							if (!isMountedRef.current) return;
							logger.log_event("Execution continued successfully after input.");
							dispatch({ type: 'SET_IS_AWAITING_INPUT', payload: false }); // Снимаем флаг ожидания
							// Запускаем анимацию ОСТАВШЕЙСЯ части трассировки из contData.trace
							// и обрабатываем финальный результат из contData
							// ... (логика похожа на обработку обычного /execute) ...
						})
						.catch((contError) => { // Ошибка при продолжении
							if (!isMountedRef.current) return;
							logger.log_error(`Continue execution failed: ${contError.message}`);
							dispatch({ type: 'SET_STATUS_MESSAGE', payload: `Ошибка продолжения: ${contError.message}` });
							dispatch({ type: 'SET_IS_AWAITING_INPUT', payload: false }); // Снимаем флаг ожидания
							dispatch({ type: 'SET_IS_RUNNING', payload: false }); // Останавливаем выполнение
						});
						// ----- КОНЕЦ ВАРИАНТА Б ----- */
					}

					// Вне зависимости от действий пользователя, применяем состояние,
					// которое было на момент запроса ввода, чтобы UI был консистентным.
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
					return; // Выходим из обработчика .then(), т.к. ввод обработан (или отменен)
				}
				// --- КОНЕЦ ОБРАБОТКИ ЗАПРОСА ВВОДА ---

				// --- Обработка обычного завершения (успех или ошибка без ввода) ---
				let animationResult = {completed: true}; // Результат анимации по умолчанию
				try {
					// Анимируем трассировку, если она есть
					if (data.trace?.length > 0) {
						// Передаем isRunning=true, чтобы анимация могла обновлять статус
						dispatch({type: 'SET_IS_RUNNING', payload: true});
						animationResult = await animateTrace(data.trace);
						// После анимации снимаем флаг isRunning только если не было запроса на остановку
						if (animationControllerRef.current.isRunning === false) { // Проверяем флаг контроллера
							dispatch({type: 'SET_IS_RUNNING', payload: false});
						}
					} else {
						// Если трассировки нет, сразу снимаем флаг isRunning
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
					dispatch({type: 'SET_IS_RUNNING', payload: false}); // Снимаем флаг при ошибке анимации
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

					// Обновляем финальное сообщение статуса, если анимация не была прервана
					if (animationControllerRef.current.isRunning === false) { // Используем флаг контроллера
						const finalMessage = data.message || (data.success ? 'Выполнение успешно завершено.' : 'Выполнение завершено с ошибкой.');
						// Добавляем вывод, если он есть
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

				// Логируем результат
				if (data.success) {
					logger.log_event('Execution successful (server).');
				} else {
					logger.log_error(`Execution failed (server): ${data.message || '?'}`);
				}

				// Убедимся, что флаг isRunning снят, если анимация завершилась или ее не было
				if (animationControllerRef.current.isRunning === false) {
					dispatch({type: 'SET_IS_RUNNING', payload: false});
				}
			})
			.catch((error) => { // Обработка ошибок fetch или HTTP
				if (!isMountedRef.current) return;
				console.error('Error during fetch /execute:', error);
				const errorText = error.message || 'Неизвестная сетевая ошибка';
				dispatch({type: 'SET_STATUS_MESSAGE', payload: `Ошибка сети: ${errorText}`});
				logger.log_error(`Fetch /execute failed: ${errorText}`);
				dispatch({type: 'SET_IS_RUNNING', payload: false});
				dispatch({type: 'SET_IS_AWAITING_INPUT', payload: false}); // Сбрасываем ожидание ввода при ошибке сети
			});
	}, [state.isRunning, state.isAwaitingInput, state.code, state.width, state.height, state.robotPos, state.walls, state.markers, state.coloredCells, state.symbols, state.radiation, state.temperature, animateTrace, backendUrl]);

	// Эффект для отправки состояния поля на бэкенд (debounced)
	useEffect(() => {
		const debounceTimeout = 500; // Задержка в мс
		const handler = setTimeout(() => {
			if (!isMountedRef.current) return;
			const fieldState = { // Собираем актуальное состояние
				width: state.width, height: state.height, cellSize: state.cellSize,
				robotPos: state.robotPos, walls: Array.from(state.walls),
				markers: state.markers, coloredCells: Array.from(state.coloredCells),
				symbols: state.symbols, radiation: state.radiation, temperature: state.temperature
			};
			// Логируем отправляемое состояние (опционально)
			// const stateToLog = JSON.stringify(fieldState, (k, v) => v instanceof Set ? [...v] : v, 2);
			// console.log('%cPOST /updateField (debounced):', 'color:#f5a623;', JSON.parse(stateToLog));

			// Отправляем на бэкенд
			fetch(`${backendUrl}/updateField`, {
				method: 'POST', credentials: 'include',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify(fieldState),
			})
				.then(response => {
					if (isMountedRef.current && !response.ok) {
						// Логируем ошибку, если ответ не OK
						logger.log_warning(`/updateField responded with status ${response.status}`);
					}
				})
				.catch((error) => {
					// Логируем ошибку сети
					if (isMountedRef.current) {
						logger.log_error(`/updateField fetch error: ${error.message}`);
					}
				});
		}, debounceTimeout); // Выполняем отправку через 500 мс после последнего изменения

		// Очищаем таймаут при изменении зависимостей или размонтировании
		return () => clearTimeout(handler);
	}, [ // Зависимости для пересоздания таймаута
		state.width, state.height, state.cellSize, state.robotPos,
		state.walls, state.markers, state.coloredCells, state.symbols,
		state.radiation, state.temperature, backendUrl
	]);

	// Эффект для обновления границ поля при изменении размеров
	useEffect(() => {
		const expectedPermanentWalls = setupPermanentWalls(state.width, state.height);
		// Сравниваем содержимое Set как строки для простоты
		if (JSON.stringify([...state.permanentWalls].sort()) !== JSON.stringify([...expectedPermanentWalls].sort())) {
			dispatch({type: 'SET_PERMANENT_WALLS', payload: expectedPermanentWalls});
			logger.log_event(`Permanent walls updated for size ${state.width}x${state.height}`);
		}
	}, [state.width, state.height, state.permanentWalls]); // Зависит от размеров и текущих границ

	// Формируем текст для строки статуса под редактором
	const statusText = `Поз: (${state.robotPos?.x ?? '?'},${state.robotPos?.y ?? '?'}) | ${state.width}x${state.height} | ${state.editMode ? 'Ред.' : 'Упр.'}`;

	// --- Рендер компонента ---
	return (
		<ThemeProvider theme={theme}>
			<div className="app-container">
				{/* Компонент редактора кода */}
				<CodeEditor
					code={state.code}
					setCode={c => dispatch({type: 'SET_CODE', payload: c})}
					// Блокируем кнопки, если идет выполнение или ожидание ввода
					isRunning={state.isRunning || state.isAwaitingInput}
					onClearCode={handleClearCode}
					onStop={handleStop}
					onStart={handleStart}
					onReset={handleReset}
					statusText={statusText}
					speedLevel={animationSpeedLevel} // Передаем уровень скорости
					onSpeedChange={setAnimationSpeedLevel} // Обработчик изменения скорости
					// error={state.statusMessage.startsWith('Ошибка') ? state.statusMessage : ''} // Передача ошибки в редактор (опционально)
				/>
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
				{/* Компонент игрового поля */}
				<Field
					canvasRef={canvasRef} // Передаем реф для canvas
					// Передаем состояние поля для отрисовки
					robotPos={state.robotPos}
					walls={state.walls}
					permanentWalls={state.permanentWalls}
					markers={state.markers}
					coloredCells={state.coloredCells}
					symbols={state.symbols}
					// radiation={state.radiation} // Передать, если Field их рисует
					// temperature={state.temperature} // Передать, если Field их рисует
					width={state.width}
					height={state.height}
					cellSize={state.cellSize}
					editMode={state.editMode}
					statusMessage={state.statusMessage} // Сообщение под полем
					// Передаем функции для обработки действий на поле
					setRobotPos={p => dispatch({type: 'SET_ROBOT_POS', payload: p})}
					setWalls={w => dispatch({type: 'SET_WALLS', payload: w})}
					setMarkers={m => dispatch({type: 'SET_MARKERS', payload: m})}
					setColoredCells={c => dispatch({type: 'SET_COLORED_CELLS', payload: c})}
					setCellSize={v => dispatch({type: 'SET_CELL_SIZE', payload: v})}
					setStatusMessage={m => dispatch({type: 'SET_STATUS_MESSAGE', payload: m})}
					// setSymbols не нужен в Field, т.к. символы ставятся кодом
				/>
			</div>
		</ThemeProvider>
	);
});

export default RobotSimulator;
// FILE END: RobotSimulator.jsx