/**
 * @file canvasDrawing.js
 * @description Модуль для рисования игрового поля симулятора робота на canvas.
 * Каждая клетка (x, y) отрисовывается по координатам (x * cellSize, y * cellSize).
 * Размер canvas равен (width * cellSize) x (height * cellSize).
 */

/**
 * Очищает canvas, удаляя все ранее нарисованные элементы.
 *
 * @param {HTMLCanvasElement} canvas - Элемент canvas, который нужно очистить.
 * @param {CanvasRenderingContext2D} ctx - Контекст рисования canvas.
 */
export function clearCanvas(canvas, ctx) {
	// Очищаем весь canvas от рисованных элементов
	ctx.clearRect(0, 0, canvas.width, canvas.height);
}

/**
 * Рисует закрашенные клетки на canvas.
 *
 * @param {CanvasRenderingContext2D} ctx - Контекст рисования canvas.
 * @param {Set<string>} coloredCells - Множество клеток, которые нужно закрасить. Каждая клетка представлена строкой "x,y".
 * @param {number} cellSize - Размер одной клетки в пикселях.
 */
export function drawColoredCells(ctx, coloredCells, cellSize) {
	// Устанавливаем серый цвет для закрашивания клеток
	ctx.fillStyle = 'gray';
	// Проходим по каждой клетке в множестве coloredCells
	coloredCells.forEach(cell => {
		// Преобразуем строку "x,y" в числовые координаты x и y
		const [x, y] = cell.split(',').map(Number);
		// Рисуем прямоугольник, соответствующий клетке
		ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
	});
}

/**
 * Рисует робота на canvas.
 *
 * @param {CanvasRenderingContext2D} ctx - Контекст рисования canvas.
 * @param {Object} robotPos - Позиция робота в виде объекта {x, y}.
 * @param {number} cellSize - Размер одной клетки в пикселях.
 */
export function drawRobot(ctx, robotPos, cellSize) {
	// Вычисляем координаты центра клетки, в которой находится робот,
	// чтобы ромб робота был отрисован внутри клетки
	const rx = (robotPos.x + 0.5) * cellSize;
	const ry = (robotPos.y + 0.5) * cellSize;
	// Размер робота (ромба) равен 60% от cellSize
	const dSize = cellSize * 0.6;

	// Устанавливаем цвет заполнения для робота
	ctx.fillStyle = '#FF4500';
	ctx.beginPath();
	// Рисуем ромб: верхняя точка
	ctx.moveTo(rx, ry - dSize / 2);
	// Правая точка
	ctx.lineTo(rx + dSize / 2, ry);
	// Нижняя точка
	ctx.lineTo(rx, ry + dSize / 2);
	// Левая точка
	ctx.lineTo(rx - dSize / 2, ry);
	// Замыкаем путь и заполняем ромб
	ctx.closePath();
	ctx.fill();
	// Отрисовываем контур ромба
	ctx.stroke();
}

/**
 * Рисует маркеры на поле.
 *
 * @param {CanvasRenderingContext2D} ctx - Контекст рисования canvas.
 * @param {Object} markers - Объект с маркерами, где ключами являются строки с координатами "x,y".
 * @param {number} cellSize - Размер одной клетки в пикселях.
 */
export function drawMarkers(ctx, markers, cellSize) {
	// Проходим по всем ключам объекта markers
	Object.keys(markers).forEach(key => {
		// Преобразуем ключ "x,y" в числовые координаты
		const [x, y] = key.split(',').map(Number);
		// Устанавливаем белый цвет для заполнения маркера
		ctx.fillStyle = 'white';
		ctx.beginPath();
		// Рисуем круг (маркер) в правой нижней части клетки
		ctx.arc((x + 0.75) * cellSize, // x-координата центра маркера
			(y + 0.75) * cellSize, // y-координата центра маркера
			cellSize * 0.15,       // Радиус маркера
			0, 2 * Math.PI);
		ctx.fill();
		// Настраиваем стиль обводки для маркера
		ctx.strokeStyle = 'black';
		ctx.lineWidth = 1;
		ctx.stroke();
	});
}

