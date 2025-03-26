/**
 * @file canvasDrawing.js
 * @description Модуль для рисования игрового поля симулятора робота на canvas.
 */

export function clearCanvas(canvas, ctx) {
	ctx.clearRect(0, 0, canvas.width, canvas.height);
}

export function drawColoredCells(ctx, coloredCells, cellSize) {
	ctx.fillStyle = 'rgba(128, 128, 128, 0.7)'; // Slightly transparent gray
	if (coloredCells && typeof coloredCells[Symbol.iterator] === 'function') {
		coloredCells.forEach(cellKey => {
			try { // Add try-catch for robustness
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
}

export function drawRobot(ctx, robotPos, cellSize) {
	if (!robotPos || typeof robotPos.x !== 'number' || typeof robotPos.y !== 'number') {
		console.warn("Invalid robotPos for drawRobot:", robotPos);
		return;
	}
	const rx = (robotPos.x + 0.5) * cellSize;
	const ry = (robotPos.y + 0.5) * cellSize;
	const dSize = cellSize * 0.6;
	ctx.fillStyle = '#FF4500';
	ctx.strokeStyle = '#000000';
	ctx.lineWidth = 1;
	ctx.beginPath();
	ctx.moveTo(rx, ry - dSize / 2);
	ctx.lineTo(rx + dSize / 2, ry);
	ctx.lineTo(rx, ry + dSize / 2);
	ctx.lineTo(rx - dSize / 2, ry);
	ctx.closePath();
	ctx.fill();
	ctx.stroke();
}

export function drawMarkers(ctx, markers, cellSize) {
	if (!markers || typeof markers !== 'object') return;
	const radius = cellSize * 0.15;
	const offset = cellSize * 0.75;
	Object.keys(markers).forEach(key => {
		try {
			const coords = key.split(',').map(Number);
			if (coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
				ctx.fillStyle = 'white';
				ctx.strokeStyle = 'black';
				ctx.lineWidth = 1;
				ctx.beginPath();
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

// --- Draw Symbols Function with Logging ---
export function drawSymbols(ctx, symbols, cellSize) {
	if (!symbols || typeof symbols !== 'object') {
		return;
	}

	// <<< Log entry into drawSymbols >>>
	// Use short log to avoid flooding, can expand if needed
	console.debug('%cdrawSymbols - Drawing %d symbols', 'color: teal;', Object.keys(symbols).length);
	// console.debug('%cdrawSymbols - Drawing data:', 'color: teal;', symbols); // Use this for more detail if needed
	// <<< ------------------------- >>>

	const padding = cellSize * 0.1;
	const fontSize = Math.max(8, Math.min(16, Math.round(cellSize * 0.25)));
	ctx.font = `bold ${fontSize}px Arial, sans-serif`;
	ctx.fillStyle = '#000000';
	ctx.textAlign = 'left';

	Object.entries(symbols).forEach(([key, symbolData]) => {
		try { // Add try-catch
			if (!symbolData) return;
			const coords = key.split(',').map(Number);
			if (coords.length !== 2 || isNaN(coords[0]) || isNaN(coords[1])) {
				console.warn("Invalid key in symbols:", key);
				return;
			}
			const [x, y] = coords;
			// console.debug(`Drawing symbol at [${x}, ${y}]`, symbolData); // Detail log per symbol if needed
			if (symbolData.upper) {
				ctx.textBaseline = 'top';
				ctx.fillText(symbolData.upper, x * cellSize + padding, y * cellSize + padding);
			}
			if (symbolData.lower) {
				ctx.textBaseline = 'bottom';
				ctx.fillText(symbolData.lower, x * cellSize + padding, (y + 1) * cellSize - padding);
			}
		} catch (e) {
			console.error("Error drawing symbol for key:", key, e);
		}
	});
}

// ------------------------------------------

export function drawWalls(ctx, walls, strokeStyle, lineWidth, cellSize) {
	if (!walls || typeof walls[Symbol.iterator] !== 'function') return;
	ctx.strokeStyle = strokeStyle;
	ctx.lineWidth = lineWidth;
	ctx.lineCap = 'round';
	walls.forEach(wall => {
		try {
			const coords = wall.split(',').map(Number);
			if (coords.length === 4 && coords.every(c => !isNaN(c))) {
				ctx.beginPath();
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
	ctx.strokeStyle = '#A0A0A0';
	ctx.lineWidth = 0.5;
	for (let x = 0; x <= width; x++) {
		ctx.beginPath();
		ctx.moveTo(x * cellSize, 0);
		ctx.lineTo(x * cellSize, height * cellSize);
		ctx.stroke();
	}
	for (let y = 0; y <= height; y++) {
		ctx.beginPath();
		ctx.moveTo(0, y * cellSize);
		ctx.lineTo(width * cellSize, y * cellSize);
		ctx.stroke();
	}
}

export function drawField(canvas, config) {
	if (!canvas) {
		console.error("drawField called with no canvas");
		return;
	}
	const ctx = canvas.getContext('2d');
	if (!ctx) {
		console.error("Failed to get 2D context");
		return;
	}
	if (!config) {
		console.error("drawField called with no config");
		return;
	}

	// <<< Log the config received by drawField >>>
	// Stringify carefully, converting Sets
	const configToLog = JSON.stringify(config, (key, value) => value instanceof Set ? Array.from(value) : value, 2);
	console.log('%cdrawField - Config:', 'color: magenta;', JSON.parse(configToLog));
	// <<< ------------------------------------ >>>

	clearCanvas(canvas, ctx);
	// Draw layers, passing potentially undefined/null values to checked functions
	drawGrid(ctx, config.width, config.height, config.cellSize);
	drawColoredCells(ctx, config.coloredCells, config.cellSize);
	drawSymbols(ctx, config.symbols, config.cellSize); // This function now has internal checks
	drawWalls(ctx, config.walls, '#FFA500', Math.max(2, config.cellSize * 0.08), config.cellSize);
	drawWalls(ctx, config.permanentWalls, '#8B4513', Math.max(3, config.cellSize * 0.1), config.cellSize);
	drawMarkers(ctx, config.markers, config.cellSize);
	drawRobot(ctx, config.robotPos, config.cellSize);
}