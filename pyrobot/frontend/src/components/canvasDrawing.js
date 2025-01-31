/**
 * canvasDrawing.js
 *
 * Унифицированный вариант: каждая клетка (x,y) рисуется
 * непосредственно в (x*cellSize, y*cellSize).
 * Canvas имеет размер width*cellSize, height*cellSize.
 */

export function clearCanvas(canvas, ctx) {
	ctx.clearRect(0, 0, canvas.width, canvas.height);
}

export function drawColoredCells(ctx, coloredCells, cellSize) {
	ctx.fillStyle = 'gray';
	coloredCells.forEach(cell => {
		const [x, y] = cell.split(',').map(Number);
		// Без "+1", просто (x, y)
		ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
	});
}

export function drawRobot(ctx, robotPos, cellSize) {
	// Центр робота: (robotPos.x + 0.5, robotPos.y + 0.5), чтобы ромб был внутри клетки
	const rx = (robotPos.x + 0.5) * cellSize;
	const ry = (robotPos.y + 0.5) * cellSize;
	const dSize = cellSize * 0.6;

	ctx.fillStyle = '#FF4500';
	ctx.beginPath();
	// Ромб: верхняя точка
	ctx.moveTo(rx, ry - dSize / 2);
	// Правая точка
	ctx.lineTo(rx + dSize / 2, ry);
	// Нижняя
	ctx.lineTo(rx, ry + dSize / 2);
	// Левая
	ctx.lineTo(rx - dSize / 2, ry);
	ctx.closePath();
	ctx.fill();
	ctx.stroke();
}

export function drawMarkers(ctx, markers, cellSize) {
	Object.keys(markers).forEach(key => {
		const [x, y] = key.split(',').map(Number);
		ctx.fillStyle = 'white';
		ctx.beginPath();
		// Центр маркера ближе к нижнему правому углу клетки?
		// Можно (x+0.5, y+0.5) для центра
		ctx.arc(
			(x + 0.75) * cellSize,
			(y + 0.75) * cellSize,
			cellSize * 0.15,
			0,
			2 * Math.PI
		);
		ctx.fill();
		ctx.strokeStyle = 'black';
		ctx.lineWidth = 1;
		ctx.stroke();
	});
}

export function drawWalls(ctx, walls, strokeStyle, lineWidth, cellSize) {
	ctx.strokeStyle = strokeStyle;
	ctx.lineWidth = lineWidth;
	walls.forEach(wall => {
		const [x1, y1, x2, y2] = wall.split(',').map(Number);
		ctx.beginPath();
		ctx.moveTo(x1 * cellSize, y1 * cellSize);
		ctx.lineTo(x2 * cellSize, y2 * cellSize);
		ctx.stroke();
	});
}

export function drawGrid(ctx, width, height, cellSize) {
	ctx.strokeStyle = '#C8C80F';
	ctx.lineWidth = 1;
	for (let x = 0; x <= width; x++) {
		for (let y = 0; y <= height; y++) {
			ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
		}
	}
}

export function drawField(canvas, {
	coloredCells,
	robotPos,
	markers,
	walls,
	permanentWalls,
	width,
	height,
	cellSize
}) {
	if (!canvas) return;
	const ctx = canvas.getContext('2d');

	clearCanvas(canvas, ctx);

	drawColoredCells(ctx, coloredCells, cellSize);
	drawRobot(ctx, robotPos, cellSize);
	drawMarkers(ctx, markers, cellSize);

	drawWalls(ctx, walls, '#C8C80F', 6, cellSize);
	drawWalls(ctx, permanentWalls, '#C8C80F', 6, cellSize);

	// Если хотите включить сетку
	drawGrid(ctx, width, height, cellSize);
}
