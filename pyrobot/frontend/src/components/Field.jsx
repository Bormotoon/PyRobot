/**
 * Field.jsx
 *
 * Данный компонент отвечает за отображение Canvas (поля) и обработку взаимодействия:
 * - Рисование стен при включённом editMode (левый клик по границе клетки)
 * - Раскраска клеток (левый клик внутри клетки)
 * - Перетаскивание робота (зажать левую кнопку на роботе и двигать)
 * - Ставить/убирать маркер (правый клик)
 * - Зумировать (колёсико мыши)
 *
 * Он также отображает карточку со статусной информацией (позиция робота, количество маркеров и т.д.).
 */

import React, {useCallback, useEffect, useState} from 'react';
import {Card, Typography} from '@mui/material';
import {drawField} from '../canvasDrawing';

/**
 * Компонент Field.
 * @param {Object} props - Пропсы с состоянием и коллбэками для управления логикой поля и робота.
 * @returns {JSX.Element} Разметка поля (Canvas) и блока статуса.
 */
function Field({
	               canvasRef,
	               robotPos,
	               walls,
	               permanentWalls,
	               coloredCells,
	               markers,
	               width,
	               height,
	               cellSize,
	               editMode,
	               setRobotPos,
	               setWalls,
	               setMarkers,
	               setColoredCells,
	               setStatusMessage,
	               setCellSize
               }) {
	/**
	 * Локальное состояние: флаг, перетаскивается ли сейчас робот.
	 */
	const [isDraggingRobot, setIsDraggingRobot] = useState(false);

	/**
	 * Вызываем drawField при каждом изменении зависимостей.
	 */
	useEffect(() => {
		const canvas = canvasRef.current;
		if (!canvas) return;
		drawField(canvas, {
			coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize
		});
	}, [canvasRef, robotPos, walls, permanentWalls, coloredCells, markers, width, height, cellSize]);

	/**
	 * Функция getCanvasCoords(event)
	 * Возвращает координаты мыши внутри canvas.
	 */
	const getCanvasCoords = useCallback((event) => {
		const canvas = canvasRef.current;
		if (!canvas) return {x: null, y: null};
		const rect = canvas.getBoundingClientRect();
		return {
			x: event.clientX - rect.left, y: event.clientY - rect.top
		};
	}, [canvasRef]);

	/**
	 * Функция toGridCoords(px, py)
	 * Перевод пиксельных координат (Canvas) в координаты сетки (gridX, gridY).
	 */
	const toGridCoords = useCallback((px, py) => {
		const gx = Math.floor(px / cellSize) - 1;
		const gy = Math.floor(py / cellSize) - 1;
		if (gx < 0 || gx >= width || gy < 0 || gy >= height) {
			return {gridX: null, gridY: null};
		}
		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	/**
	 * handleCanvasLeftClickEditMode(px, py)
	 * Логика левого клика в режиме рисования:
	 * - Ставим/убираем стену, если попали в границу клетки
	 * - Красим/очищаем клетку, если клик внутри клетки
	 */
	const handleCanvasLeftClickEditMode = useCallback((px, py) => {
		const gridX = Math.floor(px / cellSize) - 1;
		const gridY = Math.floor(py / cellSize) - 1;
		if (gridX < 0 || gridX >= width || gridY < 0 || gridY >= height) {
			setStatusMessage('Клик за пределами поля рисования.');
			return;
		}

		const margin = 5;
		const xRemainder = px % cellSize;
		const yRemainder = py % cellSize;
		let wall = null;

		// Проверяем, не попали ли вблизи левой или правой границы клетки
		if (xRemainder < margin) {
			wall = `${gridX},${gridY},${gridX},${gridY + 1}`;
		} else if (xRemainder > cellSize - margin) {
			wall = `${gridX + 1},${gridY},${gridX + 1},${gridY + 1}`;
		} else if (yRemainder < margin) {
			// Верхняя граница
			wall = `${gridX},${gridY},${gridX + 1},${gridY}`;
		} else if (yRemainder > cellSize - margin) {
			// Нижняя граница
			wall = `${gridX},${gridY + 1},${gridX + 1},${gridY + 1}`;
		}

		// Если клик на границе — стена
		if (wall) {
			// Если это не постоянная (граничная) стена
			if (!permanentWalls.has(wall)) {
				setWalls(prev => {
					const clone = new Set(prev);
					if (clone.has(wall)) {
						clone.delete(wall);
						setStatusMessage('Стена удалена.');
					} else {
						clone.add(wall);
						setStatusMessage('Стена поставлена.');
					}
					return clone;
				});
			} else {
				setStatusMessage('Это постоянная стена, её убрать нельзя.');
			}
		} else {
			// Иначе считаем, что клик внутри клетки => красим/очищаем клетку
			const posKey = `${gridX},${gridY}`;
			setColoredCells(prev => {
				const clone = new Set(prev);
				if (clone.has(posKey)) {
					clone.delete(posKey);
					setStatusMessage('Клетка очищена от краски!');
				} else {
					clone.add(posKey);
					setStatusMessage('Клетка раскрашена!');
				}
				return clone;
			});
		}
	}, [cellSize, permanentWalls, width, height, setWalls, setColoredCells, setStatusMessage]);

	/**
	 * handleMouseDown — левый клик на Canvas
	 * Может начать перетаскивание робота или рисовать стены/закрашивать клетку (editMode).
	 */
	const handleMouseDown = useCallback((e) => {
		if (e.button !== 0) return; // только левая кнопка
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null) return;

		const {gridX, gridY} = toGridCoords(x, y);
		if (gridX === null || gridY === null) {
			setStatusMessage('Клик за пределами поля.');
			return;
		}

		// Если режим рисования включён
		if (editMode) {
			// Если клик по роботу — начинаем перетаскивание
			if (gridX === robotPos.x && gridY === robotPos.y) {
				setIsDraggingRobot(true);
				setStatusMessage('Перетаскивание робота начато.');
			} else {
				// Иначе — ставим/убираем стены или красим клетку
				handleCanvasLeftClickEditMode(x, y);
			}
		} else {
			setStatusMessage('Режим рисования не включён.');
		}
	}, [editMode, robotPos, getCanvasCoords, toGridCoords, setStatusMessage, handleCanvasLeftClickEditMode]);

	/**
	 * handleMouseMove — если идёт перетаскивание робота, обновляем позицию.
	 */
	const handleMouseMove = useCallback((e) => {
		if (!isDraggingRobot) return;
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null) return;

		const {gridX, gridY} = toGridCoords(x, y);
		if (gridX === null || gridY === null) {
			setStatusMessage('Робот не выйдет за границы.');
			return;
		}
		const newX = Math.min(Math.max(gridX, 0), width - 1);
		const newY = Math.min(Math.max(gridY, 0), height - 1);
		setRobotPos({x: newX, y: newY});
	}, [isDraggingRobot, getCanvasCoords, toGridCoords, setStatusMessage, setRobotPos, width, height]);

	/**
	 * handleMouseUp — завершаем перетаскивание робота, если было.
	 */
	const handleMouseUp = useCallback(() => {
		if (isDraggingRobot) {
			setIsDraggingRobot(false);
			setStatusMessage('Перетаскивание робота завершено.');
		}
	}, [isDraggingRobot, setStatusMessage]);

	/**
	 * handleCanvasRightClick — при правом клике ставим/убираем маркер (если editMode).
	 */
	const handleCanvasRightClick = useCallback((e) => {
		e.preventDefault();
		if (!editMode) {
			setStatusMessage('Правый клик — режим рисования не включён.');
			return;
		}
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null) return;

		const {gridX, gridY} = toGridCoords(x, y);
		if (gridX === null || gridY === null) {
			setStatusMessage('Правый клик за пределами поля.');
			return;
		}

		const posKey = `${gridX},${gridY}`;
		setMarkers(prev => {
			const clone = {...prev};
			if (!clone[posKey]) {
				clone[posKey] = 1;
				setStatusMessage('Маркер добавлен!');
			} else {
				delete clone[posKey];
				setStatusMessage('Маркер убран.');
			}
			return clone;
		});
	}, [editMode, getCanvasCoords, toGridCoords, setMarkers, setStatusMessage]);

	/**
	 * handleCanvasWheel — меняем cellSize при прокрутке колёсика.
	 */
	const handleCanvasWheel = useCallback((e) => {
		e.preventDefault();
		setCellSize(prev => {
			const newSize = Math.max(10, prev + (e.deltaY > 0 ? -5 : 5));
			return newSize;
		});
	}, [setCellSize]);

	return (<div className="field-area">
			<Card className="card-controls">
				<div className="field-container">
					<div className="canvas-wrapper">
						<canvas
							ref={canvasRef}
							width={(width + 2) * cellSize}
							height={(height + 2) * cellSize}
							className={editMode ? 'edit-mode' : ''}
							onMouseDown={handleMouseDown}
							onMouseMove={handleMouseMove}
							onMouseUp={handleMouseUp}
							onContextMenu={handleCanvasRightClick}
							onWheel={handleCanvasWheel}
						/>
					</div>
				</div>
			</Card>

			<Card className="status-card">
				<Typography variant="body2">
					Позиция робота: ({robotPos.x}, {robotPos.y})
				</Typography>
				<Typography variant="body2" style={{marginTop: 8}}>
					Маркеров на поле: {Object.keys(markers).length} <br/>
					Раскрашенных клеток: {coloredCells.size}
				</Typography>
			</Card>
		</div>);
}

export default Field;
