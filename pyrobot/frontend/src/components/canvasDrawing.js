/**
 * canvasDrawing.js
 *
 * Файл содержит вспомогательные функции для рисования на Canvas:
 * - clearCanvas: очищает холст
 * - drawColoredCells: закрашенные клетки
 * - drawRobot: рисует робота (ромб)
 * - drawMarkers: рисует маркеры (кружки)
 * - drawWalls: рисует линии-стены
 * - drawGrid: рисует сетку (опционально)
 * - drawField: объединяет всё вышеописанное
 */

/**
 * clearCanvas(canvas, ctx)
 * Полностью очищает область canvas.
 * @param {HTMLCanvasElement} canvas - элемент Canvas
 * @param {CanvasRenderingContext2D} ctx - контекст рисования
 */
export function clearCanvas(canvas, ctx) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

/**
 * drawColoredCells(ctx, coloredCells, cellSize)
 * Рисует клетки, которые были закрашены (цвет - серый).
 * @param {CanvasRenderingContext2D} ctx
 * @param {Set<string>} coloredCells - множество строк вида \"x,y\"
 * @param {number} cellSize - размер клетки (px)
 */
export function drawColoredCells(ctx, coloredCells, cellSize) {
  ctx.fillStyle = 'gray';
  coloredCells.forEach(cell => {
    const [x, y] = cell.split(',').map(Number);
    // Рисуем прямоугольник (x+1, y+1) чтобы оставить границу в 1 клетку
    ctx.fillRect((x + 1) * cellSize, (y + 1) * cellSize, cellSize, cellSize);
  });
}

/**
 * drawRobot(ctx, robotPos, cellSize)
 * Рисует робота в виде ромба (diamond shape) оранжевого цвета.
 * @param {CanvasRenderingContext2D} ctx
 * @param {{x:number,y:number}} robotPos
 * @param {number} cellSize
 */
export function drawRobot(ctx, robotPos, cellSize) {
  const rx = (robotPos.x + 1) * cellSize + cellSize / 2;
  const ry = (robotPos.y + 1) * cellSize + cellSize / 2;
  const dSize = cellSize * 0.6; // коэффициент размера робота

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

/**
 * drawMarkers(ctx, markers, cellSize)
 * Рисует белые кружочки-маркеры в клетках, где есть ключ \"x,y\" => 1.
 * @param {CanvasRenderingContext2D} ctx
 * @param {Object} markers - { \"x,y\": 1 }
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
 * drawWalls(ctx, walls, strokeStyle, lineWidth, cellSize)
 * Рисует линии-стены по набору \"x1,y1,x2,y2\".
 * @param {CanvasRenderingContext2D} ctx
 * @param {Set<string>} walls - множество строк вида \"x1,y1,x2,y2\"
 * @param {string} strokeStyle - цвет линии
 * @param {number} lineWidth - толщина линии
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
 * drawGrid(ctx, width, height, cellSize)
 * Рисует сетку (опционально, если хотите видеть границы клеток).
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
 * drawField(canvas, params)
 * Основная функция, объединяющая все остальные:
 *   - clearCanvas
 *   - drawColoredCells
 *   - drawRobot
 *   - drawMarkers
 *   - drawWalls (для обычных и постоянных)
 *   - drawGrid (опционально, если нужно)
 * @param {HTMLCanvasElement} canvas
 * @param {Object} params - объект со всеми нужными параметрами
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

  // Очищаем холст
  clearCanvas(canvas, ctx);

  // Рисуем закрашенные клетки
  drawColoredCells(ctx, coloredCells, cellSize);

  // Робот
  drawRobot(ctx, robotPos, cellSize);

  // Маркеры
  drawMarkers(ctx, markers, cellSize);

  // Обычные стены (жёлтый цвет, толщина 8)
  drawWalls(ctx, walls, '#C8C80F', 8, cellSize);

  // Постоянные стены (те же параметры)
  drawWalls(ctx, permanentWalls, '#C8C80F', 8, cellSize);

  // Сетка (если не нужна, можно закомментировать)
  drawGrid(ctx, width, height, cellSize);
}