/**
 * Рисует стены на canvas.
 *
 * @param {CanvasRenderingContext2D} ctx - Контекст рисования canvas.
 * @param {Set<string>} walls - Множество стен. Каждая стена представлена строкой "x1,y1,x2,y2".
 * @param {string} strokeStyle - Цвет линии для отрисовки стен.
 * @param {number} lineWidth - Толщина линии.
 * @param {number} cellSize - Размер одной клетки в пикселях.
 */
export function drawWalls(ctx, walls, strokeStyle, lineWidth, cellSize) {
	// Устанавливаем цвет и толщину линии для стен
	ctx.strokeStyle = strokeStyle;
	ctx.lineWidth = lineWidth;
	// Проходим по каждой стене из множества walls
	walls.forEach(wall => {
		// Преобразуем строку с координатами стены в числа
		const [x1, y1, x2, y2] = wall.split(',').map(Number);
		ctx.beginPath();
		// Перемещаемся к началу стены
		ctx.moveTo(x1 * cellSize, y1 * cellSize);
		// Рисуем линию до конечной точки стены
		ctx.lineTo(x2 * cellSize, y2 * cellSize);
		ctx.stroke();
	});
}

/**
 * Рисует сетку поля на canvas.
 *
 * @param {CanvasRenderingContext2D} ctx - Контекст рисования canvas.
 * @param {number} width - Ширина поля в количестве клеток.
 * @param {number} height - Высота поля в количестве клеток.
 * @param {number} cellSize - Размер одной клетки в пикселях.
 */
export function drawGrid(ctx, width, height, cellSize) {
	// Устанавливаем стиль линии для сетки
	ctx.strokeStyle = '#C8C80F';
	ctx.lineWidth = 1;
	// Рисуем прямоугольники для каждой ячейки поля
	for (let x = 0; x <= width; x++) {
		for (let y = 0; y <= height; y++) {
			ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
		}
	}
}

/**
 * Отрисовывает всё поле на canvas, включая закрашенные клетки, робота, маркеры, стены и сетку.
 *
 * @param {HTMLCanvasElement} canvas - Элемент canvas для рисования.
 * @param {Object} config - Объект с параметрами поля.
 * @param {Set<string>} config.coloredCells - Множество закрашенных клеток.
 * @param {Object} config.robotPos - Позиция робота в виде объекта {x, y}.
 * @param {Object} config.markers - Объект с маркерами на поле.
 * @param {Set<string>} config.walls - Множество временных стен.
 * @param {Set<string>} config.permanentWalls - Множество постоянных стен.
 * @param {number} config.width - Ширина поля в количестве клеток.
 * @param {number} config.height - Высота поля в количестве клеток.
 * @param {number} config.cellSize - Размер одной клетки в пикселях.
 */
export function drawField(canvas, {
	coloredCells, robotPos, markers, walls, permanentWalls, width, height, cellSize
}) {
	// Если canvas недоступен, прерываем выполнение функции
	if (!canvas) return;
	// Получаем 2D-контекст для рисования на canvas
	const ctx = canvas.getContext('2d');

	// Очищаем canvas перед началом отрисовки
	clearCanvas(canvas, ctx);

	// Рисуем закрашенные клетки
	drawColoredCells(ctx, coloredCells, cellSize);
	// Рисуем робота
	drawRobot(ctx, robotPos, cellSize);
	// Рисуем маркеры
	drawMarkers(ctx, markers, cellSize);

	// Рисуем временные и постоянные стены
	drawWalls(ctx, walls, '#C8C80F', 6, cellSize);
	drawWalls(ctx, permanentWalls, '#C8C80F', 6, cellSize);

	// Рисуем сетку поля
	drawGrid(ctx, width, height, cellSize);
}
