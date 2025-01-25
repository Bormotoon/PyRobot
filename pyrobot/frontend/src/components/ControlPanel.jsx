// /frontend/src/components/ControlPanel.jsx

import React, {useRef} from 'react';
import {Button, Card, CardContent, CardHeader, Grid, Typography} from '@mui/material';
import {ChevronDown, ChevronLeft, ChevronRight, ChevronUp} from 'lucide-react';

/**
 * Панель управления роботом (кнопки движения),
 * маркерами, покраской, режимом рисования,
 * изменением размеров поля, импортом .fil.
 */
function ControlPanel({
	                      robotPos,
	                      setRobotPos,
	                      walls,
	                      setWalls,
	                      markers,
	                      setMarkers,
	                      coloredCells,
	                      setColoredCells,
	                      width,
	                      setWidth,
	                      height,
	                      setHeight,
	                      cellSize,
	                      setCellSize,
	                      editMode,
	                      setEditMode,
	                      setStatusMessage
                      }) {

	const fileInputRef = useRef(null);

	/**
	 * moveRobot(direction) — двигаем робота на 1 клетку, проверяя стены и границы
	 */
	const moveRobot = (direction) => {
		const {x, y} = robotPos;
		let newX = x;
		let newY = y;

		if (direction === 'up') newY -= 1;
		if (direction === 'down') newY += 1;
		if (direction === 'left') newX -= 1;
		if (direction === 'right') newX += 1;

		// проверка границ
		if (newX < 0 || newX >= width || newY < 0 || newY >= height) {
			setStatusMessage('Робот не может выйти за границу поля.');
			return;
		}
		// проверка стены
		const wallKey = `${Math.min(x, newX)},${Math.min(y, newY)},${Math.max(x, newX)},${Math.max(y, newY)}`;
		if (walls.has(wallKey)) {
			setStatusMessage('Робот не может пройти сквозь стену.');
			return;
		}

		setRobotPos({x: newX, y: newY});
		setStatusMessage('Робот перемещён кнопкой!');
	};

	/**
	 * Положить маркер в текущую клетку
	 */
	const putMarker = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (!markers[posKey]) {
			const newMarkers = {...markers};
			newMarkers[posKey] = 1;
			setMarkers(newMarkers);
			setStatusMessage('Маркер положен.');
		} else {
			setStatusMessage('Тут уже есть маркер.');
		}
	};

	/**
	 * Поднять маркер
	 */
	const pickMarker = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (markers[posKey]) {
			const newMarkers = {...markers};
			delete newMarkers[posKey];
			setMarkers(newMarkers);
			setStatusMessage('Маркер поднят.');
		} else {
			setStatusMessage('Здесь нет маркера.');
		}
	};

	/**
	 * Покрасить клетку
	 */
	const paintCell = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (!coloredCells.has(posKey)) {
			const newSet = new Set(coloredCells);
			newSet.add(posKey);
			setColoredCells(newSet);
			setStatusMessage('Клетка покрашена!');
		} else {
			setStatusMessage('Клетка уже покрашена.');
		}
	};

	/**
	 * Очистить клетку
	 */
	const clearCell = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (coloredCells.has(posKey)) {
			const newSet = new Set(coloredCells);
			newSet.delete(posKey);
			setColoredCells(newSet);
			setStatusMessage('Клетка очищена.');
		} else {
			setStatusMessage('Эта клетка и так не была покрашена.');
		}
	};

	/**
	 * Переключить режим рисования
	 */
	const toggleEditMode = () => {
		const newMode = !editMode;
		setEditMode(newMode);
		if (newMode) {
			setStatusMessage('Режим рисования включён.');
		} else {
			setStatusMessage('Режим рисования выключен.');
		}
	};

	/**
	 * Увеличить/уменьшить ширину поля
	 */
	const increaseWidth = () => {
		if (!editMode) {
			setStatusMessage('Включите режим рисования для изменения поля.');
			return;
		}
		setWidth(width + 1);
		setStatusMessage('Поле расширено.');
	};

	const decreaseWidth = () => {
		if (!editMode) {
			setStatusMessage('Включите режим рисования для изменения поля.');
			return;
		}
		if (width > 1) {
			setWidth(width - 1);
			setStatusMessage('Поле сужено.');
		} else {
			setStatusMessage('Ширина не может быть меньше 1.');
		}
	};

	/**
	 * Увеличить/уменьшить высоту поля
	 */
	const increaseHeight = () => {
		if (!editMode) {
			setStatusMessage('Включите режим рисования для изменения поля.');
			return;
		}
		setHeight(height + 1);
		setStatusMessage('Поле увеличено по высоте.');
	};

	const decreaseHeight = () => {
		if (!editMode) {
			setStatusMessage('Включите режим рисования для изменения поля.');
			return;
		}
		if (height > 1) {
			setHeight(height - 1);
			setStatusMessage('Поле уменьшено по высоте.');
		} else {
			setStatusMessage('Высота не может быть меньше 1.');
		}
	};

	/**
	 * Импорт .fil
	 */
	const handleImportField = () => {
		fileInputRef.current.click();
	};

	const handleFileChange = async (e) => {
		const file = e.target.files[0];
		if (!file) return;
		try {
			const content = await file.text();
			parseAndApplyFieldFile(content);
			setStatusMessage('Обстановка успешно импортирована!');
		} catch (error) {
			setStatusMessage('Ошибка импорта: ' + error.message);
		}
	};

	/**
	 * parseAndApplyFieldFile(content)
	 * Разбирает файл .fil и применяет к состоянию (width, height, robotPos, walls и т.д.).
	 */
	const parseAndApplyFieldFile = (content) => {
		try {
			// Сбрасываем поле перед загрузкой
			setRobotPos({x: 0, y: 0});
			setWalls(new Set());
			setColoredCells(new Set());
			setMarkers({});

			const lines = content.split('\n').filter(line => {
				return !line.startsWith(';') && line.trim() !== '';
			});

			// Первая строка: размеры
			const [wFile, hFile] = lines[0].split(/\s+/).map(Number);
			setWidth(wFile);
			setHeight(hFile);

			// Вторая строка: позиция робота
			const [rx, ry] = lines[1].split(/\s+/).map(Number);
			setRobotPos({x: rx, y: ry});

			const newWalls = new Set();
			const newColored = new Set();
			const newMarkers = {};

			for (let i = 2; i < lines.length; i++) {
				const parts = lines[i].split(/\s+/);
				const x = parseInt(parts[0], 10);
				const y = parseInt(parts[1], 10);
				const wallCode = parseInt(parts[2], 10);
				const color = parts[3];
				const point = parts[8];

				if (color === '1') {
					newColored.add(`${x},${y}`);
				}
				if (point === '1') {
					newMarkers[`${x},${y}`] = 1;
				}

				const wallsParsed = parseWallCode(wallCode, x, y);
				wallsParsed.forEach(w => newWalls.add(w));
			}

			setWalls(newWalls);
			setColoredCells(newColored);
			setMarkers(newMarkers);
		} catch (error) {
			setStatusMessage('Ошибка парсинга .fil: ' + error.message);
		}
	};

	const parseWallCode = (code, x, y) => {
		const arr = [];
		// 8 => верх, 4 => право, 2 => низ, 1 => лево
		if (code & 8) arr.push(`${x},${y},${x + 1},${y}`);
		if (code & 4) arr.push(`${x + 1},${y},${x + 1},${y + 1}`);
		if (code & 2) arr.push(`${x},${y + 1},${x + 1},${y + 1}`);
		if (code & 1) arr.push(`${x},${y},${x},${y + 1}`);
		return arr;
	};

	return (<Card className="card">
			<CardHeader
				title={<Typography variant="h6" style={{textAlign: 'center'}}>
					Управление
				</Typography>}
			/>
			<CardContent>
				<Grid container spacing={2} alignItems="center" justifyContent="center">
					<Grid item xs={4}></Grid>
					<Grid item xs={4}>
						<Button variant="contained" onClick={() => moveRobot('up')}>
							<ChevronUp/>
						</Button>
					</Grid>
					<Grid item xs={4}></Grid>

					<Grid item xs={4}>
						<Button variant="contained" onClick={() => moveRobot('left')}>
							<ChevronLeft/>
						</Button>
					</Grid>
					<Grid item xs={4}></Grid>
					<Grid item xs={4}>
						<Button variant="contained" onClick={() => moveRobot('right')}>
							<ChevronRight/>
						</Button>
					</Grid>

					<Grid item xs={4}></Grid>
					<Grid item xs={4}>
						<Button variant="contained" onClick={() => moveRobot('down')}>
							<ChevronDown/>
						</Button>
					</Grid>
					<Grid item xs={4}></Grid>

					<Grid item xs={6}>
						<Button
							variant="contained"
							onClick={putMarker}
							fullWidth
						>
							Положить маркер
						</Button>
					</Grid>
					<Grid item xs={6}>
						<Button
							variant="contained"
							onClick={pickMarker}
							fullWidth
						>
							Поднять маркер
						</Button>
					</Grid>
					<Grid item xs={6}>
						<Button
							variant="contained"
							onClick={paintCell}
							fullWidth
						>
							Покрасить
						</Button>
					</Grid>
					<Grid item xs={6}>
						<Button
							variant="contained"
							onClick={clearCell}
							fullWidth
						>
							Очистить
						</Button>
					</Grid>

					<Grid item xs={12}>
						<Button
							variant="outlined"
							onClick={toggleEditMode}
							fullWidth
						>
							{editMode ? 'Выключить Режим рисования' : 'Включить Режим рисования'}
						</Button>
					</Grid>

					<Grid item xs={6}>
						<Button
							variant="contained"
							onClick={increaseWidth}
							fullWidth
						>
							Поле шире
						</Button>
					</Grid>
					<Grid item xs={6}>
						<Button
							variant="contained"
							onClick={decreaseWidth}
							fullWidth
						>
							Поле уже
						</Button>
					</Grid>
					<Grid item xs={6}>
						<Button
							variant="contained"
							onClick={increaseHeight}
							fullWidth
						>
							Поле выше
						</Button>
					</Grid>
					<Grid item xs={6}>
						<Button
							variant="contained"
							onClick={decreaseHeight}
							fullWidth
						>
							Поле ниже
						</Button>
					</Grid>

					<Grid item xs={12}>
						<Button variant="contained" color="secondary" fullWidth>
							Помощь
						</Button>
					</Grid>

					<Grid item xs={12}>
						<Button
							variant="contained"
							color="secondary"
							onClick={handleImportField}
							fullWidth
						>
							Импорт .fil
						</Button>
						<input
							type="file"
							ref={fileInputRef}
							style={{display: 'none'}}
							accept=".fil"
							onChange={handleFileChange}
						/>
					</Grid>
				</Grid>
			</CardContent>
		</Card>);
}

export default ControlPanel;
