// FILE START: canvasDrawing.js
/**
 * @file canvasDrawing.js
 * @description Модуль для рисования игрового поля симулятора робота на canvas.
 * Реализована оптимизация с использованием слоев (offscreen canvas) для статических элементов.
 */

// --- Функции отрисовки отдельных элементов (без изменений) ---

export function clearCanvas(canvas, ctx) {
	if (!canvas || !ctx) return;
	ctx.clearRect(0, 0, canvas.width, canvas.height);
}

export function drawColoredCells(ctx, coloredCells, cellSize) {
	if (!ctx || !coloredCells || typeof coloredCells[Symbol.iterator] !== 'function' || cellSize <= 0) return;
	ctx.fillStyle = 'rgba(192, 192, 192, 0.6)'; // Более светлый серый для закраски
	coloredCells.forEach(cellKey => {
		try {
			const coords = cellKey.split(',').map(Number);
			if (coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
				ctx.fillRect(coords[0] * cellSize, coords[1] * cellSize, cellSize, cellSize);
			} else {
				console.warn("Invalid key in coloredCells:", cellKey);
			}
		} catch (e) {
			console.error("Error drawing colored cell for key:", cellKey, e);
		}
	});
}

export function drawRobot(ctx, robotPos, cellSize, errorDirection = null) {
	if (!ctx || !robotPos || typeof robotPos.x !== 'number' || typeof robotPos.y !== 'number' || cellSize <= 0) {
		// console.warn("Invalid parameters for drawRobot:", {ctx, robotPos, cellSize});
		return;
	}
	const rx = (robotPos.x + 0.5) * cellSize;
	const ry = (robotPos.y + 0.5) * cellSize;
	const diamondSizeRatio = 0.6; // Размер ромба относительно клетки
	const diamondHalf = (cellSize * diamondSizeRatio) / 2;

	ctx.fillStyle = '#FF4500'; // OrangeRed
	ctx.strokeStyle = '#000000'; // Black border
	ctx.lineWidth = Math.max(1, cellSize * 0.02); // Тонкая граница

	ctx.beginPath();
	ctx.moveTo(rx, ry - diamondHalf);           // Top point
	ctx.lineTo(rx + diamondHalf, ry);           // Right point
	ctx.lineTo(rx, ry + diamondHalf);           // Bottom point
	ctx.lineTo(rx - diamondHalf, ry);           // Left point
	ctx.closePath();
	ctx.fill();
	ctx.stroke();
	
	// Рисуем красный треугольник при ошибке движения
	if (errorDirection) {
		drawRobotErrorTriangle(ctx, robotPos, cellSize, errorDirection);
	}
}

// Функция для отрисовки красного треугольника в углу клетки при ошибке движения
export function drawRobotErrorTriangle(ctx, robotPos, cellSize, direction) {
	if (!ctx || !robotPos || !direction || cellSize <= 0) return;
	
	const x = robotPos.x * cellSize;
	const y = robotPos.y * cellSize;
	const triangleSize = Math.max(8, cellSize * 0.25); // Размер треугольника
	
	ctx.fillStyle = '#FF0000'; // Красный цвет
	ctx.strokeStyle = '#800000'; // Темно-красная граница
	ctx.lineWidth = Math.max(1, cellSize * 0.015);
	
	ctx.beginPath();
	
	switch (direction.toLowerCase()) {
		case 'up':
			// Треугольник в верхнем левом углу
			ctx.moveTo(x, y);
			ctx.lineTo(x + triangleSize, y);
			ctx.lineTo(x, y + triangleSize);
			break;
		case 'down':
			// Треугольник в нижнем правом углу
			ctx.moveTo(x + cellSize, y + cellSize);
			ctx.lineTo(x + cellSize - triangleSize, y + cellSize);
			ctx.lineTo(x + cellSize, y + cellSize - triangleSize);
			break;
		case 'left':
			// Треугольник в нижнем левом углу
			ctx.moveTo(x, y + cellSize);
			ctx.lineTo(x + triangleSize, y + cellSize);
			ctx.lineTo(x, y + cellSize - triangleSize);
			break;
		case 'right':
			// Треугольник в верхнем правом углу
			ctx.moveTo(x + cellSize, y);
			ctx.lineTo(x + cellSize - triangleSize, y);
			ctx.lineTo(x + cellSize, y + triangleSize);
			break;
		default:
			return; // Неизвестное направление
	}
	
	ctx.closePath();
	ctx.fill();
	ctx.stroke();
}

