/**
 * @file Field.jsx
 * @description Компонент игрового поля симулятора робота.
 * Этот компонент отвечает за визуализацию поля, робота, стен, маркеров и окрашенных клеток с помощью canvas.
 * Также обрабатываются события мыши для редактирования поля (установка/удаление стен, окрашивание клеток,
 * перемещение робота и установка/удаление маркеров при правом клике).
 */

import React, {memo, useCallback, useEffect, useState} from 'react';
import {Card, Typography} from '@mui/material';
import {drawField} from '../canvasDrawing';
import {getHint} from '../hints';
import './Field.css';

const Field = memo(({
	                    canvasRef,         // Ссылка на элемент canvas для рисования поля
	                    robotPos,          // Текущая позиция робота {x, y}
	                    setRobotPos,       // Функция обновления позиции робота
	                    walls,             // Множество временных стен
	                    setWalls,          // Функция для обновления множества стен
	                    permanentWalls,    // Множество постоянных стен (не редактируются)
	                    markers,           // Объект с маркерами на поле
	                    setMarkers,        // Функция для обновления маркеров
	                    coloredCells,      // Множество закрашенных клеток
	                    setColoredCells,   // Функция для обновления закрашенных клеток
	                    width,             // Ширина поля (количество клеток)
	                    height,            // Высота поля (количество клеток)
	                    cellSize,          // Размер клетки в пикселях
	                    editMode,          // Флаг, определяющий, включен ли режим редактирования поля
	                    statusMessage,     // Текущие динамические подсказки и сообщения для пользователя
	                    setStatusMessage,  // Функция для обновления статусного сообщения
                    }) => {
	// Локальное состояние для отслеживания, перетаскивается ли робот
	const [isDraggingRobot, setIsDraggingRobot] = useState(false);

	/**
	 * Хук useEffect для перерисовки игрового поля при изменении зависимостей.
	 * Вызывает функцию drawField для обновления canvas.
	 */
	useEffect(() => {
		if (!canvasRef.current) return;
		drawField(canvasRef.current, {
			coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize,
		});
	}, [canvasRef, coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize]);

	/**
	 * Функция для получения координат курсора относительно canvas.
	 *
	 * @param {MouseEvent} event - Событие мыши.
	 * @returns {Object} Объект с координатами {x, y} на canvas или {x: null, y: null}, если canvas недоступен.
	 */
	const getCanvasCoords = useCallback((event) => {
		const canvas = canvasRef.current;
		if (!canvas) return {x: null, y: null};
		// Получаем размеры и положение canvas на странице
		const rect = canvas.getBoundingClientRect();
		// Вычисляем масштаб по осям X и Y
		const scaleX = canvas.width / rect.width;
		const scaleY = canvas.height / rect.height;
		// Пересчитываем координаты события в координаты canvas
		const x = (event.clientX - rect.left) * scaleX;
		const y = (event.clientY - rect.top) * scaleY;
		return {x, y};
	}, [canvasRef]);

	/**
	 * Функция для проверки, находится ли заданная точка за пределами поля.
	 *
	 * @param {number} px - Координата X в пикселях.
	 * @param {number} py - Координата Y в пикселях.
	 * @returns {boolean} Истина, если точка за пределами поля, иначе ложь.
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
		let gx = Math.floor(px / cellSize);
		let gy = Math.floor(py / cellSize);
		// Ограничиваем координаты, чтобы они не выходили за пределы поля
		gx = Math.min(Math.max(gx, 0), width - 1);
		gy = Math.min(Math.max(gy, 0), height - 1);
		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	/**
	 * Функция для обработки клика по стенам или клеткам.
	 * В зависимости от позиции клика на ячейке определяет, устанавливать или удалять стену,
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
		// Определяем, с какой стороны ячейки был совершен клик
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
			// Если стена не является постоянной, изменяем множество стен
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
				// Если стена постоянная, уведомляем пользователя
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
	 * При левой кнопке инициируется процесс редактирования поля, либо начинается перетаскивание робота.
	 *
	 * @param {MouseEvent} e - Событие нажатия мыши.
	 */
	const handleMouseDown = useCallback((e) => {
		// Обрабатываем только левую кнопку мыши (button === 0)
		if (e.button !== 0) return;
		e.preventDefault();
		e.stopPropagation();
		const {x, y} = getCanvasCoords(e);
		// Если координаты недоступны или клик за пределами поля, уведомляем пользователя
		if (x === null || y === null || isOutsideCanvas(x, y)) {
			setStatusMessage('Клик за пределами поля.');
			return;
		}
		// Если режим редактирования не активен, выводим сообщение об этом
		if (!editMode) {
			setStatusMessage(getHint('canvasLeftClickNoEdit', false));
			return;
		}
		// Преобразуем координаты в координаты сетки
		const {gridX, gridY} = toGridCoords(x, y);
		// Если клик произведён по позиции робота, начинаем перетаскивание робота
		if (gridX === robotPos.x && gridY === robotPos.y) {
			setIsDraggingRobot(true);
			setStatusMessage('Начали перетаскивать робота.');
			return;
		}
		// В противном случае обрабатываем клик как установку/удаление стен или окраску клетки
		handleWallsAndCells(gridX, gridY, x, y);
	}, [editMode, robotPos, getCanvasCoords, isOutsideCanvas, toGridCoords, setStatusMessage, handleWallsAndCells]);

	/**
	 * Обработчик движения мыши по canvas.
	 * Если происходит перетаскивание робота, обновляет его позицию.
	 *
	 * @param {MouseEvent} e - Событие движения мыши.
	 */
	const handleMouseMove = useCallback((e) => {
		if (!isDraggingRobot) return;
		e.preventDefault();
		e.stopPropagation();
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvas(x, y)) return;
		const {gridX, gridY} = toGridCoords(x, y);
		// Обновляем позицию робота в сетке
		setRobotPos({x: gridX, y: gridY});
	}, [isDraggingRobot, getCanvasCoords, toGridCoords, setRobotPos, isOutsideCanvas]);

	/**
	 * Обработчик события отпускания кнопки мыши.
	 * Завершает процесс перетаскивания робота.
	 *
	 * @param {MouseEvent} e - Событие отпускания мыши.
	 */
	const handleMouseUp = useCallback((e) => {
		if (!isDraggingRobot) return;
		e.preventDefault();
		e.stopPropagation();
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
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvas(x, y)) {
			setStatusMessage('Правый клик за пределами поля.');
			return;
		}
		if (!editMode) {
			setStatusMessage(getHint('canvasRightClickNoEdit', false));
			return;
		}
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

	return (<div className="field-area">
			<Card className="field-card">
				<canvas
					ref={canvasRef}
					width={width * cellSize}    // Ширина canvas = количество клеток по горизонтали * размер клетки
					height={height * cellSize}  // Высота canvas = количество клеток по вертикали * размер клетки
					className={editMode ? 'edit-mode' : ''}  // Применение класса редактирования при активном editMode
					onMouseDown={handleMouseDown}
					onMouseMove={handleMouseMove}
					onMouseUp={handleMouseUp}
					onContextMenu={handleCanvasRightClick}
				/>
			</Card>

			{/* Карточка для отображения динамических подсказок под полем */}
			<Card className="status-card">
				<Typography variant="body2" className="status-text">
					{statusMessage}
				</Typography>
			</Card>
		</div>);
});

export default Field;
