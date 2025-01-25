// /frontend/src/canvasDrawing.js

/**
 * Набор функций для рисования на Canvas:
 * - clearCanvas
 * - drawColoredCells
 * - drawRobot
 * - drawMarkers
 * - drawWalls
 * - drawGrid
 * - drawField
 */

export function clearCanvas(canvas, ctx) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

export function drawColoredCells(ctx, coloredCells, cellSize) {
  ctx.fillStyle = 'gray';
  coloredCells.forEach(cell => {
    const [x, y] = cell.split(',').map(Number);
    ctx.fillRect((x + 1) * cellSize, (y + 1) * cellSize, cellSize, cellSize);
  });
}

export function drawRobot(ctx, robotPos, cellSize) {
  const rx = (robotPos.x + 1) * cellSize + cellSize / 2;
  const ry = (robotPos.y + 1) * cellSize + cellSize / 2;
  const dSize = cellSize * 0.6;

  ctx.fillStyle = '#FF4500';
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
  Object.keys(markers).forEach((key) => {
    const [x, y] = key.split(',').map(Number);
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(
      (x + 1.75) * cellSize,
      (y + 1.75) * cellSize,
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
  walls.forEach((wall) => {
    const [x1, y1, x2, y2] = wall.split(',').map(Number);
    ctx.beginPath();
    ctx.moveTo((x1 + 1) * cellSize, (y1 + 1) * cellSize);
    ctx.lineTo((x2 + 1) * cellSize, (y2 + 1) * cellSize);
    ctx.stroke();
  });
}

export function drawGrid(ctx, width, height, cellSize) {
  ctx.strokeStyle = '#C8C80F';
  ctx.lineWidth = 2;
  for (let x = 0; x <= width + 2; x++) {
    for (let y = 0; y <= height + 2; y++) {
      ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
    }
  }
}

/**
 * drawField - вызывается в useEffect Field.jsx
 */
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

  // Обычные стены
  drawWalls(ctx, walls, '#C8C80F', 8, cellSize);
  // Постоянные стены (границы)
  drawWalls(ctx, permanentWalls, '#C8C80F', 8, cellSize);

  // Сетка
  drawGrid(ctx, width, height, cellSize);
}
