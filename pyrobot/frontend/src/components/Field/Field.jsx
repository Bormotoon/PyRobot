/**
 * @file Field.jsx
 * @description Компонент игрового поля симулятора робота.
 * Этот компонент отвечает за визуализацию игрового поля, робота, стен, маркеров и окрашенных клеток с помощью canvas.
 * Также обрабатываются события мыши для редактирования поля:
 * - Установка/удаление стен
 * - Окрашивание/очистка клеток
 * - Перемещение робота (перетаскивание) в режиме редактирования, игнорируя внутренние стены (учитываются только внешние границы поля)
 * - Установка/удаление маркеров при правом клике
 */

import React, {memo, useCallback, useEffect, useState} from 'react';
import {Card, Typography} from '@mui/material';
import {drawField} from '../canvasDrawing';
import {getHint} from '../hints';
import './Field.css';

const Field = memo(({
	                    // Ссылка на элемент canvas для отрисовки игрового поля
	                    canvasRef,
	                    // Текущая позиция робота в сетке {x, y}
	                    robotPos,
	                    // Функция для обновления позиции робота
	                    setRobotPos,
	                    // Множество временных стен
	                    walls,
	                    // Функция для обновления множества стен
	                    setWalls,
	                    // Множество постоянных стен (редактировать нельзя)
	                    permanentWalls,
	                    // Объект с маркерами на поле
	                    markers,
	                    // Функция для обновления маркеров
	                    setMarkers,
	                    // Множество закрашенных клеток
	                    coloredCells,
	                    // Функция для обновления закрашенных клеток
	                    setColoredCells,
	                    // Ширина поля (количество клеток по горизонтали)
	                    width,
	                    // Высота поля (количество клеток по вертикали)
	                    height,
	                    // Размер клетки в пикселях
	                    cellSize,
	                    // Флаг, указывающий, включён ли режим редактирования поля
	                    editMode,
	                    // Текущие динамические подсказки и сообщения для пользователя
	                    statusMessage,
	                    // Функция для обновления сообщения статуса
	                    setStatusMessage,
                    }) => {
	// Локальное состояние для отслеживания режима перетаскивания робота
	const [isDraggingRobot, setIsDraggingRobot] = useState(false);

	/**
	 * useEffect для перерисовки игрового поля при изменении зависимостей.
	 * Вызывает функцию drawField для обновления содержимого canvas.
	 */
	useEffect(() => {
		if (!canvasRef.current) return;
		drawField(canvasRef.current, {
			coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize,
		});
	}, [canvasRef, coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize]);

	/**
	 * Глобальный useEffect для обработки событий mousemove и mouseup, когда начинается перетаскивание робота.
	 * Это позволяет продолжать перетаскивание, даже если курсор выходит за пределы canvas.
	 */
	useEffect(() => {
		if (isDraggingRobot) {
			// Добавляем глобальные обработчики событий
			window.addEventListener('mousemove', handleMouseMove);
			window.addEventListener('mouseup', handleMouseUp);
			// При завершении перетаскивания удаляем их
			return () => {
				window.removeEventListener('mousemove', handleMouseMove);
				window.removeEventListener('mouseup', handleMouseUp);
			};
		}
	}, [isDraggingRobot]);

	/**
	 * Функция для получения координат курсора относительно canvas.
	 * Учитывает масштабирование и возможные отступы (letterboxing), возникающие из-за CSS‑стилей.
	 *
	 * @param {MouseEvent} event - Событие мыши.
	 * @returns {Object} Объект с координатами {x, y} в системе координат canvas или {x: null, y: null}, если canvas недоступен.
	 */
	const getCanvasCoords = useCallback((event) => {
		const canvas = canvasRef.current;
		if (!canvas) return {x: null, y: null};

		// Получаем размеры canvas, как он отображается на странице (учитывая CSS‑стили, отступы и т.д.)
		const rect = canvas.getBoundingClientRect();

		// Вычисляем соотношение сторон внутреннего canvas (его "логические" размеры)
		const canvasAspect = canvas.width / canvas.height;
		// Вычисляем соотношение сторон отображаемого элемента
		const rectAspect = rect.width / rect.height;

		// Вычисляем координаты клика относительно левого верхнего угла rect
		let offsetX = event.clientX - rect.left;
		let offsetY = event.clientY - rect.top;

		let scaleX, scaleY;

		// Если отображаемая область шире, чем нужно, появляются горизонтальные отступы (letterboxing)
		if (rectAspect > canvasAspect) {
			const effectiveWidth = rect.height * canvasAspect; // Фактическая ширина отрисовки
			const marginX = (rect.width - effectiveWidth) / 2;    // Горизонтальный отступ с обеих сторон
			offsetX = Math.max(0, offsetX - marginX);             // Сдвигаем координату X, убирая отступ
			offsetX = Math.min(offsetX, effectiveWidth);          // Ограничиваем значение effectiveWidth
			scaleX = canvas.width / effectiveWidth;               // Коэффициент масштабирования по X
			scaleY = canvas.height / rect.height;                 // Коэффициент масштабирования по Y
		} else if (rectAspect < canvasAspect) {
			// Если отображаемая область уже, чем нужно, появляются вертикальные отступы
			const effectiveHeight = rect.width / canvasAspect;    // Фактическая высота отрисовки
			const marginY = (rect.height - effectiveHeight) / 2;    // Вертикальный отступ сверху и снизу
			offsetY = Math.max(0, offsetY - marginY);             // Сдвигаем координату Y, убирая отступ
			offsetY = Math.min(offsetY, effectiveHeight);         // Ограничиваем значение effectiveHeight
			scaleX = canvas.width / rect.width;                   // Коэффициент масштабирования по X
			scaleY = canvas.height / effectiveHeight;             // Коэффициент масштабирования по Y
		} else {
			// Если соотношения сторон совпадают, масштабирование прямое
			scaleX = canvas.width / rect.width;
			scaleY = canvas.height / rect.height;
		}

		// Возвращаем координаты в системе координат canvas
		return {x: offsetX * scaleX, y: offsetY * scaleY};
	}, [canvasRef]);

	/**
	 * Функция для проверки, находится ли заданная точка за пределами игрового поля.
	 *
	 * @param {number} px - Координата X в пикселях.
	 * @param {number} py - Координата Y в пикселях.
	 * @returns {boolean} Истина, если точка выходит за границы поля, иначе ложь.
	 */
	const isOutsideCanvas = useCallback((px, py) => {
		return px < 0 || py < 0 || px >= width * cellSize || py >= height * cellSize;
	}, [width, height, cellSize]);

	/**
	 * Функция для преобразования пиксельных координат в координаты сетки (ячейки).
	 *
	 * @param {number} px - Координата X в пикселях.
	 * @param {number} py - Координата Y в пикселях.
	 * @returns {Object} Объект с координатами ячейки {gridX, gridY}.
	 */
	const toGridCoords = useCallback((px, py) => {
		// Вычисляем номер колонки и строки по размеру клетки
		let gx = Math.floor(px / cellSize);
		let gy = Math.floor(py / cellSize);
		// Ограничиваем координаты так, чтобы они не выходили за пределы игрового поля
		gx = Math.min(Math.max(gx, 0), width - 1);
		gy = Math.min(Math.max(gy, 0), height - 1);
		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	/**
	 * Функция для обработки клика по стенам или клеткам.
	 * В зависимости от позиции клика внутри ячейки определяет, устанавливать или удалять стену,
	 * либо окрашивать/очищать клетку.
	 *
	 * @param {number} gx - Координата X ячейки.
	 * @param {number} gy - Координата Y ячейки.
	 * @param {number} px - Точная координата X клика в пикселях.
	 * @param {number} py - Точная координата Y клика в пикселях.
	 */
	const handleWallsAndCells = useCallback((gx, gy, px, py) => {
		const margin = 5; // Зона чувствительности для определения стороны ячейки
		const xRem = px % cellSize; // Остаток от деления по X внутри ячейки
		const yRem = py % cellSize; // Остаток от деления по Y внутри ячейки
		let wall = null;
		// Определяем сторону ячейки, куда произведён клик
		if (xRem < margin) {
			// Левая сторона ячейки
			wall = `${gx},${gy},${gx},${gy + 1}`;
		} else if (xRem > cellSize - margin) {
			// Правая сторона ячейки
			wall = `${gx + 1},${gy},${gx + 1},${gy + 1}`;
		} else if (yRem < margin) {
			// Верхняя сторона ячейки
			wall = `${gx},${gy},${gx + 1},${gy}`;
		} else if (yRem > cellSize - margin) {
			// Нижняя сторона ячейки
			wall = `${gx},${gy + 1},${gx + 1},${gy + 1}`;
		}
		if (wall) {
			// Если стена не является постоянной, изменяем множество временных стен
			if (!permanentWalls.has(wall)) {
				setWalls(prev => {
					const copy = new Set(prev);
					if (copy.has(wall)) {
						// Если стена уже установлена, удаляем её
						copy.delete(wall);
						setStatusMessage('Стена удалена. ' + getHint('canvasLeftClickEditMode', true));
					} else {
						// Если стены нет, устанавливаем её
						copy.add(wall);
						setStatusMessage('Стена поставлена. ' + getHint('canvasLeftClickEditMode', true));
					}
					return copy;
				});
			} else {
				// Если стена является постоянной, уведомляем пользователя
				setStatusMessage('Это постоянная стена. ' + getHint('canvasLeftClickEditMode', true));
			}
		} else {
			// Если клик не попадает в область стены, изменяем окраску клетки
			const posKey = `${gx},${gy}`;
			setColoredCells(prev => {
				const c = new Set(prev);
				if (c.has(posKey)) {
					c.delete(posKey);
					setStatusMessage('Клетка очищена! ' + getHint('canvasLeftClickEditMode', true));
				} else {
					c.add(posKey);
					setStatusMessage('Клетка закрашена! ' + getHint('canvasLeftClickEditMode', true));
				}
				return c;
			});
		}
	}, [cellSize, permanentWalls, setWalls, setColoredCells, setStatusMessage]);

	/**
	 * Обработчик события нажатия кнопки мыши на canvas.
	 * При нажатии левой кнопки начинается режим редактирования поля.
	 * Если клик произведён по ячейке, в которой находится робот, запускается режим перетаскивания робота.
	 *
	 * @param {MouseEvent} e - Событие нажатия кнопки мыши.
	 */
	const handleMouseDown = useCallback((e) => {
		// Обрабатываем только нажатие левой кнопки мыши (button === 0)
		if (e.button !== 0) return;
		e.preventDefault();
		e.stopPropagation();
		// Получаем координаты клика относительно canvas
		const {x, y} = getCanvasCoords(e);
		// Если координаты недоступны или клик за пределами игрового поля, уведомляем пользователя
		if (x === null || y === null || isOutsideCanvas(x, y)) {
			setStatusMessage('Клик за пределами поля.');
			return;
		}
		// Если режим редактирования не активен, выводим соответствующее сообщение
		if (!editMode) {
			setStatusMessage(getHint('canvasLeftClickNoEdit', false));
			return;
		}
		// Преобразуем координаты в координаты сетки (ячейки)
		const {gridX, gridY} = toGridCoords(x, y);
		// Если клик произведён по ячейке, где находится робот, запускаем режим перетаскивания
		if (gridX === robotPos.x && gridY === robotPos.y) {
			setIsDraggingRobot(true);
			setStatusMessage('Начали перетаскивать робота.');
			return;
		}
		// Если клик не по роботу, обрабатываем его как установку/удаление стен или окраску клетки
		handleWallsAndCells(gridX, gridY, x, y);
	}, [editMode, robotPos, getCanvasCoords, isOutsideCanvas, toGridCoords, setStatusMessage, handleWallsAndCells]);

	/**
	 * Обработчик движения мыши при перетаскивании робота.
	 * Получает координаты курсора, преобразует их в координаты сетки и обновляет позицию робота.
	 * Здесь не проверяем, находится ли курсор за пределами поля – функция toGridCoords ограничит координаты.
	 *
	 * @param {MouseEvent} e - Событие движения мыши.
	 */
	const handleMouseMove = useCallback((e) => {
		// Если режим перетаскивания не активен, ничего не делаем
		if (!isDraggingRobot) return;
		e.preventDefault();
		e.stopPropagation();
		// Получаем координаты курсора относительно canvas
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null) return;
		// Преобразуем координаты в координаты сетки (ячейки). Функция toGridCoords гарантирует, что координаты будут в пределах поля.
		const {gridX, gridY} = toGridCoords(x, y);
		// Обновляем позицию робота в сетке, игнорируя внутренние стены
		setRobotPos({x: gridX, y: gridY});
	}, [isDraggingRobot, getCanvasCoords, toGridCoords, setRobotPos]);

	/**
	 * Обработчик события отпускания кнопки мыши.
	 * Завершает режим перетаскивания робота.
	 *
	 * @param {MouseEvent} e - Событие отпускания кнопки мыши.
	 */
	const handleMouseUp = useCallback((e) => {
		// Если режим перетаскивания не активен, ничего не делаем
		if (!isDraggingRobot) return;
		e.preventDefault();
		e.stopPropagation();
		// Завершаем режим перетаскивания робота
		setIsDraggingRobot(false);
		setStatusMessage('Перемещение робота завершено.');
	}, [isDraggingRobot, setStatusMessage]);

	/**
	 * Обработчик правого клика (contextmenu) на canvas.
	 * Используется для установки или удаления маркера на выбранной клетке.
	 *
	 * @param {MouseEvent} e - Событие правого клика мыши.
	 */
	const handleCanvasRightClick = useCallback((e) => {
		e.preventDefault();
		e.stopPropagation();
		// Получаем координаты клика относительно canvas
		const {x, y} = getCanvasCoords(e);
		// Если координаты недоступны или клик за пределами поля, уведомляем пользователя
		if (x === null || y === null || isOutsideCanvas(x, y)) {
			setStatusMessage('Правый клик за пределами поля.');
			return;
		}
		// Если режим редактирования не активен, выводим соответствующее сообщение
		if (!editMode) {
			setStatusMessage(getHint('canvasRightClickNoEdit', false));
			return;
		}
		// Преобразуем координаты в координаты сетки (ячейки)
		const {gridX, gridY} = toGridCoords(x, y);
		const posKey = `${gridX},${gridY}`;
		// Обновляем объект маркеров: если маркер отсутствует, добавляем его, иначе удаляем
		setMarkers(prev => {
			const copy = {...prev};
			if (!copy[posKey]) {
				copy[posKey] = 1;
				setStatusMessage('Маркер добавлен! ' + getHint('canvasRightClickEditMode', true));
			} else {
				delete copy[posKey];
				setStatusMessage('Маркер убран. ' + getHint('canvasRightClickEditMode', true));
			}
			return copy;
		});
	}, [editMode, getCanvasCoords, isOutsideCanvas, toGridCoords, setMarkers, setStatusMessage]);

	// Рендер компонента: область поля и карточка со статусными сообщениями
	return (
		<div className="field-area">
			<Card className="field-card">
				<canvas
					ref={canvasRef}
					width={width * cellSize}    // Ширина canvas = количество клеток по горизонтали * размер клетки
					height={height * cellSize}  // Высота canvas = количество клеток по вертикали * размер клетки
					className={editMode ? 'edit-mode' : ''}  // Применение класса редактирования при активном режиме
					onMouseDown={handleMouseDown}
					onContextMenu={handleCanvasRightClick}
				/>
			</Card>
			{/* Карточка для отображения динамических подсказок и сообщений под игровым полем */}
			<Card className="status-card">
				<Typography variant="body2" className="status-text">
					{statusMessage}
				</Typography>
			</Card>
		</div>
	);
});

export default Field;
