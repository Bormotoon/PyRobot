/**
 * @file Field.jsx
 * @description Компонент игрового поля симулятора робота.
 * Отвечает за визуализацию поля, робота, стен, маркеров и окрашенных клеток с использованием canvas.
 * Обрабатывает события мыши для редактирования поля (установка/удаление стен, окраска клеток, перетаскивание робота).
 * Также обрабатывает масштабирование колесиком мыши.
 */

import React, {memo, useCallback, useEffect, useRef, useState} from 'react';
import {Card, Typography} from '@mui/material';
import {drawField} from '../canvasDrawing';
import {getHint} from '../hints';
import './Field.css';
import logger from '../../Logger'; // Correct path assumed

const Field = memo(({
	                    canvasRef,
	                    robotPos,
	                    setRobotPos,
	                    walls,
	                    setWalls,
	                    permanentWalls,
	                    markers,
	                    setMarkers,
	                    coloredCells,
	                    setColoredCells,
	                    width,
	                    height,
	                    cellSize,
	                    setCellSize, // Receive setter for cellSize (zoom)
	                    editMode,
	                    statusMessage,
	                    setStatusMessage,
                    }) => {
	const [isDraggingRobot, setIsDraggingRobot] = useState(false);
	const dragStartRef = useRef({x: 0, y: 0}); // Store initial robot pos on drag start

	// Перерисовка поля при изменении зависимостей
	useEffect(() => {
		if (!canvasRef.current) return;
		drawField(canvasRef.current, {coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize});
	}, [canvasRef, coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize]);

	/**
	 * Получает координаты курсора относительно canvas, учитывая масштабирование CSS.
	 * @param {MouseEvent} event - Событие мыши.
	 * @returns {Object} Объект с координатами {x, y} или {x: null, y: null}, если canvas недоступен.
	 */
	const getCanvasCoords = useCallback((event) => {
		const canvas = canvasRef.current;
		if (!canvas) return {x: null, y: null};
		const rect = canvas.getBoundingClientRect();
		// Координаты клика относительно viewport
		const clientX = event.clientX;
		const clientY = event.clientY;
		// Координаты клика относительно верхнего левого угла canvas элемента
		const canvasX = clientX - rect.left;
		const canvasY = clientY - rect.top;
		// Рассчитываем масштаб отображения canvas к его реальным размерам
		const scaleX = canvas.width / rect.width;
		const scaleY = canvas.height / rect.height;
		// Применяем масштаб для получения координат на реальном canvas
		const x = canvasX * scaleX;
		const y = canvasY * scaleY;

		// Проверяем, находится ли клик внутри границ (на случай погрешностей)
		if (x < 0 || x > canvas.width || y < 0 || y > canvas.height) {
			return {x: null, y: null}; // Клик вне видимой области canvas
		}

		return {x, y};
	}, [canvasRef]); // No dependencies on dimensions or cellsize here

	/**
	 * Проверяет, находится ли точка (в пикселях) за пределами игрового поля.
	 * @param {number} px - Координата X в пикселях.
	 * @param {number} py - Координата Y в пикселях.
	 * @returns {boolean} Истина, если точка за пределами.
	 */
	const isOutsideCanvasPixels = useCallback((px, py) => {
		return px < 0 || py < 0 || px >= width * cellSize || py >= height * cellSize;
	}, [width, height, cellSize]);

	/**
	 * Преобразует координаты пикселей в координаты сетки.
	 * @param {number} px - Координата X в пикселях.
	 * @param {number} py - Координата Y в пикселях.
	 * @returns {Object} Объект с координатами сетки {gridX, gridY}.
	 */
	const toGridCoords = useCallback((px, py) => {
		let gx = Math.floor(px / cellSize);
		let gy = Math.floor(py / cellSize);
		// Clamp coordinates to be within the valid grid range [0, width-1] and [0, height-1]
		gx = Math.min(Math.max(gx, 0), width - 1);
		gy = Math.min(Math.max(gy, 0), height - 1);
		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	/**
	 * Обрабатывает клики по canvas для установки/удаления стен или окраски клеток в режиме редактирования.
	 * @param {number} gx - Координата X ячейки.
	 * @param {number} gy - Координата Y ячейки.
	 * @param {number} px - Точная координата X клика в пикселях.
	 * @param {number} py - Точная координата Y клика в пикселях.
	 */
	const handleWallsAndCells = useCallback((gx, gy, px, py) => {
		const wallMargin = Math.max(2, Math.min(8, cellSize * 0.1)); // Margin for wall clicks, proportional but capped
		const xRem = px % cellSize;
		const yRem = py % cellSize;

		let wallKey = null;
		let wallType = ''; // 'horizontal' or 'vertical'

		// Check vertical wall candidates (left/right edges of cell)
		if (xRem < wallMargin && gx > 0) { // Click near left edge (wall between gx-1 and gx)
			wallKey = `${gx},${gy},${gx},${gy + 1}`; // Vertical wall to the left
			wallType = 'vertical';
		} else if (xRem > cellSize - wallMargin && gx < width - 1) { // Click near right edge (wall between gx and gx+1)
			wallKey = `${gx + 1},${gy},${gx + 1},${gy + 1}`; // Vertical wall to the right
			wallType = 'vertical';
		}
		// Check horizontal wall candidates (top/bottom edges of cell)
		else if (yRem < wallMargin && gy > 0) { // Click near top edge (wall between gy-1 and gy)
			wallKey = `${gx},${gy},${gx + 1},${gy}`; // Horizontal wall above
			wallType = 'horizontal';
		} else if (yRem > cellSize - wallMargin && gy < height - 1) { // Click near bottom edge (wall between gy and gy+1)
			wallKey = `${gx},${gy + 1},${gx + 1},${gy + 1}`; // Horizontal wall below
			wallType = 'horizontal';
		}

		if (wallKey) {
			// Ensure the coordinates in the wall key are ordered consistently (x1<=x2, y1<=y2 might be safer if format allows variability)
			// Current format `${x1},${y1},${x2},${y2}` seems fixed by generation logic.

			if (permanentWalls.has(wallKey)) {
				setStatusMessage('Нельзя изменить постоянную стену. ' + getHint('canvasLeftClickEditMode', true));
				logger.log_wall("Попытка изменить постоянную стену: " + wallKey);
			} else {
				setWalls(prevWalls => {
					const newWalls = new Set(prevWalls);
					if (newWalls.has(wallKey)) {
						newWalls.delete(wallKey);
						setStatusMessage('Стена удалена. ' + getHint('canvasLeftClickEditMode', true));
						logger.log_wall_removed(wallKey);
					} else {
						newWalls.add(wallKey);
						setStatusMessage('Стена поставлена. ' + getHint('canvasLeftClickEditMode', true));
						logger.log_wall_added(wallKey);
					}
					return newWalls;
				});
			}
		} else {
			// Click is inside the cell, handle painting/clearing
			const cellKey = `${gx},${gy}`;
			setColoredCells(prevColored => {
				const newColored = new Set(prevColored);
				if (newColored.has(cellKey)) {
					newColored.delete(cellKey);
					setStatusMessage('Клетка очищена! ' + getHint('canvasLeftClickEditMode', true));
					logger.log_cell_cleared(cellKey);
				} else {
					newColored.add(cellKey);
					setStatusMessage('Клетка закрашена! ' + getHint('canvasLeftClickEditMode', true));
					logger.log_cell_painted(cellKey);
				}
				return newColored;
			});
		}
	}, [cellSize, width, height, permanentWalls, setWalls, setColoredCells, setStatusMessage]);

	/**
	 * Обработчик нажатия левой кнопки мыши на canvas.
	 * @param {MouseEvent} e - Событие мыши.
	 */
	const handleMouseDown = useCallback((e) => {
		if (e.button !== 0) return; // Only handle left clicks
		e.preventDefault();
		// e.stopPropagation(); // Might prevent other desired behaviors, use cautiously

		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvasPixels(x, y)) {
			// Click was outside the logical canvas area or off the element
			// setStatusMessage('Клик за пределами поля.'); // Avoid noisy messages for clicks outside
			return;
		}

		const {gridX, gridY} = toGridCoords(x, y);

		if (!editMode) {
			// If not in edit mode, maybe allow selecting the robot?
			// For now, just provide feedback.
			setStatusMessage(getHint('canvasLeftClickNoEdit', false));
			logger.log_event('Клик на поле вне режима редактирования.');
			return;
		}

		// In Edit Mode
		if (gridX === robotPos.x && gridY === robotPos.y) {
			// Clicked on the robot: start dragging
			setIsDraggingRobot(true);
			dragStartRef.current = {...robotPos}; // Store starting position for logging
			setStatusMessage('Перетаскивание робота...');
			logger.log_robot_drag_start(robotPos);
			// Make canvas less sensitive during drag? Optional.
			// canvasRef.current.style.cursor = 'grabbing';
		} else {
			// Clicked on the field (wall or cell): handle editing
			handleWallsAndCells(gridX, gridY, x, y);
		}
	}, [editMode, robotPos, getCanvasCoords, isOutsideCanvasPixels, toGridCoords, setStatusMessage, handleWallsAndCells, setIsDraggingRobot]);

	/**
	 * Обработчик движения мыши при перетаскивании робота.
	 * @param {MouseEvent} e - Событие мыши.
	 */
	const handleMouseMove = useCallback((e) => {
		if (!isDraggingRobot) return;
		e.preventDefault();
		// e.stopPropagation();

		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null) {
			// Moved cursor off the canvas while dragging, potentially stop drag?
			// Or just keep last valid position? For now, do nothing.
			return;
		}

		const {gridX, gridY} = toGridCoords(x, y);

		// Update position only if it changes to avoid unnecessary re-renders/logs
		if (gridX !== robotPos.x || gridY !== robotPos.y) {
			setRobotPos({x: gridX, y: gridY});
			// Logging during move removed as requested. Logging only happens on drag end.
			// setStatusMessage(`Перемещение в (${gridX}, ${gridY})`); // Optional: Live feedback
		}
	}, [isDraggingRobot, getCanvasCoords, toGridCoords, setRobotPos, robotPos]); // Added robotPos dependency for comparison

	/**
	 * Обработчик отпускания кнопки мыши. Завершает перетаскивание.
	 * @param {MouseEvent} e - Событие мыши.
	 */
	const handleMouseUp = useCallback((e) => {
		if (!isDraggingRobot) return;
		if (e.button !== 0) return; // Ensure it's the left button release

		e.preventDefault();
		// e.stopPropagation();

		setIsDraggingRobot(false);
		setStatusMessage('Перемещение робота завершено.');
		// Log the final position AFTER the drag ends.
		// Note: robotPos might have already been updated by the last mouseMove.
		logger.log_robot_drag_end(robotPos);
		// Restore cursor if changed
		// if (canvasRef.current) canvasRef.current.style.cursor = '';
	}, [isDraggingRobot, setStatusMessage, robotPos, setIsDraggingRobot]);

	/**
	 * Обработчик правого клика на canvas (для маркеров).
	 * @param {MouseEvent} e - Событие мыши.
	 */
	const handleCanvasRightClick = useCallback((e) => {
		e.preventDefault(); // Prevent browser context menu
		// e.stopPropagation();

		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvasPixels(x, y)) {
			// setStatusMessage('Правый клик за пределами поля.'); // Avoid noise
			return;
		}

		if (!editMode) {
			setStatusMessage(getHint('canvasRightClickNoEdit', false));
			logger.log_event('Правый клик на поле вне режима редактирования.');
			return;
		}

		// In Edit Mode: Place/Remove Marker
		const {gridX, gridY} = toGridCoords(x, y);
		const posKey = `${gridX},${gridY}`;

		setMarkers(prevMarkers => {
			const newMarkers = {...prevMarkers};
			if (newMarkers[posKey]) {
				// Marker exists, remove it
				delete newMarkers[posKey];
				setStatusMessage('Маркер убран. ' + getHint('canvasRightClickEditMode', true));
				logger.log_canvas_marker_removed(posKey);
			} else {
				// Marker doesn't exist, add it
				newMarkers[posKey] = 1; // Value could be anything truthy, 1 is simple
				setStatusMessage('Маркер добавлен! ' + getHint('canvasRightClickEditMode', true));
				logger.log_canvas_marker_added(posKey);
			}
			return newMarkers;
		});
	}, [editMode, getCanvasCoords, isOutsideCanvasPixels, toGridCoords, setMarkers, setStatusMessage]);


	/**
	 * Обработчик прокрутки колеса мыши для масштабирования (изменения cellSize).
	 * @param {WheelEvent} e - Событие колеса мыши.
	 */
	const handleWheel = useCallback((e) => {
		e.preventDefault(); // Prevent page scrolling
		// e.stopPropagation();

		const delta = Math.sign(e.deltaY); // -1 for wheel up (zoom in), 1 for wheel down (zoom out)
		const zoomFactor = 1.1;
		const minCellSize = 10;
		const maxCellSize = 200;

		let newCellSize;
		if (delta < 0) { // Zoom In
			newCellSize = Math.min(maxCellSize, Math.round(cellSize * zoomFactor));
			if (newCellSize > cellSize) { // Only update if size actually increased
				setStatusMessage(getHint('wheelZoomIn'));
				logger.log_event(`Масштаб увеличен (cellSize: ${newCellSize})`);
			} else {
				setStatusMessage(`Достигнут максимальный масштаб.`);
				return; // No change
			}
		} else { // Zoom Out
			newCellSize = Math.max(minCellSize, Math.round(cellSize / zoomFactor));
			if (newCellSize < cellSize) { // Only update if size actually decreased
				setStatusMessage(getHint('wheelZoomOut'));
				logger.log_event(`Масштаб уменьшен (cellSize: ${newCellSize})`);
			} else {
				setStatusMessage(`Достигнут минимальный масштаб.`);
				return; // No change
			}
		}
		setCellSize(newCellSize);

	}, [cellSize, setCellSize, setStatusMessage]); // Dependencies for zoom handler

	// Effect to add/remove global listeners for mouse move/up during drag
	useEffect(() => {
		if (isDraggingRobot) {
			// Add listeners to the window to capture mouse events even outside the canvas
			window.addEventListener('mousemove', handleMouseMove);
			window.addEventListener('mouseup', handleMouseUp);

			// Cleanup function
			return () => {
				window.removeEventListener('mousemove', handleMouseMove);
				window.removeEventListener('mouseup', handleMouseUp);
				// Restore cursor if needed
				// if (canvasRef.current) canvasRef.current.style.cursor = '';
			};
		}
		// No cleanup needed if not dragging
		return undefined;
	}, [isDraggingRobot, handleMouseMove, handleMouseUp]);

	return (
		<div className="field-area">
			<Card className="field-card" elevation={3}>
				<canvas
					ref={canvasRef}
					// Set logical width/height based on state
					width={width * cellSize}
					height={height * cellSize}
					// CSS class controls visual appearance/cursor
					className={`robot-canvas ${editMode ? 'edit-mode' : ''} ${isDraggingRobot ? 'dragging' : ''}`}
					onMouseDown={handleMouseDown}
					onContextMenu={handleCanvasRightClick}
					onWheel={handleWheel} // Add wheel handler for zooming
					style={{ // Ensure canvas scales visually within its container
						display: 'block', // Avoid extra space below canvas
						maxWidth: '100%',
						maxHeight: '100%', // Adjust as needed based on layout
						width: 'auto', // Let aspect ratio determine size
						height: 'auto',
						cursor: editMode ? (isDraggingRobot ? 'grabbing' : 'crosshair') : 'default', // Dynamic cursor
						// backgroundColor: '#f0f0f0' // Optional background
					}}
				/>
			</Card>
			{/* Status display moved below the canvas */}
			<Card className="status-card" elevation={2}>
				<Typography variant="body2" component="pre" className="status-text">
					{statusMessage || ' '} {/* Ensure pre doesn't collapse if message is empty */}
				</Typography>
			</Card>
		</div>
	);
});

export default Field;