export function drawMarkers(ctx, markers, cellSize) {
	if (!ctx || !markers || typeof markers !== 'object' || cellSize <= 0) return;
	const radius = cellSize * 0.15; // Радиус маркера
	const offset = cellSize * 0.75; // Смещение от угла клетки
	const lineWidth = Math.max(1, cellSize * 0.03);

	Object.keys(markers).forEach(key => {
		// Проверяем, что значение маркера "истинное" (вдруг там 0 или false)
		if (!markers[key]) return;
		try {
			const coords = key.split(',').map(Number);
			if (coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
				ctx.fillStyle = '#FFFFFF'; // White fill
				ctx.strokeStyle = '#333333'; // Dark gray border
				ctx.lineWidth = lineWidth;
				ctx.beginPath();
				// Рисуем в правом нижнем углу клетки
				ctx.arc(coords[0] * cellSize + offset, coords[1] * cellSize + offset, radius, 0, 2 * Math.PI);
				ctx.fill();
				ctx.stroke();
			} else {
				console.warn("Invalid key in markers:", key);
			}
		} catch (e) {
			console.error("Error drawing marker for key:", key, e);
		}
	});
}

export function drawSymbols(ctx, symbols, cellSize) {
	if (!ctx || !symbols || typeof symbols !== 'object' || cellSize <= 0) return;

	// console.debug('%cdrawSymbols - Drawing %d symbols', 'color: teal;', Object.keys(symbols).length);

	const padding = Math.max(1, cellSize * 0.08); // Отступ от краев
	// Адаптивный размер шрифта
	const baseFontSize = Math.max(8, Math.min(16, Math.round(cellSize * 0.25)));
	ctx.font = `bold ${baseFontSize}px Arial, sans-serif`;
	ctx.fillStyle = '#000000'; // Black text
	ctx.textAlign = 'left'; // Выравнивание по левому краю

	Object.entries(symbols).forEach(([key, symbolData]) => {
		try {
			if (!symbolData || (!symbolData.upper && !symbolData.lower)) return; // Пропускаем пустые данные
			const coords = key.split(',').map(Number);
			if (coords.length !== 2 || isNaN(coords[0]) || isNaN(coords[1])) {
				console.warn("Invalid key in symbols:", key);
				return;
			}
			const [x, y] = coords;
			const cellX = x * cellSize;
			const cellY = y * cellSize;

			// Рисуем верхний символ
			if (symbolData.upper) {
				ctx.textBaseline = 'top'; // Выравнивание по верхнему краю текста
				ctx.fillText(symbolData.upper, cellX + padding, cellY + padding);
			}
			// Рисуем нижний символ
			if (symbolData.lower) {
				ctx.textBaseline = 'bottom'; // Выравнивание по нижнему краю текста
				ctx.fillText(symbolData.lower, cellX + padding, cellY + cellSize - padding);
			}
		} catch (e) {
			console.error("Error drawing symbol for key:", key, e);
		}
	});
}

export function drawWalls(ctx, walls, strokeStyle, lineWidth, cellSize) {
	if (!ctx || !walls || typeof walls[Symbol.iterator] !== 'function' || cellSize <= 0) return;
	ctx.strokeStyle = strokeStyle;
	ctx.lineWidth = lineWidth;
	ctx.lineCap = 'round'; // Скругляем концы линий стен

	walls.forEach(wall => {
		try {
			// Формат стены: "x1,y1,x2,y2"
			const coords = wall.split(',').map(Number);
			if (coords.length === 4 && coords.every(c => !isNaN(c))) {
				ctx.beginPath();
				// Переводим координаты сетки в координаты canvas
				ctx.moveTo(coords[0] * cellSize, coords[1] * cellSize);
				ctx.lineTo(coords[2] * cellSize, coords[3] * cellSize);
				ctx.stroke();
			} else {
				console.warn("Invalid wall format:", wall);
			}
		} catch (e) {
			console.error("Error drawing wall:", wall, e);
		}
	});
}

