// FILE START: Field.jsx
import React, {memo, useCallback, useEffect, useState, useRef} from 'react';
import {Card, Typography} from '@mui/material';
import {drawField, drawStaticLayer} from '../canvasDrawing'; // Уточните путь
import {getHint} from '../hints'; // Уточните путь
import './Field.css';
import logger from '../../Logger'; // Уточните путь

const Field = memo(({
	                    canvasRef,
	                    robotPos, walls, permanentWalls, markers, coloredCells, symbols,
	                    width, height, cellSize, editMode, statusMessage,
	                    setRobotPos, setWalls, setMarkers, setColoredCells, setCellSize, setStatusMessage,
                    }) => {

	const offscreenCanvasRef = useRef(null);
	const staticLayerNeedsUpdate = useRef(true);
	const [isDraggingRobot, setIsDraggingRobot] = useState(false);

	// Эффект для статического слоя (без изменений)
	useEffect(() => {
		if (!canvasRef.current) {
			console.error("Main canvas Ref not available in static layer effect.");
			return;
		}
		if (!offscreenCanvasRef.current) {
			offscreenCanvasRef.current = document.createElement('canvas');
			logger.log_event("Offscreen canvas created for static layer.");
			staticLayerNeedsUpdate.current = true;
		}
		const mainCanvas = canvasRef.current;
		const offscreenCanvas = offscreenCanvasRef.current;
		const newWidth = Math.round(width * cellSize);
		const newHeight = Math.round(height * cellSize);
		if (offscreenCanvas.width !== newWidth || offscreenCanvas.height !== newHeight) {
			offscreenCanvas.width = newWidth;
			offscreenCanvas.height = newHeight;
			logger.log_event(`Offscreen canvas resized to ${newWidth}x${newHeight}`);
			staticLayerNeedsUpdate.current = true;
		}
		if (staticLayerNeedsUpdate.current) {
			console.debug("Updating static layer (grid) on offscreen canvas...");
			const staticConfig = {width, height, cellSize};
			drawStaticLayer(offscreenCanvas, staticConfig);
			staticLayerNeedsUpdate.current = false;
			logger.log_event("Static layer (grid) updated on offscreen canvas.");
			if (mainCanvas.width !== newWidth || mainCanvas.height !== newHeight) {
				mainCanvas.width = newWidth;
				mainCanvas.height = newHeight;
				logger.log_event(`Resized main canvas to match offscreen: ${newWidth}x${newHeight}`);
			} else {
				const ctx = mainCanvas.getContext('2d');
				if (ctx) {
					logger.debug("Triggering dynamic layer redraw after static layer update.");
					const dynamicConfig = {coloredCells, robotPos, markers, symbols, walls, permanentWalls, cellSize};
					drawField(mainCanvas, offscreenCanvas, dynamicConfig);
				}
			}
		}
	}, [width, height, cellSize, canvasRef]);

	// Эффект для динамического слоя (без изменений)
	useEffect(() => {
		const displayCanvas = canvasRef.current;
		const offscreenCanvas = offscreenCanvasRef.current;
		if (!displayCanvas || !offscreenCanvas) {
			return;
		}
		const expectedWidth = Math.round(width * cellSize);
		const expectedHeight = Math.round(height * cellSize);
		if (displayCanvas.width !== expectedWidth || displayCanvas.height !== expectedHeight) {
			displayCanvas.width = expectedWidth;
			displayCanvas.height = expectedHeight;
			logger.log_event(`Display canvas synchronized to size ${expectedWidth}x${expectedHeight}`);
			if (offscreenCanvas.width !== expectedWidth || offscreenCanvas.height !== expectedHeight) {
				logger.warning("Offscreen canvas size mismatch during dynamic draw - resizing and redrawing static layer.");
				offscreenCanvas.width = expectedWidth;
				offscreenCanvas.height = expectedHeight;
				drawStaticLayer(offscreenCanvas, {width, height, cellSize});
			}
		}
		const dynamicConfig = {coloredCells, robotPos, markers, symbols, walls, permanentWalls, cellSize};
		drawField(displayCanvas, offscreenCanvas, dynamicConfig);
	}, [canvasRef, robotPos, walls, permanentWalls, markers, coloredCells, symbols, width, height, cellSize]);

	// --- Обработчики событий мыши ---

	// getCanvasCoords и toGridCoords без изменений
	const getCanvasCoords = useCallback((event) => { /* ... */
		const canvas = canvasRef.current;
		if (!canvas) return {x: null, y: null};
		const rect = canvas.getBoundingClientRect();
		let clientX, clientY;
		if (event.touches && event.touches.length > 0) {
			clientX = event.touches[0].clientX;
			clientY = event.touches[0].clientY;
		} else {
			clientX = event.clientX;
			clientY = event.clientY;
		}
		if (clientX === undefined || clientY === undefined) {
			return {x: null, y: null};
		}
		if (clientX < rect.left || clientX > rect.right || clientY < rect.top || clientY > rect.bottom) {
			return {x: null, y: null};
		}
		const canvasX = clientX - rect.left;
		const canvasY = clientY - rect.top;
		const scaleX = canvas.width / rect.width;
		const scaleY = canvas.height / rect.height;
		const x = canvasX * scaleX;
		const y = canvasY * scaleY;
		if (x < 0 || x >= canvas.width || y < 0 || y >= canvas.height) {
			return {x: null, y: null};
		}
		return {x, y};
	}, [canvasRef]);
	const toGridCoords = useCallback((px, py) => { /* ... */
		if (cellSize <= 0) return {gridX: 0, gridY: 0};
		let gx = Math.floor(px / cellSize);
		let gy = Math.floor(py / cellSize);
		gx = Math.min(Math.max(gx, 0), width - 1);
		gy = Math.min(Math.max(gy, 0), height - 1);
		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	// --->>> ОБНОВЛЯЕМ ПОДСКАЗКИ В handleWallsAndCells <<<---
	const handleWallsAndCells = useCallback((gridX, gridY, pixelX, pixelY) => {
		if (cellSize <= 0) return;
		const wallMargin = Math.max(2, Math.min(8, cellSize * 0.12));
		const xRemainder = pixelX % cellSize;
		const yRemainder = pixelY % cellSize;
		let wallKey = null;
		if (yRemainder < wallMargin && gridY > 0) wallKey = `${gridX},${gridY},${gridX + 1},${gridY}`;
		else if (yRemainder > cellSize - wallMargin && gridY < height - 1) wallKey = `${gridX},${gridY + 1},${gridX + 1},${gridY + 1}`;
		else if (xRemainder < wallMargin && gridX > 0) wallKey = `${gridX},${gridY},${gridX},${gridY + 1}`;
		else if (xRemainder > cellSize - wallMargin && gridX < width - 1) wallKey = `${gridX + 1},${gridY},${gridX + 1},${gridY + 1}`;

		if (wallKey) { // Клик на границе
			if (permanentWalls.has(wallKey)) {
				// Используем новый ключ подсказки
				setStatusMessage(getHint('canvasLeftClickEditModePermanentWall', true));
				logger.log_warning("[Wall Action] Attempted to modify permanent wall: " + wallKey);
			} else {
				setWalls(prevWalls => {
					const newWalls = new Set(prevWalls);
					if (newWalls.has(wallKey)) {
						newWalls.delete(wallKey);
						// Используем новый ключ подсказки
						setStatusMessage(getHint('canvasLeftClickEditModeWallRemove', true));
						logger.log_event("[Wall Action] Wall removed via click: " + wallKey);
					} else {
						newWalls.add(wallKey);
						// Используем новый ключ подсказки
						setStatusMessage(getHint('canvasLeftClickEditModeWallAdd', true));
						logger.log_event("[Wall Action] Wall added via click: " + wallKey);
					}
					return newWalls;
				});
			}
		} else { // Клик на клетке
			const cellKey = `${gridX},${gridY}`;
			setColoredCells(prevCells => {
				const newCells = new Set(prevCells);
				if (newCells.has(cellKey)) {
					newCells.delete(cellKey);
					// Используем новый ключ подсказки
					setStatusMessage(getHint('canvasLeftClickEditModeCellClear', true));
					logger.log_event("[Cell Action] Cell cleared via click: " + cellKey);
				} else {
					newCells.add(cellKey);
					// Используем новый ключ подсказки
					setStatusMessage(getHint('canvasLeftClickEditModeCellPaint', true));
					logger.log_event("[Cell Action] Cell painted via click: " + cellKey);
				}
				return newCells;
			});
		}
	}, [cellSize, width, height, permanentWalls, setWalls, setColoredCells, setStatusMessage, logger]);

	// --->>> ОБНОВЛЯЕМ ПОДСКАЗКИ В handleMouseDown <<<---
	const handleMouseDown = useCallback((e) => {
		if (e.button !== 0) return;
		e.preventDefault();
		const {x: pixelX, y: pixelY} = getCanvasCoords(e);
		if (pixelX === null || pixelY === null) {
			return;
		}
		const {gridX, gridY} = toGridCoords(pixelX, pixelY);
		if (editMode) {
			if (robotPos && gridX === robotPos.x && gridY === robotPos.y) {
				setIsDraggingRobot(true);
				// Используем новый ключ подсказки
				setStatusMessage(getHint('robotDragStart', true));
				logger.log_robot_drag_start(robotPos);
			} else {
				handleWallsAndCells(gridX, gridY, pixelX, pixelY);
			}
		} else {
			// Используем новый ключ подсказки
			setStatusMessage(getHint('canvasLeftClickNoEdit', false));
			logger.log_event('Left click ignored (not in edit mode).');
		}
	}, [editMode, robotPos, getCanvasCoords, toGridCoords, setStatusMessage, handleWallsAndCells, setIsDraggingRobot, logger]);

	// handleMouseMove без изменений
	const handleMouseMove = useCallback((e) => { /* ... */
		if (!isDraggingRobot) return;
		e.preventDefault();
		const {x: pixelX, y: pixelY} = getCanvasCoords(e);
		if (pixelX === null || pixelY === null) {
			return;
		}
		const {gridX, gridY} = toGridCoords(pixelX, pixelY);
		if (robotPos && (gridX !== robotPos.x || gridY !== robotPos.y)) {
			setRobotPos({x: gridX, y: gridY});
		}
	}, [isDraggingRobot, getCanvasCoords, toGridCoords, setRobotPos, robotPos]);

	// --->>> ОБНОВЛЯЕМ ПОДСКАЗКИ В handleMouseUp <<<---
	const handleMouseUp = useCallback((e) => {
		if (!isDraggingRobot || e.button !== 0) return;
		e.preventDefault();
		setIsDraggingRobot(false);
		// Используем новый ключ и добавляем позицию
		setStatusMessage(`${getHint('robotDragEnd', true)} (${robotPos?.x ?? '?'}, ${robotPos?.y ?? '?'}).`);
		logger.log_robot_drag_end(robotPos);
	}, [isDraggingRobot, setStatusMessage, robotPos, setIsDraggingRobot, logger]);

	// --->>> ОБНОВЛЯЕМ ПОДСКАЗКИ В handleCanvasRightClick <<<---
	const handleCanvasRightClick = useCallback((e) => {
		e.preventDefault();
		const {x: pixelX, y: pixelY} = getCanvasCoords(e);
		if (pixelX === null || pixelY === null) return;
		if (editMode) {
			const {gridX, gridY} = toGridCoords(pixelX, pixelY);
			const posKey = `${gridX},${gridY}`;
			setMarkers(prevMarkers => {
				const newMarkers = {...prevMarkers};
				if (newMarkers[posKey]) {
					delete newMarkers[posKey];
					// Используем новый ключ подсказки
					setStatusMessage(getHint('canvasRightClickEditModeMarkerRemove', true));
					logger.log_event("[Marker Action] Marker removed via right click: " + posKey);
				} else {
					newMarkers[posKey] = 1;
					// Используем новый ключ подсказки
					setStatusMessage(getHint('canvasRightClickEditModeMarkerAdd', true));
					logger.log_event("[Marker Action] Marker added via right click: " + posKey);
				}
				return newMarkers;
			});
		} else {
			// Используем новый ключ подсказки
			setStatusMessage(getHint('canvasRightClickNoEdit', false));
			logger.log_event('Right click ignored (not in edit mode).');
		}
	}, [editMode, getCanvasCoords, toGridCoords, setMarkers, setStatusMessage, logger]);

	// --->>> ОБНОВЛЯЕМ ПОДСКАЗКИ В handleWheel <<<---
	const handleWheel = useCallback((e) => {
		e.preventDefault();
		const delta = Math.sign(e.deltaY);
		const zoomFactor = 1.15;
		const minCellSize = 15;
		const maxCellSize = 180;
		let newSize;
		const oldSize = cellSize;

		if (delta < 0) { // Приближение
			newSize = Math.min(maxCellSize, Math.round(oldSize * zoomFactor));
			if (newSize > oldSize) {
				setStatusMessage(getHint('wheelZoomIn')); // Старый ключ подходит
				logger.log_event(`[Zoom] Changed cell size from ${oldSize} to ${newSize} (+)`);
			} else {
				// Используем новый ключ подсказки
				setStatusMessage(getHint('zoomMaxReached'));
				return;
			}
		} else { // Отдаление
			newSize = Math.max(minCellSize, Math.round(oldSize / zoomFactor));
			if (newSize < oldSize) {
				setStatusMessage(getHint('wheelZoomOut')); // Старый ключ подходит
				logger.log_event(`[Zoom] Changed cell size from ${oldSize} to ${newSize} (-)`);
			} else {
				// Используем новый ключ подсказки
				setStatusMessage(getHint('zoomMinReached'));
				return;
			}
		}
		staticLayerNeedsUpdate.current = true;
		setCellSize(newSize);
	}, [cellSize, setCellSize, setStatusMessage, logger]);

	// Глобальные слушатели без изменений
	useEffect(() => {
		if (isDraggingRobot) {
			window.addEventListener('mousemove', handleMouseMove);
			window.addEventListener('mouseup', handleMouseUp);
			window.addEventListener('touchmove', handleMouseMove, {passive: false});
			window.addEventListener('touchend', handleMouseUp);
			window.addEventListener('touchcancel', handleMouseUp);
			return () => {
				window.removeEventListener('mousemove', handleMouseMove);
				window.removeEventListener('mouseup', handleMouseUp);
				window.removeEventListener('touchmove', handleMouseMove);
				window.removeEventListener('touchend', handleMouseUp);
				window.removeEventListener('touchcancel', handleMouseUp);
			};
		}
	}, [isDraggingRobot, handleMouseMove, handleMouseUp]);

	// --- Рендер компонента ---
	return (
		<div className="field-area">
			{/* Карточка с canvas */}
			<Card className="field-card" elevation={3}>
				<canvas
					ref={canvasRef}
					className={`robot-canvas ${editMode ? 'edit-mode' : ''} ${isDraggingRobot ? 'dragging' : ''}`}
					onMouseDown={handleMouseDown} onContextMenu={handleCanvasRightClick} onWheel={handleWheel}
					onTouchStart={handleMouseDown}
					style={{
						display: 'block',
						maxWidth: '100%',
						maxHeight: '100%',
						width: 'auto',
						height: 'auto',
						aspectRatio: `${width || 1} / ${height || 1}`,
						cursor: editMode ? (isDraggingRobot ? 'grabbing' : 'crosshair') : 'default',
						touchAction: 'none'
					}}
				/>
			</Card>
			{/* Карточка статуса */}
			<Card className="status-card" elevation={2} sx={{mt: 1, width: '100%'}}>
				<Typography variant="body2" component="div" className="status-text" sx={{
					minHeight: '60px',
					maxHeight: '100px',
					overflowY: 'auto',
					textAlign: 'center',
					padding: '8px',
					whiteSpace: 'pre-wrap',
					wordBreak: 'break-word'
				}}>
					{statusMessage || ' '}
				</Typography>
			</Card>
		</div>
	);
});

export default Field;
// FILE END: Field.jsx