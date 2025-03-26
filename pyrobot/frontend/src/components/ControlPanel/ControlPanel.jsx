/**
 * @file ControlPanel.jsx
 * @description Компонент панели управления симулятором робота.
 * Позволяет управлять перемещением робота, маркерами, окраской клеток и размерами поля.
 */

import React, {memo, useCallback, useRef, useState} from 'react';
import {Button, Card, CardContent, CardHeader, Grid, Tooltip} from '@mui/material'; // Added Tooltip
import {
	Add as AddIcon,
	AddLocation as AddLocationIcon,
	ArrowBack as ArrowBackIcon,
	ArrowDownward as ArrowDownwardIcon,
	ArrowForward as ArrowForwardIcon,
	ArrowUpward as ArrowUpwardIcon,
	Brush as BrushIcon,
	Clear as ClearIcon,
	DeleteOutline as DeleteOutlineIcon,
	Edit as EditIcon,
	FileUpload as FileUploadIcon,
	HelpOutline as HelpOutlineIcon,
	Remove as RemoveIcon,
} from '@mui/icons-material';
import {getHint} from '../hints';
import './ControlPanel.css';
import HelpDialog from '../Help/HelpDialog';
import logger from '../../Logger'; // Correct path assumed

// Helper function to parse wall code from .fil file
const parseWallCode = (code, x, y) => {
	const wallSegments = [];
	// Bit flags: 8=Top, 4=Right, 2=Bottom, 1=Left
	if (code & 8) wallSegments.push(`${x},${y},${x + 1},${y}`);         // Top wall of cell (x, y)
	if (code & 4) wallSegments.push(`${x + 1},${y},${x + 1},${y + 1}`); // Right wall of cell (x, y)
	if (code & 2) wallSegments.push(`${x},${y + 1},${x + 1},${y + 1}`); // Bottom wall of cell (x, y)
	if (code & 1) wallSegments.push(`${x},${y},${x},${y + 1}`);         // Left wall of cell (x, y)
	return wallSegments;
};

