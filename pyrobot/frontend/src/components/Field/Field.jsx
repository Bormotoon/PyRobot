import React, {memo, useCallback, useEffect, useState, useRef} from 'react';
import {Card, Typography} from '@mui/material';
import {drawField} from '../canvasDrawing'; // Adjust path if needed
import {getHint} from '../hints'; // Adjust path if needed
import './Field.css';
import logger from '../../Logger'; // Adjust path if needed

const Field = memo(({
	                    canvasRef, robotPos, setRobotPos, walls, setWalls, permanentWalls,
	                    markers, setMarkers, coloredCells, setColoredCells,
	                    symbols, // Receive symbols prop
	                    // NO setSymbols prop needed
	                    width, height, cellSize, setCellSize, editMode,
	                    statusMessage, setStatusMessage,
                    }) => {
	const [isDraggingRobot, setIsDraggingRobot] = useState(false);
	// const dragStartRef = useRef({ x: 0, y: 0 }); // If needed for drag logic

	// <<< Add Prop Logging >>>
	// Use JSON.stringify with a replacer for complex objects/sets
	const propsToLog = JSON.stringify({
		symbols,
		width,
		height,
		cellSize,
		robotPos,
		editMode,
		walls: Array.from(walls),
		markers,
		coloredCells: Array.from(coloredCells)
	}, (key, value) => value instanceof Set ? Array.from(value) : value, 2);
	console.log('%cField Render - Received props:', 'color: green;', JSON.parse(propsToLog));
	// <<< ---------------- >>>

	// Effect for drawing
	useEffect(() => {
		if (!canvasRef.current) {
			console.error("Canvas Ref not available in Field useEffect.");
			return;
		}
		;
		// <<< Log data passed to drawField >>>
		const drawConfig = {coloredCells, robotPos, markers, symbols, walls, permanentWalls, width, height, cellSize};
		const configToLog = JSON.stringify(drawConfig, (key, value) => value instanceof Set ? Array.from(value) : value, 2);
		console.log('%cField useEffect - Calling drawField with config:', 'color: purple;', JSON.parse(configToLog));
		// <<< ----------------------------- >>>
		drawField(canvasRef.current, drawConfig); // Pass config object
	}, [ // Dependencies for redraw
		canvasRef, coloredCells, robotPos, markers, symbols, // Add symbols dependency
		walls, permanentWalls, width, height, cellSize
	]);


	// --- Handlers ---

	const getCanvasCoords = useCallback((event) => {
		// ... (implementation as before) ...
		const canvas = canvasRef.current;
		if (!canvas) return {x: null, y: null};
		const rect = canvas.getBoundingClientRect();
		const clientX = event.clientX;
		const clientY = event.clientY;
		const canvasX = clientX - rect.left;
		const canvasY = clientY - rect.top;
		const scaleX = canvas.width / rect.width;
		const scaleY = canvas.height / rect.height;
		const x = canvasX * scaleX;
		const y = canvasY * scaleY;
		if (x < 0 || x > canvas.width || y < 0 || y > canvas.height) {
			return {x: null, y: null};
		}
		return {x, y};
	}, [canvasRef]);

	const isOutsideCanvasPixels = useCallback((px, py) => {
		return px < 0 || py < 0 || px >= width * cellSize || py >= height * cellSize;
	}, [width, height, cellSize]);

	const toGridCoords = useCallback((px, py) => {
		let gx = Math.floor(px / cellSize);
		let gy = Math.floor(py / cellSize);
		gx = Math.min(Math.max(gx, 0), width - 1);
		gy = Math.min(Math.max(gy, 0), height - 1);
		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	const handleWallsAndCells = useCallback((gx, gy, px, py) => { /* ... (implementation as before, logging within if needed) ... */
		const wallMargin = Math.max(2, Math.min(8, cellSize * 0.1));
		const xRem = px % cellSize;
		const yRem = py % cellSize;
		let wallKey = null;
		if (xRem < wallMargin && gx > 0) {
			wallKey = `${gx},${gy},${gx},${gy + 1}`;
		} else if (xRem > cellSize - wallMargin && gx < width - 1) {
			wallKey = `${gx + 1},${gy},${gx + 1},${gy + 1}`;
		} else if (yRem < wallMargin && gy > 0) {
			wallKey = `${gx},${gy},${gx + 1},${gy}`;
		} else if (yRem > cellSize - wallMargin && gy < height - 1) {
			wallKey = `${gx},${gy + 1},${gx + 1},${gy + 1}`;
		}
		if (wallKey) {
			if (permanentWalls.has(wallKey)) {
				setStatusMessage('Постоянная стена.');
				logger.log_wall("Попытка изменить пост. стену: " + wallKey);
			} else {
				setWalls(prev => {
					const copy = new Set(prev);
					if (copy.has(wallKey)) {
						copy.delete(wallKey);
						setStatusMessage('Стена удалена.');
						logger.log_wall_removed(wallKey);
					} else {
						copy.add(wallKey);
						setStatusMessage('Стена поставлена.');
						logger.log_wall_added(wallKey);
					}
					return copy;
				});
			}
		} else {
			const cellKey = `${gx},${gy}`;
			setColoredCells(prev => {
				const c = new Set(prev);
				if (c.has(cellKey)) {
					c.delete(cellKey);
					setStatusMessage('Клетка очищена.');
					logger.log_cell_cleared(cellKey);
				} else {
					c.add(cellKey);
					setStatusMessage('Клетка закрашена.');
					logger.log_cell_painted(cellKey);
				}
				return c;
			});
		}
	}, [cellSize, width, height, permanentWalls, setWalls, setColoredCells, setStatusMessage]);

	const handleMouseDown = useCallback((e) => { /* ... (implementation as before, logging within if needed) ... */
		if (e.button !== 0) return;
		e.preventDefault();
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvasPixels(x, y)) {
			return;
		}
		const {gridX, gridY} = toGridCoords(x, y);
		if (!editMode) {
			setStatusMessage(getHint('canvasLeftClickNoEdit', false));
			logger.log_event('Клик вне ред. режима.');
			return;
		}
		if (gridX === robotPos.x && gridY === robotPos.y) {
			setIsDraggingRobot(true);
			setStatusMessage('Перетаскивание...');
			logger.log_robot_drag_start(robotPos);
		} else {
			handleWallsAndCells(gridX, gridY, x, y);
		}
	}, [editMode, robotPos, getCanvasCoords, isOutsideCanvasPixels, toGridCoords, setStatusMessage, handleWallsAndCells, setIsDraggingRobot]);

	const handleMouseMove = useCallback((e) => { /* ... (implementation as before, no logging during move) ... */
		if (!isDraggingRobot) return;
		e.preventDefault();
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null) return;
		const {gridX, gridY} = toGridCoords(x, y);
		if (gridX !== robotPos.x || gridY !== robotPos.y) {
			setRobotPos({x: gridX, y: gridY});
		}
	}, [isDraggingRobot, getCanvasCoords, toGridCoords, setRobotPos, robotPos]);

	const handleMouseUp = useCallback((e) => { /* ... (implementation as before, logs end pos) ... */
		if (!isDraggingRobot) return;
		if (e.button !== 0) return;
		e.preventDefault();
		setIsDraggingRobot(false);
		setStatusMessage('Перемещение завершено.');
		logger.log_robot_drag_end(robotPos);
	}, [isDraggingRobot, setStatusMessage, robotPos, setIsDraggingRobot]);

	const handleCanvasRightClick = useCallback((e) => { /* ... (implementation as before, logging within if needed) ... */
		e.preventDefault();
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvasPixels(x, y)) {
			return;
		}
		if (!editMode) {
			setStatusMessage(getHint('canvasRightClickNoEdit', false));
			logger.log_event('Правый клик вне ред. режима.');
			return;
		}
		const {gridX, gridY} = toGridCoords(x, y);
		const posKey = `${gridX},${gridY}`;
		setMarkers(prev => {
			const copy = {...prev};
			if (copy[posKey]) {
				delete copy[posKey];
				setStatusMessage('Маркер убран.');
				logger.log_canvas_marker_removed(posKey);
			} else {
				copy[posKey] = 1;
				setStatusMessage('Маркер добавлен.');
				logger.log_canvas_marker_added(posKey);
			}
			return copy;
		});
	}, [editMode, getCanvasCoords, isOutsideCanvasPixels, toGridCoords, setMarkers, setStatusMessage]);

	const handleWheel = useCallback((e) => { /* ... (implementation as before, logging within if needed) ... */
		e.preventDefault();
		const delta = Math.sign(e.deltaY);
		const zoomFactor = 1.1;
		const min = 10;
		const max = 200;
		let newSize;
		if (delta < 0) {
			newSize = Math.min(max, Math.round(cellSize * zoomFactor));
			if (newSize > cellSize) {
				setStatusMessage(getHint('wheelZoomIn'));
				logger.log_event(`Zoom+ (cell: ${newSize})`);
			} else {
				setStatusMessage(`Max zoom.`);
				return;
			}
		} else {
			newSize = Math.max(min, Math.round(cellSize / zoomFactor));
			if (newSize < cellSize) {
				setStatusMessage(getHint('wheelZoomOut'));
				logger.log_event(`Zoom- (cell: ${newSize})`);
			} else {
				setStatusMessage(`Min zoom.`);
				return;
			}
		}
		setCellSize(newSize);
	}, [cellSize, setCellSize, setStatusMessage]);

	// useEffect for window drag listeners
	useEffect(() => {
		if (isDraggingRobot) {
			window.addEventListener('mousemove', handleMouseMove);
			window.addEventListener('mouseup', handleMouseUp);
			return () => {
				window.removeEventListener('mousemove', handleMouseMove);
				window.removeEventListener('mouseup', handleMouseUp);
			};
		}
	}, [isDraggingRobot, handleMouseMove, handleMouseUp]);


	return (
		<div className="field-area">
			<Card className="field-card" elevation={3}>
				<canvas
					ref={canvasRef}
					width={width * cellSize} height={height * cellSize}
					className={`robot-canvas ${editMode ? 'edit-mode' : ''} ${isDraggingRobot ? 'dragging' : ''}`}
					onMouseDown={handleMouseDown}
					onContextMenu={handleCanvasRightClick}
					onWheel={handleWheel}
					style={{
						display: 'block',
						maxWidth: '100%',
						maxHeight: '100%',
						width: 'auto',
						height: 'auto',
						cursor: editMode ? (isDraggingRobot ? 'grabbing' : 'crosshair') : 'default'
					}}
				/>
			</Card>
			<Card className="status-card" elevation={2}>
				<Typography variant="body2" component="pre" className="status-text">
					{statusMessage || ' '}
				</Typography>
			</Card>
		</div>
	);
});

export default Field;