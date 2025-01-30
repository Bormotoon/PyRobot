import React, {memo, useCallback, useEffect, useState} from 'react';
import {Card, Typography} from '@mui/material';
import {drawField} from '../canvasDrawing';
import {getHint} from '../hints';
import './Field.css';

const Field = memo(({
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
	                    statusMessage,
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
	}, [
		canvasRef,
		coloredCells,
		robotPos,
		markers,
		walls,
		permanentWalls,
		width,
		height,
		cellSize,
	]);

	const getCanvasCoords = useCallback((event) => {
		const canvas = canvasRef.current;
		if (!canvas) return {x: null, y: null};
		const rect = canvas.getBoundingClientRect();
		return {
			x: event.clientX - rect.left,
			y: event.clientY - rect.top,
		};
	}, [canvasRef]);

	const toGridCoords = useCallback((px, py) => {
		const gx = Math.floor(px / cellSize) - 1;
		const gy = Math.floor(py / cellSize) - 1;
		if (gx < 0 || gx >= width || gy < 0 || gy >= height) {
			return {gridX: null, gridY: null};
		}
		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	const handleCanvasLeftClickEditMode = useCallback(
		(px, py) => {
			const margin = 5;
			const gridX = Math.floor(px / cellSize) - 1;
			const gridY = Math.floor(py / cellSize) - 1;

			if (
				gridX == null ||
				gridY == null ||
				gridX < 0 ||
				gridX >= width ||
				gridY < 0 ||
				gridY >= height
			) {
				setStatusMessage('Клик за пределами поля рисования.');
				return;
			}

			const xRem = px % cellSize;
			const yRem = py % cellSize;
			let wall = null;

			if (xRem < margin) {
				wall = `${gridX},${gridY},${gridX},${gridY + 1}`;
			} else if (xRem > cellSize - margin) {
				wall = `${gridX + 1},${gridY},${gridX + 1},${gridY + 1}`;
			} else if (yRem < margin) {
				wall = `${gridX},${gridY},${gridX + 1},${gridY}`;
			} else if (yRem > cellSize - margin) {
				wall = `${gridX},${gridY + 1},${gridX + 1},${gridY + 1}`;
			}

			if (wall) {
				if (!permanentWalls.has(wall)) {
					setWalls((prev) => {
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
				const posKey = `${gridX},${gridY}`;
				setColoredCells((prev) => {
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
		},
		[
			cellSize,
			width,
			height,
			permanentWalls,
			setWalls,
			setColoredCells,
			setStatusMessage,
		]
	);

	const handleMouseDown = useCallback(
		(e) => {
			if (e.button !== 0) return;
			const {x, y} = getCanvasCoords(e);
			if (x === null || y === null) return;

			const {gridX, gridY} = toGridCoords(x, y);
			if (gridX === null || gridY === null) {
				setStatusMessage('Клик за пределами поля.');
				return;
			}

			if (!editMode) {
				setStatusMessage(getHint('canvasLeftClickNoEdit', false));
				return;
			}

			if (gridX === robotPos.x && gridY === robotPos.y) {
				setIsDraggingRobot(true);
				setStatusMessage('Перетаскивание робота (стены игнорируются).');
			} else {
				handleCanvasLeftClickEditMode(x, y);
			}
		},
		[
			editMode,
			robotPos,
			getCanvasCoords,
			toGridCoords,
			handleCanvasLeftClickEditMode,
			setStatusMessage,
		]
	);

	const handleMouseMove = useCallback(
		(e) => {
			if (!isDraggingRobot) return;
			const {x, y} = getCanvasCoords(e);
			if (x === null || y === null) return;

			const {gridX, gridY} = toGridCoords(x, y);
			if (gridX === null || gridY === null) {
				setStatusMessage('Робот не выйдет за границы поля.');
				return;
			}

			const newX = Math.min(Math.max(gridX, 0), width - 1);
			const newY = Math.min(Math.max(gridY, 0), height - 1);
			setRobotPos({x: newX, y: newY});
		},
		[
			isDraggingRobot,
			getCanvasCoords,
			toGridCoords,
			setStatusMessage,
			setRobotPos,
			width,
			height,
		]
	);

	const handleMouseUp = useCallback(() => {
		if (isDraggingRobot) {
			setIsDraggingRobot(false);
			setStatusMessage('Перетаскивание робота завершено.');
		}
	}, [isDraggingRobot, setStatusMessage]);

	const handleCanvasRightClick = useCallback(
		(e) => {
			e.preventDefault();
			if (!editMode) {
				setStatusMessage(getHint('canvasRightClickNoEdit', false));
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
			setMarkers((prev) => {
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
		},
		[editMode, getCanvasCoords, toGridCoords, setMarkers, setStatusMessage]
	);

	const displayString = `Позиция робота: (${robotPos.x}, ${robotPos.y})
Маркеров: ${Object.keys(markers).length}
Раскрашенных клеток: ${coloredCells.size}`;

	const finalString = statusMessage ? `${displayString}\n\n${statusMessage}` : displayString;

	return (
		<div className="field-area">
			<Card className="field-card">
				<canvas
					ref={canvasRef}
					width={(width + 2) * cellSize}
					height={(height + 2) * cellSize}
					className={editMode ? 'edit-mode' : ''}
					onMouseDown={handleMouseDown}
					onMouseMove={handleMouseMove}
					onMouseUp={handleMouseUp}
					onContextMenu={handleCanvasRightClick}
				/>
			</Card>
			<Card className="status-card">
				<Typography variant="body2">
					{finalString}
				</Typography>
			</Card>
		</div>
	);
});

export default Field;