const ControlPanel = memo(({
	                           robotPos,
	                           setRobotPos,
	                           walls, // User-defined walls
	                           setWalls,
	                           permanentWalls, // Boundary walls
	                           markers,
	                           setMarkers,
	                           coloredCells,
	                           setColoredCells,
	                           width,
	                           setWidth,
	                           height,
	                           setHeight,
	                           // cellSize is now managed by Field component via zoom
	                           // setCellSize,
	                           editMode,
	                           setEditMode,
	                           setStatusMessage,
                           }) => {
	const fileInputRef = useRef(null);
	const [helpOpen, setHelpOpen] = useState(false);

	/**
	 * Check if a move from (x, y) in a given direction is blocked by a wall.
	 * Walls are represented as strings "x1,y1,x2,y2".
	 * permanentWalls contains the outer boundary walls.
	 * walls contains user-defined inner walls.
	 */
	const isBlocked = useCallback((x, y, direction) => {
		let wallKey = '';
		switch (direction) {
			case 'up':
				if (y <= 0) return true; // Blocked by top boundary implicitly handled by permanentWalls
				wallKey = `${x},${y},${x + 1},${y}`; // Horizontal wall between (x, y-1) and (x, y)
				break;
			case 'down':
				if (y >= height - 1) return true; // Blocked by bottom boundary
				wallKey = `${x},${y + 1},${x + 1},${y + 1}`; // Horizontal wall between (x, y) and (x, y+1)
				break;
			case 'left':
				if (x <= 0) return true; // Blocked by left boundary
				wallKey = `${x},${y},${x},${y + 1}`; // Vertical wall between (x-1, y) and (x, y)
				break;
			case 'right':
				if (x >= width - 1) return true; // Blocked by right boundary
				wallKey = `${x + 1},${y},${x + 1},${y + 1}`; // Vertical wall between (x, y) and (x+1, y)
				break;
			default:
				return true; // Unknown direction is blocked
		}
		return permanentWalls.has(wallKey) || walls.has(wallKey);
	}, [walls, permanentWalls, width, height]);

	/**
	 * Function to attempt moving the robot.
	 * @param {string} direction - 'up', 'down', 'left', or 'right'.
	 */
	const moveRobot = useCallback((direction) => {
		let {x, y} = robotPos;
		let newX = x, newY = y;
		let moveBlocked = false;
		let hintKeySuccess = '';
		let hintKeyBlocked = '';
		let logDirection = '';

		switch (direction) {
			case 'up':
				hintKeySuccess = 'moveRobotUp';
				hintKeyBlocked = 'moveRobotUpBlocked';
				logDirection = 'вверх';
				if (!isBlocked(x, y, 'up')) newY--; else moveBlocked = true;
				break;
			case 'down':
				hintKeySuccess = 'moveRobotDown';
				hintKeyBlocked = 'moveRobotDownBlocked';
				logDirection = 'вниз';
				if (!isBlocked(x, y, 'down')) newY++; else moveBlocked = true;
				break;
			case 'left':
				hintKeySuccess = 'moveRobotLeft';
				hintKeyBlocked = 'moveRobotLeftBlocked';
				logDirection = 'влево';
				if (!isBlocked(x, y, 'left')) newX--; else moveBlocked = true;
				break;
			case 'right':
				hintKeySuccess = 'moveRobotRight';
				hintKeyBlocked = 'moveRobotRightBlocked';
				logDirection = 'вправо';
				if (!isBlocked(x, y, 'right')) newX++; else moveBlocked = true;
				break;
			default:
				logger.log_error(`Неизвестное направление движения: ${direction}`);
				return;
		}

		if (moveBlocked) {
			setStatusMessage(getHint(hintKeyBlocked, editMode));
			logger.log_movement(`Попытка перемещения ${logDirection} заблокирована. Позиция: (${x}, ${y})`);
		} else {
			const newPos = {x: newX, y: newY};
			setRobotPos(newPos); // Update state
			setStatusMessage(getHint(hintKeySuccess, editMode));
			logger.log_movement(`Робот перемещён ${logDirection}. Новая позиция: (${newX}, ${newY})`);
		}
	}, [robotPos, isBlocked, editMode, setRobotPos, setStatusMessage, logger]); // Added logger to dependencies

	// --- Marker and Cell Manipulation ---

	const putMarker = useCallback(() => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (markers[posKey]) {
			setStatusMessage(getHint('markerAlreadyExists', editMode));
			logger.log_marker(`Попытка поставить маркер, но он уже есть в (${robotPos.x}, ${robotPos.y})`);
		} else {
			// Use functional update for safety if needed, though direct is often fine here
			setMarkers(prev => ({...prev, [posKey]: 1}));
			setStatusMessage(getHint('putMarker', editMode));
			logger.log_marker(`Маркер установлен в позиции: (${robotPos.x}, ${robotPos.y})`);
		}
	}, [robotPos, markers, setMarkers, setStatusMessage, editMode, logger]);

	const pickMarker = useCallback(() => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (!markers[posKey]) {
			setStatusMessage(getHint('noMarkerHere', editMode));
			logger.log_marker(`Попытка поднять маркер, но его нет в (${robotPos.x}, ${robotPos.y})`);
		} else {
			setMarkers(prev => {
				const newMarkers = {...prev};
				delete newMarkers[posKey];
				return newMarkers;
			});
			setStatusMessage(getHint('pickMarker', editMode));
			logger.log_marker(`Маркер снят из позиции: (${robotPos.x}, ${robotPos.y})`);
		}
	}, [robotPos, markers, setMarkers, setStatusMessage, editMode, logger]);

	const paintCell = useCallback(() => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (coloredCells.has(posKey)) {
			setStatusMessage(getHint('cellAlreadyPainted', editMode));
			logger.log_cell(`Попытка закрасить клетку (${robotPos.x}, ${robotPos.y}), но она уже закрашена.`);
		} else {
			setColoredCells(prev => new Set(prev).add(posKey));
			setStatusMessage(getHint('paintCell', editMode));
			logger.log_cell(`Клетка (${robotPos.x}, ${robotPos.y}) закрашена.`);
		}
	}, [robotPos, coloredCells, setColoredCells, setStatusMessage, editMode, logger]);

	const clearCell = useCallback(() => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (!coloredCells.has(posKey)) {
			setStatusMessage(getHint('cellAlreadyClear', editMode));
			logger.log_cell(`Попытка очистить клетку (${robotPos.x}, ${robotPos.y}), но она уже чистая.`);
		} else {
			setColoredCells(prev => {
				const newColored = new Set(prev);
				newColored.delete(posKey);
				return newColored;
			});
			setStatusMessage(getHint('clearCell', editMode));
			logger.log_cell(`Клетка (${robotPos.x}, ${robotPos.y}) очищена.`);
		}
	}, [robotPos, coloredCells, setColoredCells, setStatusMessage, editMode, logger]);

	// --- Edit Mode and Dimensions ---

	const toggleEditMode = useCallback(() => {
		const newMode = !editMode;
		setEditMode(newMode);
		const hintKey = newMode ? 'enterEditMode' : 'exitEditMode';
		setStatusMessage(getHint(hintKey, newMode));
		logger.log_edit_mode_change(newMode);
	}, [editMode, setEditMode, setStatusMessage, logger]);

	const changeDimension = useCallback((dim, delta) => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', false)); // Pass false as editMode is off
			logger.log_event(`Попытка изменить размер поля (${dim}) вне режима редактирования.`);
			return;
		}

		let currentValue = dim === 'width' ? width : height;
		let newValue = currentValue + delta;
		let setter = dim === 'width' ? setWidth : setHeight;
		let limitMsgKey = dim === 'width' ? 'widthCannotBeLessThan1' : 'heightCannotBeLessThan1';
		let increaseHintKey = dim === 'width' ? 'increaseWidth' : 'increaseHeight';
		let decreaseHintKey = dim === 'width' ? 'decreaseWidth' : 'decreaseHeight';

		if (newValue < 1) {
			setStatusMessage(getHint(limitMsgKey, true)); // Pass true as we are in edit mode
			logger.log_dimension(`Попытка уменьшить ${dim} ниже 1.`);
		} else {
			setter(newValue);
			const hintKey = delta > 0 ? increaseHintKey : decreaseHintKey;
			setStatusMessage(getHint(hintKey, true));
			logger.log_dimension_change(dim, currentValue, newValue);
		}
	}, [editMode, width, height, setWidth, setHeight, setStatusMessage, logger]);

	const increaseWidth = useCallback(() => changeDimension('width', 1), [changeDimension]);
	const decreaseWidth = useCallback(() => changeDimension('width', -1), [changeDimension]);
	const increaseHeight = useCallback(() => changeDimension('height', 1), [changeDimension]);
	const decreaseHeight = useCallback(() => changeDimension('height', -1), [changeDimension]);

	// --- File Import ---

	const handleImportClick = useCallback(() => {
		if (fileInputRef.current) {
			fileInputRef.current.click(); // Trigger hidden file input
		}
	}, [fileInputRef]);

	const handleFileChange = useCallback(async (e) => {
		const file = e.target.files?.[0];
		if (!file) return;

		try {
			const content = await file.text();
			logger.log_fileimport(`Чтение файла '${file.name}' начато.`);
			parseAndApplyFieldFile(content, file.name);
			setStatusMessage(getHint('importSuccess', editMode));
			logger.log_file_import_success(file.name);
		} catch (error) {
			const errMsg = error instanceof Error ? error.message : String(error);
			setStatusMessage(getHint('importError', editMode) + errMsg);
			logger.log_file_import_error(file.name, errMsg);
		} finally {
			// Reset input value to allow importing the same file again
			if (e.target) {
				e.target.value = "";
			}
		}
	}, [editMode, setWidth, setHeight, setRobotPos, setWalls, setColoredCells, setMarkers, setStatusMessage, logger]); // Dependencies for file handling

	const parseAndApplyFieldFile = useCallback((content, filename = "unknown") => {
		// Basic validation first
		if (!content || typeof content !== 'string') {
			throw new Error('Содержимое файла пустое или недействительное.');
		}

		try {
			const lines = content.split('\n')
				.map(line => line.replace(/#.*$/, '').trim()) // Remove comments and trim
				.filter(line => line !== ''); // Remove empty lines

			if (lines.length < 2) throw new Error('Недостаточно строк данных (требуется как минимум 2).');

			// Line 1: Dimensions
			const dimensions = lines[0].split(/\s+/).map(Number);
			if (dimensions.length < 2 || isNaN(dimensions[0]) || isNaN(dimensions[1]) || dimensions[0] < 1 || dimensions[1] < 1) {
				throw new Error('Неверный формат размеров поля в первой строке.');
			}
			const [fileWidth, fileHeight] = dimensions;

			// Line 2: Robot Position
			const robotCoords = lines[1].split(/\s+/).map(Number);
			if (robotCoords.length < 2 || isNaN(robotCoords[0]) || isNaN(robotCoords[1])) {
				throw new Error('Неверный формат координат робота во второй строке.');
			}
			const [robotX, robotY] = robotCoords;

			// Clamp robot position to new dimensions BEFORE setting state
			const clampedRobotPos = {
				x: Math.min(Math.max(0, robotX), fileWidth - 1),
				y: Math.min(Math.max(0, robotY), fileHeight - 1)
			};


			const importedWalls = new Set();
			const importedColored = new Set();
			const importedMarkers = {};

			// Process remaining lines for cell data
			if (lines.length !== 2 + fileWidth * fileHeight) {
				logger.log_warning(`Количество строк данных (${lines.length - 2}) не соответствует размеру поля ${fileWidth}x${fileHeight}. Некоторые данные могут отсутствовать.`);
			}

			for (let i = 2; i < lines.length; i++) {
				const parts = lines[i].split(/\s+/);
				if (parts.length < 9) {
					logger.log_warning(`Строка ${i + 1} имеет неверное количество полей (${parts.length}), пропускается.`);
					continue; // Skip malformed lines
				}

				const cellX = parseInt(parts[0], 10);
				const cellY = parseInt(parts[1], 10);
				const wallCode = parseInt(parts[2], 10);
				const colorFlag = parts[3]; // '0' or '1'
				// parts[4] to parts[7] seem unused in the original example
				const markerFlag = parts[8]; // '0' or '1'

				// Basic sanity checks
				if (isNaN(cellX) || isNaN(cellY) || isNaN(wallCode) || cellX < 0 || cellY < 0 || cellX >= fileWidth || cellY >= fileHeight) {
					logger.log_warning(`Строка ${i + 1} содержит неверные координаты или код стены, пропускается.`);
					continue;
				}

				const cellKey = `${cellX},${cellY}`;

				// Add colored cell if flag is '1'
				if (colorFlag === '1') {
					importedColored.add(cellKey);
				}

				// Add marker if flag is '1'
				if (markerFlag === '1') {
					importedMarkers[cellKey] = 1; // Store marker
				}

				// Parse and add wall segments
				const wallsToAdd = parseWallCode(wallCode, cellX, cellY);
				wallsToAdd.forEach(w => importedWalls.add(w));
			}

			// Update state: Set dimensions first, then robot position, then field elements
			setWidth(fileWidth);
			setHeight(fileHeight);
			setRobotPos(clampedRobotPos); // Use clamped position
			setWalls(importedWalls);
			setColoredCells(importedColored);
			setMarkers(importedMarkers);
			// No need to set permanent walls, they will be updated by useEffect in RobotSimulator based on new width/height

			setStatusMessage(`Поле (${fileWidth}x${fileHeight}) успешно загружено из файла ${filename}.`);
			logger.log_event(`Импорт поля ${filename} (${fileWidth}x${fileHeight}) завершен.`);

		} catch (error) {
			const errMsg = error instanceof Error ? error.message : String(error);
			logger.log_error(`Ошибка парсинга файла '${filename}': ${errMsg}`);
			// Re-throw a more specific error for the caller to catch
			throw new Error(`Ошибка разбора файла ${filename}: ${errMsg}`);
		}
	}, [setWidth, setHeight, setRobotPos, setWalls, setColoredCells, setMarkers, setStatusMessage, logger]); // Dependencies for parsing logic

	// --- Help Dialog ---
	const openHelpDialog = useCallback(() => setHelpOpen(true), []);
	const closeHelpDialog = useCallback(() => setHelpOpen(false), []);

	// --- Rendering ---
	return (
		<>
			<Card className="control-panel" elevation={3}>
				<CardHeader title="Панель управления"/>
				<CardContent>
					{/* Robot Movement Controls */}
					<Grid container spacing={1} justifyContent="center" alignItems="center" className="control-section">
						<Grid item xs={12} container justifyContent="center">
							<Tooltip title="Переместить робота вверх">
								<Button onClick={() => moveRobot('up')} color="primary" variant="contained"
								        className="control-button small-button" aria-label="Вверх"> <ArrowUpwardIcon/>
								</Button>
							</Tooltip>
						</Grid>
						<Grid item xs={4} container justifyContent="flex-end">
							<Tooltip title="Переместить робота влево">
								<Button onClick={() => moveRobot('left')} color="primary" variant="contained"
								        className="control-button small-button" aria-label="Влево"> <ArrowBackIcon/>
								</Button>
							</Tooltip>
						</Grid>
						<Grid item xs={4} container justifyContent="center">
							{/* Placeholder or Icon in the middle */}
						</Grid>
						<Grid item xs={4} container justifyContent="flex-start">
							<Tooltip title="Переместить робота вправо">
								<Button onClick={() => moveRobot('right')} color="primary" variant="contained"
								        className="control-button small-button" aria-label="Вправо"> <ArrowForwardIcon/>
								</Button>
							</Tooltip>
						</Grid>
						<Grid item xs={12} container justifyContent="center">
							<Tooltip title="Переместить робота вниз">
								<Button onClick={() => moveRobot('down')} color="primary" variant="contained"
								        className="control-button small-button" aria-label="Вниз"> <ArrowDownwardIcon/>
								</Button>
							</Tooltip>
						</Grid>
					</Grid>

					{/* Marker and Paint Controls */}
					<Grid container spacing={1} className="control-section">
						<Grid item xs={6}>
							<Tooltip title="Положить маркер в текущей клетке">
								<Button onClick={putMarker} startIcon={<AddLocationIcon/>} color="success"
								        variant="contained" fullWidth className="control-button"
								        aria-label="Положить маркер"> Маркер </Button>
							</Tooltip>
						</Grid>
						<Grid item xs={6}>
							<Tooltip title="Поднять маркер из текущей клетки">
								<Button onClick={pickMarker} startIcon={<DeleteOutlineIcon/>} color="error"
								        variant="contained" fullWidth className="control-button"
								        aria-label="Поднять маркер"> Маркер </Button>
							</Tooltip>
						</Grid>
						<Grid item xs={6}>
							<Tooltip title="Закрасить текущую клетку">
								<Button onClick={paintCell} startIcon={<BrushIcon/>} color="warning" variant="contained"
								        fullWidth className="control-button" aria-label="Покрасить"> Клетка </Button>
							</Tooltip>
						</Grid>
						<Grid item xs={6}>
							<Tooltip title="Очистить текущую клетку">
								<Button onClick={clearCell} startIcon={<ClearIcon/>} color="info" variant="contained"
								        fullWidth className="control-button" aria-label="Очистить"> Клетка </Button>
							</Tooltip>
						</Grid>
					</Grid>

					{/* Edit Mode and Dimensions Controls */}
					<Grid container spacing={1} className="control-section">
						<Grid item xs={12}>
							<Tooltip
								title={editMode ? 'Выключить режим редактирования поля мышью' : 'Включить режим редактирования поля мышью'}>
								<Button onClick={toggleEditMode} startIcon={<EditIcon/>}
								        color={editMode ? "secondary" : "primary"} variant="contained" fullWidth
								        className="control-button" aria-label="Режим рисования">
									{editMode ? 'Выкл. Ред.' : 'Вкл. Ред.'}
								</Button>
							</Tooltip>
						</Grid>
						<Grid item xs={6}>
							<Tooltip title="Увеличить ширину поля (только в режиме ред.)">
								<Button onClick={increaseWidth} startIcon={<AddIcon/>} color="primary"
								        variant="outlined" fullWidth className="control-button" disabled={!editMode}
								        aria-label="Поле шире"> Шире </Button>
							</Tooltip>
						</Grid>
						<Grid item xs={6}>
							<Tooltip title="Уменьшить ширину поля (только в режиме ред.)">
								<Button onClick={decreaseWidth} startIcon={<RemoveIcon/>} color="primary"
								        variant="outlined" fullWidth className="control-button"
								        disabled={!editMode || width <= 1} aria-label="Поле уже"> Уже </Button>
							</Tooltip>
						</Grid>
						<Grid item xs={6}>
							<Tooltip title="Увеличить высоту поля (только в режиме ред.)">
								<Button onClick={increaseHeight} startIcon={<AddIcon/>} color="primary"
								        variant="outlined" fullWidth className="control-button" disabled={!editMode}
								        aria-label="Поле выше"> Выше </Button>
							</Tooltip>
						</Grid>
						<Grid item xs={6}>
							<Tooltip title="Уменьшить высоту поля (только в режиме ред.)">
								<Button onClick={decreaseHeight} startIcon={<RemoveIcon/>} color="primary"
								        variant="outlined" fullWidth className="control-button"
								        disabled={!editMode || height <= 1} aria-label="Поле ниже"> Ниже </Button>
							</Tooltip>
						</Grid>
					</Grid>

					{/* Help and Import */}
					<Grid container spacing={1} className="control-section">
						<Grid item xs={6}>
							<Tooltip title="Открыть справку">
								<Button onClick={openHelpDialog} startIcon={<HelpOutlineIcon/>} color="info"
								        variant="text" fullWidth className="control-button"
								        aria-label="Помощь"> Помощь </Button>
							</Tooltip>
						</Grid>
						<Grid item xs={6}>
							<Tooltip title="Импортировать поле из файла .fil">
								<Button onClick={handleImportClick} startIcon={<FileUploadIcon/>} color="secondary"
								        variant="text" fullWidth className="control-button"
								        aria-label="Импорт .fil"> Импорт .fil </Button>
							</Tooltip>
							<input
								type="file"
								accept=".fil" // Specify acceptable file type
								ref={fileInputRef}
								style={{display: 'none'}} // Hidden input
								onChange={handleFileChange}
							/>
						</Grid>
					</Grid>
				</CardContent>
			</Card>
			{/* Help Dialog Component */}
			<HelpDialog open={helpOpen} onClose={closeHelpDialog}/>
		</>
	);
});

export default ControlPanel;