export function drawGrid(ctx, width, height, cellSize) {
	if (!ctx || width <= 0 || height <= 0 || cellSize <= 0) return;
	ctx.strokeStyle = '#E0E0E0'; // Более светлый серый для сетки
	ctx.lineWidth = 0.5; // Тонкая сетка

	// Вертикальные линии
	for (let x = 0; x <= width; x++) {
		ctx.beginPath();
		ctx.moveTo(x * cellSize, 0);
		ctx.lineTo(x * cellSize, height * cellSize);
		ctx.stroke();
	}
	// Горизонтальные линии
	for (let y = 0; y <= height; y++) {
		ctx.beginPath();
		ctx.moveTo(0, y * cellSize);
		ctx.lineTo(width * cellSize, y * cellSize);
		ctx.stroke();
	}
}


// --- Оптимизация: Функции для работы со слоями ---

/**
 * Рисует статический слой (сетку) на заданный canvas (обычно offscreen).
 * @param {HTMLCanvasElement} canvas - Целевой canvas (offscreen).
 * @param {object} config - Конфигурация поля { width, height, cellSize }.
 */
export function drawStaticLayer(canvas, config) {
	if (!canvas || !config || !config.width || !config.height || !config.cellSize) {
		console.error("Invalid parameters for drawStaticLayer");
		return;
	}
	const ctx = canvas.getContext('2d');
	if (!ctx) {
		console.error("Failed to get 2D context for static layer");
		return;
	}
	console.debug("Drawing static layer (grid)...");
	// Очищаем offscreen canvas перед рисованием сетки
	clearCanvas(canvas, ctx);
	// Рисуем сетку
	drawGrid(ctx, config.width, config.height, config.cellSize);
}

/**
 * Основная функция отрисовки поля, использующая слои.
 * @param {HTMLCanvasElement} displayCanvas - Основной canvas для отображения.
 * @param {HTMLCanvasElement} offscreenCanvas - Canvas со статическим слоем (сеткой).
 * @param {object} config - Конфигурация с динамическими элементами { coloredCells, robotPos, markers, symbols, walls, permanentWalls, cellSize }.
 */
export function drawField(displayCanvas, offscreenCanvas, config) {
	if (!displayCanvas || !offscreenCanvas || !config || !config.cellSize) {
		console.error("drawField called with missing canvas or config", {displayCanvas, offscreenCanvas, config});
		return;
	}
	const ctx = displayCanvas.getContext('2d');
	if (!ctx) {
		console.error("Failed to get 2D context for display canvas");
		return;
	}

	// Логирование конфига (можно закомментировать в production)
	// const configToLog = JSON.stringify(config, (key, value) => value instanceof Set ? Array.from(value) : value, 2);
	// console.log('%cdrawField - Config:', 'color: magenta;', JSON.parse(configToLog));

	// 1. Очищаем основной canvas
	clearCanvas(displayCanvas, ctx);

	// 2. Рисуем статический слой (сетку) из offscreen canvas
	try {
		// Убедимся, что размеры offscreen canvas совпадают (на случай асинхронности)
		if (displayCanvas.width === offscreenCanvas.width && displayCanvas.height === offscreenCanvas.height) {
			ctx.drawImage(offscreenCanvas, 0, 0);
		} else {
			console.warn("Offscreen canvas size mismatch. Skipping drawing static layer.");
			// Можно попробовать перерисовать сетку напрямую, если размеры не совпадают
			// drawGrid(ctx, config.width, config.height, config.cellSize); // Fallback?
		}
	} catch (e) {
		console.error("Error drawing offscreen canvas:", e);
		// Fallback: рисуем сетку напрямую, если offscreen недоступен
		if (config.width && config.height && config.cellSize) {
			console.warn("Fallback: Drawing grid directly on display canvas.");
			drawGrid(ctx, config.width, config.height, config.cellSize);
		}
	}


	// 3. Рисуем динамические слои поверх
	drawColoredCells(ctx, config.coloredCells, config.cellSize);
	drawSymbols(ctx, config.symbols, config.cellSize);
	// Пользовательские стены (например, оранжевые)
	drawWalls(ctx, config.walls, '#FFA500', Math.max(2, config.cellSize * 0.08), config.cellSize);
	// Границы поля (например, коричневые и толще)
	drawWalls(ctx, config.permanentWalls, '#8B4513', Math.max(3, config.cellSize * 0.1), config.cellSize);
	drawMarkers(ctx, config.markers, config.cellSize);
	drawRobot(ctx, config.robotPos, config.cellSize, config.robotErrorDirection); // Робот рисуется последним, поверх всего
}

// FILE END: canvasDrawing.js