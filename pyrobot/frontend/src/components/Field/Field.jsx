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
	                    statusMessage,
	                    setStatusMessage,
                    }) => {
	const [isDraggingRobot, setIsDraggingRobot] = useState(false);

	/**
	 * Перерисовываем поле при каждом изменении данных (координаты робота, стены, т. д.).
	 */
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
			cellSize
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
		cellSize
	]);

	/**
	 * Преобразует координаты клика (event.clientX, event.clientY)
	 * в "рисованные" пиксели canvas с учётом масштабирования (если canvas растянут/сжат).
	 */
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

	/**
	 * Проверка: вышли ли мы совсем за границы холста? (По пикселям).
	 */
	const isOutsideCanvas = useCallback((px, py) => {
		// Холст теперь width * cellSize, height * cellSize.
		return px < 0 || py < 0 || px >= width * cellSize || py >= height * cellSize;
	}, [width, height, cellSize]);

	/**
	 * Преобразует "рисованные" пиксели (px,py) в клетку (gridX,gridY) в диапазоне [0..width-1], [0..height-1].
	 */
	const toGridCoords = useCallback((px, py) => {
		let gx = Math.floor(px / cellSize);
		let gy = Math.floor(py / cellSize);

		// Зажимаем (clamp)
		if (gx < 0) gx = 0;
		if (gx >= width) gx = width - 1;
		if (gy < 0) gy = 0;
		if (gy >= height) gy = height - 1;

		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	/**
	 * При клике (левая кнопка) в режиме редактирования: ставим/убираем стену или красим клетку.
	 * Используем "margin", чтобы определить, попали ли в границу (стена) или внутрь клетки (покраска).
	 */
	const handleCanvasLeftClickEditMode = useCallback((gx, gy, px, py) => {
		const margin = 5; // расстояние (px) от края клетки, чтобы считать "грань"

		// Остаток внутри клетки
		const xRem = px % cellSize;
		const yRem = py % cellSize;
		let wall = null;

		// Попали в левую грань?
		if (xRem < margin) {
			wall = `${gx},${gy},${gx},${gy + 1}`;
		}
		// Правую грань?
		else if (xRem > cellSize - margin) {
			wall = `${gx + 1},${gy},${gx + 1},${gy + 1}`;
		}
		// Верхнюю грань?
		else if (yRem < margin) {
			wall = `${gx},${gy},${gx + 1},${gy}`;
		}
		// Нижнюю грань?
		else if (yRem > cellSize - margin) {
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
			// Иначе красим клетку
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
	}, [
		cellSize,
		permanentWalls,
		setWalls,
		setColoredCells,
		setStatusMessage
	]);

	/**
	 * onMouseDown (левая кнопка).
	 * Если клик по роботу, начинаем drag, иначе пытаемся поставить стену/закраску.
	 */
	const handleMouseDown = useCallback((e) => {
		e.preventDefault();
		e.stopPropagation();

		if (e.button !== 0) return; // только левая кнопка
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvas(x, y)) {
			setStatusMessage('Клик за пределами поля.');
			return;
		}

		if (!editMode) {
			setStatusMessage(getHint('canvasLeftClickNoEdit', false));
			return;
		}

		// Переводим px->grid
		const {gridX, gridY} = toGridCoords(x, y);
		// Если совпадает с роботом => drag
		if (gridX === robotPos.x && gridY === robotPos.y) {
			setIsDraggingRobot(true);
			setStatusMessage('Перетаскивание робота...');
		} else {
			// Иначе ставим стену/закрашиваем
			handleCanvasLeftClickEditMode(gridX, gridY, x, y);
		}
	}, [
		editMode,
		robotPos,
		getCanvasCoords,
		isOutsideCanvas,
		toGridCoords,
		handleCanvasLeftClickEditMode,
		setStatusMessage
	]);

	/**
	 * onMouseMove.
	 * Если drag активен, двигаем робота.
	 */
	const handleMouseMove = useCallback((e) => {
		e.preventDefault();
		e.stopPropagation();

		if (!isDraggingRobot) return;
		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null) return;

		// Зажимаем в пределы поля
		const {gridX, gridY} = toGridCoords(x, y);
		setRobotPos({x: gridX, y: gridY});
	}, [
		isDraggingRobot,
		getCanvasCoords,
		toGridCoords,
		setRobotPos
	]);

	/**
	 * onMouseUp => завершаем drag (если шёл).
	 */
	const handleMouseUp = useCallback((e) => {
		e.preventDefault();
		e.stopPropagation();

		if (isDraggingRobot) {
			setIsDraggingRobot(false);
			setStatusMessage('Перетаскивание робота завершено.');
		}
	}, [isDraggingRobot, setStatusMessage]);

	/**
	 * Правый клик => ставим/убираем маркер (при editMode).
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
			} else {
				delete copy[posKey];
				setStatusMessage('Маркер убран. ' + getHint('canvasRightClickEditMode', true));
			}
			return copy;
		});
	}, [
		editMode,
		getCanvasCoords,
		isOutsideCanvas,
		toGridCoords,
		setMarkers,
		setStatusMessage
	]);

	// Формируем текст статуса
	const statusLines = [
		`Позиция робота: (${robotPos.x}, ${robotPos.y})`,
		`Маркеров: ${Object.keys(markers).length}`,
		`Раскрашенных клеток: ${coloredCells.size}`,
	];
	const statusText = statusLines.join('\n');

	return (
		<div className="field-area">
			<Card className="field-card">
				<canvas
					ref={canvasRef}
					// ВАЖНО: без +2. То есть ровно width * cellSize, height * cellSize.
					width={width * cellSize}
					height={height * cellSize}
					className={editMode ? 'edit-mode' : ''}
					onMouseDown={handleMouseDown}
					onMouseMove={handleMouseMove}
					onMouseUp={handleMouseUp}
					// НЕ ставим onMouseLeave, чтобы не прерывать drag
					onContextMenu={handleCanvasRightClick}
				/>
			</Card>

			<Card className="status-card">
				<Typography variant="body2" className="status-text">
					{statusText}
					{statusMessage ? `\n\n${statusMessage}` : ''}
				</Typography>
			</Card>
		</div>
	);
});

export default Field;
