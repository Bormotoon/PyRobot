/**
 * @file Field.jsx
 * @description Компонент игрового поля симулятора робота.
 * Отвечает за визуализацию поля, робота, стен, маркеров и окрашенных клеток с использованием canvas.
 * Обрабатывает события мыши для редактирования поля (установка/удаление стен, окраска клеток, перетаскивание робота).
 */

import React, {memo, useCallback, useEffect, useState} from 'react';
import {Card, Typography} from '@mui/material';
import {drawField} from '../canvasDrawing';
import {getHint} from '../hints';
import './Field.css';
// Импорт логгера из Logger.js (путь обновлён)
import logger from '../../Logger';

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
	                    editMode,
	                    statusMessage,
	                    setStatusMessage,
                    }) => {
	const [isDraggingRobot, setIsDraggingRobot] = useState(false);

	// Перерисовка поля при изменении зависимостей
	useEffect(() => {
		if (!canvasRef.current) return;
		drawField(canvasRef.current, {coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize});
	}, [canvasRef, coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize]);

	// Глобальное отслеживание событий мыши для перетаскивания робота
	useEffect(() => {
		if (isDraggingRobot) {
			window.addEventListener('mousemove', handleMouseMove);
			window.addEventListener('mouseup', handleMouseUp);
			return () => {
				window.removeEventListener('mousemove', handleMouseMove);
				window.removeEventListener('mouseup', handleMouseUp);
			};
		}
	}, [isDraggingRobot]);

	/**
	 * Получает координаты курсора относительно canvas.
	 * @param {MouseEvent} event - Событие мыши.
	 * @returns {Object} Объект с координатами {x, y} или {x: null, y: null}, если canvas недоступен.
	 */
	const getCanvasCoords = useCallback((event) => {
		const canvas = canvasRef.current;
		if (!canvas) return {x: null, y: null};
		const rect = canvas.getBoundingClientRect();
		const canvasAspect = canvas.width / canvas.height;
		const rectAspect = rect.width / rect.height;
		let offsetX = event.clientX - rect.left;
		let offsetY = event.clientY - rect.top;
		let scaleX, scaleY;
		if (rectAspect > canvasAspect) {
			const effectiveWidth = rect.height * canvasAspect;
			const marginX = (rect.width - effectiveWidth) / 2;
			offsetX = Math.max(0, offsetX - marginX);
			offsetX = Math.min(offsetX, effectiveWidth);
			scaleX = canvas.width / effectiveWidth;
			scaleY = canvas.height / rect.height;
		} else if (rectAspect < canvasAspect) {
			const effectiveHeight = rect.width / canvasAspect;
			const marginY = (rect.height - effectiveHeight) / 2;
			offsetY = Math.max(0, offsetY - marginY);
			offsetY = Math.min(offsetY, effectiveHeight);
			scaleX = canvas.width / rect.width;
			scaleY = canvas.height / effectiveHeight;
		} else {
			scaleX = canvas.width / rect.width;
			scaleY = canvas.height / rect.height;
		}
		return {x: offsetX * scaleX, y: offsetY * scaleY};
	}, [canvasRef]);

	/**
	 * Проверяет, находится ли точка за пределами игрового поля.
	 * @param {number} px - Координата X.
	 * @param {number} py - Координата Y.
	 * @returns {boolean} Истина, если точка за пределами.
	 */
	const isOutsideCanvas = useCallback((px, py) => {
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
		gx = Math.min(Math.max(gx, 0), width - 1);
		gy = Math.min(Math.max(gy, 0), height - 1);
		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	/**
	 * Обрабатывает клики по canvas для установки/удаления стен или окраски клеток.
	 * @param {number} gx - Координата X ячейки.
	 * @param {number} gy - Координата Y ячейки.
	 * @param {number} px - Точная координата X.
	 * @param {number} py - Точная координата Y.
	 */
	const handleWallsAndCells = useCallback((gx, gy, px, py) => {
		const margin = 5;
		const xRem = px % cellSize;
		const yRem = py % cellSize;
		let wall = null;
		if (xRem < margin) {
			wall = `${gx},${gy},${gx},${gy + 1}`;
		} else if (xRem > cellSize - margin) {
			wall = `${gx + 1},${gy},${gx + 1},${gy + 1}`;
		} else if (yRem < margin) {
			wall = `${gx},${gy},${gx + 1},${gy}`;
		} else if (yRem > cellSize - margin) {
			wall = `${gx},${gy + 1},${gx + 1},${gy + 1}`;
		}
		if (wall) {
			if (!permanentWalls.has(wall)) {
				setWalls(prev => {
					const copy = new Set(prev);
					if (copy.has(wall)) {
						copy.delete(wall);
						setStatusMessage('Стена удалена. ' + getHint('canvasLeftClickEditMode', true));
						logger.log_wall_removed(wall);
					} else {
						copy.add(wall);
						setStatusMessage('Стена поставлена. ' + getHint('canvasLeftClickEditMode', true));
						logger.log_wall_added(wall);
					}
					return copy;
				});
			} else {
				setStatusMessage('Это постоянная стена. ' + getHint('canvasLeftClickEditMode', true));
			}
		} else {
			const posKey = `${gx},${gy}`;
			setColoredCells(prev => {
				const c = new Set(prev);
				if (c.has(posKey)) {
					c.delete(posKey);
					setStatusMessage('Клетка очищена! ' + getHint('canvasLeftClickEditMode', true));
					logger.log_cell_cleared(posKey);
				} else {
					c.add(posKey);
					setStatusMessage('Клетка закрашена! ' + getHint('canvasLeftClickEditMode', true));
					logger.log_cell_painted(posKey);
				}
				return c;
			});
		}
	}, [cellSize, permanentWalls, setWalls, setColoredCells, setStatusMessage]);

	/**
	 * Обработчик нажатия кнопки мыши на canvas.
	 * @param {MouseEvent} e - Событие мыши.
	 */
	const handleMouseDown = useCallback((e) => {
		if (e.button !== 0) return;
		e.preventDefault();
		e.stopPropagation();
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvas(x, y)) {
			setStatusMessage('Клик за пределами поля.');
			logger.log_error('Клик за пределами поля.');
			return;
		}
		if (!editMode) {
			setStatusMessage(getHint('canvasLeftClickNoEdit', false));
			return;
		}
		const {gridX, gridY} = toGridCoords(x, y);
		if (gridX === robotPos.x && gridY === robotPos.y) {
			setIsDraggingRobot(true);
			setStatusMessage('Начали перетаскивать робота.');
			logger.log_robot_drag_start();
			return;
		}
		handleWallsAndCells(gridX, gridY, x, y);
	}, [editMode, robotPos, getCanvasCoords, isOutsideCanvas, toGridCoords, setStatusMessage, handleWallsAndCells]);

	/**
	 * Обработчик движения мыши при перетаскивании робота.
	 * Логирование обновления позиции убрано, чтобы записывать состояние только при отпускании кнопки.
	 * @param {MouseEvent} e - Событие мыши.
	 */
	const handleMouseMove = useCallback((e) => {
		if (!isDraggingRobot) return;
		e.preventDefault();
		e.stopPropagation();
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null) return;
		const {gridX, gridY} = toGridCoords(x, y);
		setRobotPos({x: gridX, y: gridY});
		// Убрано: logger.log_robot_drag_update({ x: gridX, y: gridY });
	}, [isDraggingRobot, getCanvasCoords, toGridCoords, setRobotPos]);

	/**
	 * Обработчик отпускания кнопки мыши.
	 * Записывает финальное состояние перетаскивания в лог.
	 * @param {MouseEvent} e - Событие мыши.
	 */
	const handleMouseUp = useCallback((e) => {
		if (!isDraggingRobot) return;
		e.preventDefault();
		e.stopPropagation();
		setIsDraggingRobot(false);
		setStatusMessage('Перемещение робота завершено.');
		logger.log_robot_drag_end(robotPos);
	}, [isDraggingRobot, setStatusMessage, robotPos]);

	/**
	 * Обработчик правого клика на canvas.
	 * @param {MouseEvent} e - Событие мыши.
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
		setMarkers(prev => {
			const copy = {...prev};
			if (!copy[posKey]) {
				copy[posKey] = 1;
				setStatusMessage('Маркер добавлен! ' + getHint('canvasRightClickEditMode', true));
				logger.log_canvas_marker_added(posKey);
			} else {
				delete copy[posKey];
				setStatusMessage('Маркер убран. ' + getHint('canvasRightClickEditMode', true));
				logger.log_canvas_marker_removed(posKey);
			}
			return copy;
		});
	}, [editMode, getCanvasCoords, isOutsideCanvas, toGridCoords, setMarkers, setStatusMessage]);

	return (<div className="field-area">
			<Card className="field-card">
				<canvas
					ref={canvasRef}
					width={width * cellSize}
					height={height * cellSize}
					className={editMode ? 'edit-mode' : ''}
					onMouseDown={handleMouseDown}
					onContextMenu={handleCanvasRightClick}
				/>
			</Card>
			<Card className="status-card">
				<Typography variant="body2" className="status-text">
					{statusMessage}
				</Typography>
			</Card>
		</div>);
});

export default Field;
