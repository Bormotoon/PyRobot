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
	// Состояние для отслеживания перетаскивания робота
	const [isDraggingRobot, setIsDraggingRobot] = useState(false);

	/**
	 * Перерисовываем поле при каждом изменении данных (координаты робота, стены и т.д.).
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
	 * в координаты canvas с учётом масштабирования.
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
	 * Проверка, не вышли ли мы за пределы холста (по пикселям).
	 */
	const isOutsideCanvas = useCallback((px, py) => {
		return px < 0 || py < 0 || px >= width * cellSize || py >= height * cellSize;
	}, [width, height, cellSize]);

	/**
	 * Преобразует пиксельные координаты (px, py) в координаты сетки (gridX, gridY),
	 * зажимая (clamp) в диапазон [0..width-1] и [0..height-1].
	 */
	const toGridCoords = useCallback((px, py) => {
		let gx = Math.floor(px / cellSize);
		let gy = Math.floor(py / cellSize);

		gx = Math.min(Math.max(gx, 0), width - 1);
		gy = Math.min(Math.max(gy, 0), height - 1);

		return {gridX: gx, gridY: gy};
	}, [cellSize, width, height]);

	/**
	 * ЛКМ в режиме редактирования:
	 * - если кликаем по роботу, начинаем перетаскивание;
	 * - иначе ставим/убираем стены или закрашиваем клетку.
	 */
	const handleMouseDown = useCallback((e) => {
		if (e.button !== 0) return; // Только левая кнопка
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

		// Определяем клетку, куда кликнули
		const {gridX, gridY} = toGridCoords(x, y);

		// Если это клетка, в которой сейчас робот – начинаем «drag»
		if (gridX === robotPos.x && gridY === robotPos.y) {
			setIsDraggingRobot(true);
			setStatusMessage('Начали перетаскивать робота.');
			return;
		}

		// Иначе - взаимодействуем со стенами/раскрашенными клетками
		handleWallsAndCells(gridX, gridY, x, y);
	}, [
		editMode,
		robotPos,
		getCanvasCoords,
		isOutsideCanvas,
		toGridCoords,
		setStatusMessage
	]);

	/**
	 * Вспомогательный метод для постановки/убирания стен или закраски клетки.
	 */
	const handleWallsAndCells = useCallback((gx, gy, px, py) => {
		const margin = 5; // отступ от края клетки для "попадания" в стену
		const xRem = px % cellSize;
		const yRem = py % cellSize;
		let wall = null;

		// Левый/правый/верхний/нижний край
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
			// Ставим/убираем стену (если она не «постоянная»)
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
				setStatusMessage(
					'Это постоянная стена. ' + getHint('canvasLeftClickEditMode', true)
				);
			}
		} else {
			// Закрашиваем/очищаем клетку
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
	 * Пока ЛКМ зажата и мы «таскаем» робота — он двигается за курсором.
	 */
	const handleMouseMove = useCallback((e) => {
		if (!isDraggingRobot) return;
		e.preventDefault();
		e.stopPropagation();

		const {x, y} = getCanvasCoords(e);
		if (x === null || y === null || isOutsideCanvas(x, y)) {
			return;
		}

		// Определяем клетку и «зажимаем» в пределах поля
		const {gridX, gridY} = toGridCoords(x, y);
		setRobotPos({x: gridX, y: gridY});
	}, [
		isDraggingRobot,
		getCanvasCoords,
		toGridCoords,
		setRobotPos,
		isOutsideCanvas
	]);

	/**
	 * Отпустили ЛКМ — завершаем «drag», робот фиксируется в текущей клетке.
	 */
	const handleMouseUp = useCallback((e) => {
		if (!isDraggingRobot) return;
		e.preventDefault();
		e.stopPropagation();

		setIsDraggingRobot(false);
		setStatusMessage('Перемещение робота завершено.');
	}, [isDraggingRobot, setStatusMessage]);

	/**
	 * Правый клик (ПКМ) в режиме редактирования: добавить/убрать маркер.
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

	// Статус для отображения текущего состояния
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
					width={width * cellSize}
					height={height * cellSize}
					className={editMode ? 'edit-mode' : ''}
					onMouseDown={handleMouseDown}
					onMouseMove={handleMouseMove}
					onMouseUp={handleMouseUp}
					// не используем onMouseLeave, чтобы не обрывать «drag» внезапно
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
