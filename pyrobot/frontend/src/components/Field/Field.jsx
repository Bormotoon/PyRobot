import React, {memo, useCallback, useEffect, useState} from 'react';
import {Card, Typography} from '@mui/material';
import {drawField} from '../canvasDrawing';
import {getHint} from '../hints';
import './Field.css';

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
	                    statusMessage,    // Динамические подсказки (например, "Стена поставлена", "Клик за пределами поля")
	                    setStatusMessage,
                    }) => {
	const [isDraggingRobot, setIsDraggingRobot] = useState(false);

	useEffect(() => {
		if (!canvasRef.current) return;
		drawField(canvasRef.current, {
			coloredCells,
			robotPos,
			markers,
			walls,
			permanentWalls,
			width,
			height,
			cellSize,
		});
	}, [canvasRef, coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize]);

	const getCanvasCoords = useCallback((event) => {
		const canvas = canvasRef.current;
		if (!canvas) return {x: null, y: null};
		const rect = canvas.getBoundingClientRect();
		const scaleX = canvas.width / rect.width;
		const scaleY = canvas.height / rect.height;
		const x = (event.clientX - rect.left) * scaleX;
		const y = (event.clientY - rect.top) * scaleY;
		return {x, y};
	}, [canvasRef]);

	const isOutsideCanvas = useCallback((px, py) => {
		return px < 0 || py < 0 || px >= width * cellSize || py >= height * cellSize;
	}, [width, height, cellSize]);

	const toGridCoords = useCallback((px, py) => {
		let gx = Math.floor(px / cellSize);
		let gy = Math.floor(py / cellSize);
		gx = Math.min(Math.max(gx, 0), width - 1);
		gy = Math.min(Math.max(gy, 0), height - 1);
		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	// Обработка взаимодействия со стенами/клетками
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
					} else {
						copy.add(wall);
						setStatusMessage('Стена поставлена. ' + getHint('canvasLeftClickEditMode', true));
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
				} else {
					c.add(posKey);
					setStatusMessage('Клетка закрашена! ' + getHint('canvasLeftClickEditMode', true));
				}
				return c;
			});
		}
	}, [cellSize, permanentWalls, setWalls, setColoredCells, setStatusMessage]);

	const handleMouseDown = useCallback((e) => {
		if (e.button !== 0) return; // только левая кнопка
		e.preventDefault();
		e.stopPropagation();
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvas(x, y)) {
			setStatusMessage('Клик за пределами поля.');
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
			return;
		}
		// Вызываем функцию обработки стен/клеток
		handleWallsAndCells(gridX, gridY, x, y);
	}, [editMode, robotPos, getCanvasCoords, isOutsideCanvas, toGridCoords, setStatusMessage, handleWallsAndCells]);

	const handleMouseMove = useCallback((e) => {
		if (!isDraggingRobot) return;
		e.preventDefault();
		e.stopPropagation();
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvas(x, y)) return;
		const {gridX, gridY} = toGridCoords(x, y);
		setRobotPos({x: gridX, y: gridY});
	}, [isDraggingRobot, getCanvasCoords, toGridCoords, setRobotPos, isOutsideCanvas]);

	const handleMouseUp = useCallback((e) => {
		if (!isDraggingRobot) return;
		e.preventDefault();
		e.stopPropagation();
		setIsDraggingRobot(false);
		setStatusMessage('Перемещение робота завершено.');
	}, [isDraggingRobot, setStatusMessage]);

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
			} else {
				delete copy[posKey];
				setStatusMessage('Маркер убран. ' + getHint('canvasRightClickEditMode', true));
			}
			return copy;
		});
	}, [editMode, getCanvasCoords, isOutsideCanvas, toGridCoords, setMarkers, setStatusMessage]);

	return (
		<div className="field-area">
			<Card className="field-card">
				<canvas
					ref={canvasRef}
					width={width * cellSize}
					height={height * cellSize}
					className={editMode ? 'edit-mode' : ''}
					onMouseDown={handleMouseDown}
					onMouseMove={handleMouseMove}
					onMouseUp={handleMouseUp}
					onContextMenu={handleCanvasRightClick}
				/>
			</Card>

			{/* Под полем отображаются только динамические подсказки */}
			<Card className="status-card">
				<Typography variant="body2" className="status-text">
					{statusMessage}
				</Typography>
			</Card>
		</div>
	);
});

export default Field;
