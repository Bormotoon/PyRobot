/***************************************************************************
 *  canvasDrawing.js
 *
 *  Файл с вспомогательными функциями для рисования на Canvas:
 *  - clearCanvas
 *  - drawColoredCells
 *  - drawRobot
 *  - drawMarkers
 *  - drawWalls
 *  - drawGrid
 *  - drawField (общая)
 ***************************************************************************/

/**
 * Очищает canvas перед рисованием.
 * @param {HTMLCanvasElement} canvas
 * @param {CanvasRenderingContext2D} ctx
 */
export function clearCanvas(canvas, ctx) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

/**
 * Рисует раскрашенные клетки.
 * @param {CanvasRenderingContext2D} ctx
 * @param {Set<string>} coloredCells - Набор "x,y".
 * @param {number} cellSize
 */
export function drawColoredCells(ctx, coloredCells, cellSize) {
  ctx.fillStyle = 'gray';
  coloredCells.forEach(cell => {
    const [x, y] = cell.split(',').map(Number);
    ctx.fillRect((x + 1) * cellSize, (y + 1) * cellSize, cellSize, cellSize);
  });
}

/**
 * Рисует робота (ромб) на холсте.
 * @param {CanvasRenderingContext2D} ctx
 * @param {{x:number,y:number}} robotPos
 * @param {number} cellSize
 */
export function drawRobot(ctx, robotPos, cellSize) {
  const robotX = (robotPos.x + 1) * cellSize + cellSize / 2;
  const robotY = (robotPos.y + 1) * cellSize + cellSize / 2;
  const diamondSize = cellSize * 0.6; // масштаб робота

  ctx.fillStyle = '#FF4500';
  ctx.beginPath();
  ctx.moveTo(robotX, robotY - diamondSize / 2);
  ctx.lineTo(robotX + diamondSize / 2, robotY);
  ctx.lineTo(robotX, robotY + diamondSize / 2);
  ctx.lineTo(robotX - diamondSize / 2, robotY);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
}

/**
 * Рисует маркеры (маленькие белые кружочки).
 * @param {CanvasRenderingContext2D} ctx
 * @param {Object} markers - { "x,y": 1 }
 * @param {number} cellSize
 */
export function drawMarkers(ctx, markers, cellSize) {
  Object.keys(markers).forEach(key => {
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

/**
 * Рисует набор стен (обычные и постоянные).
 * @param {CanvasRenderingContext2D} ctx
 * @param {Set<string>} walls
 * @param {string} strokeStyle
 * @param {number} lineWidth
 * @param {number} cellSize
 */
export function drawWalls(ctx, walls, strokeStyle, lineWidth, cellSize) {
  ctx.strokeStyle = strokeStyle;
  ctx.lineWidth = lineWidth;
  walls.forEach(wall => {
    const [x1, y1, x2, y2] = wall.split(',').map(Number);
    ctx.beginPath();
    ctx.moveTo((x1 + 1) * cellSize, (y1 + 1) * cellSize);
    ctx.lineTo((x2 + 1) * cellSize, (y2 + 1) * cellSize);
    ctx.stroke();
  });
}

/**
 * Рисует сетку вокруг каждой клетки.
 * Можно включать или отключать по желанию.
 * @param {CanvasRenderingContext2D} ctx
 * @param {number} width
 * @param {number} height
 * @param {number} cellSize
 */
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
 * Основная функция, собирающая всё воедино.
 * @param {HTMLCanvasElement} canvas
 * @param {Object} params - Объект со всеми необходимыми параметрами.
 */
export function drawField(canvas, params) {
  const {
    coloredCells,
    robotPos,
    markers,
    walls,
    permanentWalls,
    width,
    height,
    cellSize
  } = params;

  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // 1. Очистка
  clearCanvas(canvas, ctx);

  // 2. Раскрасить ячейки
  drawColoredCells(ctx, coloredCells, cellSize);

  // 3. Робот
  drawRobot(ctx, robotPos, cellSize);

  // 4. Маркеры
  drawMarkers(ctx, markers, cellSize);

  // 5. Обычные стены (цвет '#C8C80F', толщина 8)
  drawWalls(ctx, walls, '#C8C80F', 8, cellSize);

  // 6. Постоянные стены (границы) — тот же цвет/толщина или можно другое
  drawWalls(ctx, permanentWalls, '#C8C80F', 8, cellSize);

  // 7. Сетка (при желании закомментировать)
  drawGrid(ctx, width, height, cellSize);
}
