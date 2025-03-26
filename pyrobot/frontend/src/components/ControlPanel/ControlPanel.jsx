/**
 * @file ControlPanel.jsx
 * @description Компонент панели управления симулятором робота.
 */

import React, {memo, useCallback, useRef, useState} from 'react';
import {Button, Card, CardContent, CardHeader, Grid, Tooltip} from '@mui/material';
import {
	Add as AddIcon, AddLocation as AddLocationIcon, ArrowBack as ArrowBackIcon,
	ArrowDownward as ArrowDownwardIcon, ArrowForward as ArrowForwardIcon, ArrowUpward as ArrowUpwardIcon,
	Brush as BrushIcon, Clear as ClearIcon, DeleteOutline as DeleteOutlineIcon, Edit as EditIcon,
	FileUpload as FileUploadIcon, HelpOutline as HelpOutlineIcon, Remove as RemoveIcon
} from '@mui/icons-material';
import {getHint} from '../hints';
import './ControlPanel.css';
import HelpDialog from '../Help/HelpDialog';
import logger from '../../Logger';

// Helper function to parse wall code from .fil file
const parseWallCode = (code, x, y) => {
	const wallSegments = [];
	if (code & 8) wallSegments.push(`${x},${y},${x + 1},${y}`);         // Top
	if (code & 4) wallSegments.push(`${x + 1},${y},${x + 1},${y + 1}`); // Right
	if (code & 2) wallSegments.push(`${x},${y + 1},${x + 1},${y + 1}`); // Bottom
	if (code & 1) wallSegments.push(`${x},${y},${x},${y + 1}`);         // Left
	return wallSegments;
};

const ControlPanel = memo(({
	                           robotPos, setRobotPos, walls, setWalls, permanentWalls,
	                           markers, setMarkers, coloredCells, setColoredCells,
	                           symbols, setSymbols, // <-- Receive symbols state and setter
	                           width, setWidth, height, setHeight,
	                           editMode, setEditMode, setStatusMessage,
                           }) => {
	const fileInputRef = useRef(null);
	const [helpOpen, setHelpOpen] = useState(false);

	// isBlocked function
	const isBlocked = useCallback((x, y, direction) => {
		let wallKey = '';
		switch (direction) {
			case 'up':
				if (y <= 0) return true;
				wallKey = `${x},${y},${x + 1},${y}`;
				break;
			case 'down':
				if (y >= height - 1) return true;
				wallKey = `${x},${y + 1},${x + 1},${y + 1}`;
				break;
			case 'left':
				if (x <= 0) return true;
				wallKey = `${x},${y},${x},${y + 1}`;
				break;
			case 'right':
				if (x >= width - 1) return true;
				wallKey = `${x + 1},${y},${x + 1},${y + 1}`;
				break;
			default:
				return true;
		}
		return permanentWalls.has(wallKey) || walls.has(wallKey);
	}, [walls, permanentWalls, width, height]);

	// moveRobot function
	const moveRobot = useCallback((direction) => {
		let {x, y} = robotPos;
		let newX = x, newY = y;
		let blocked = false, hS = '', hB = '', logDir = '';
		switch (direction) {
			case 'up':
				hS = 'moveRobotUp';
				hB = 'moveRobotUpBlocked';
				logDir = 'вверх';
				if (!isBlocked(x, y, 'up')) newY--; else blocked = true;
				break;
			case 'down':
				hS = 'moveRobotDown';
				hB = 'moveRobotDownBlocked';
				logDir = 'вниз';
				if (!isBlocked(x, y, 'down')) newY++; else blocked = true;
				break;
			case 'left':
				hS = 'moveRobotLeft';
				hB = 'moveRobotLeftBlocked';
				logDir = 'влево';
				if (!isBlocked(x, y, 'left')) newX--; else blocked = true;
				break;
			case 'right':
				hS = 'moveRobotRight';
				hB = 'moveRobotRightBlocked';
				logDir = 'вправо';
				if (!isBlocked(x, y, 'right')) newX++; else blocked = true;
				break;
			default:
				logger.log_error(`Неизвестное направление: ${direction}`);
				return;
		}
		if (blocked) {
			setStatusMessage(getHint(hB, editMode));
			logger.log_movement(`Блок ${logDir} в (${x}, ${y})`);
		} else {
			setRobotPos({x: newX, y: newY});
			setStatusMessage(getHint(hS, editMode));
			logger.log_movement(`Робот ${logDir} -> (${newX}, ${newY})`);
		}
	}, [robotPos, isBlocked, editMode, setRobotPos, setStatusMessage]);

	// Marker and Cell functions
	const putMarker = useCallback(() => {
		const k = `${robotPos.x},${robotPos.y}`;
		if (markers[k]) {
			setStatusMessage(getHint('markerAlreadyExists', editMode));
			logger.log_marker(`Маркер уже есть в (${robotPos.x},${robotPos.y})`);
		} else {
			setMarkers(p => ({...p, [k]: 1}));
			setStatusMessage(getHint('putMarker', editMode));
			logger.log_marker(`Маркер (${robotPos.x},${robotPos.y})`);
		}
	}, [robotPos, markers, setMarkers, setStatusMessage, editMode]);
	const pickMarker = useCallback(() => {
		const k = `${robotPos.x},${robotPos.y}`;
		if (!markers[k]) {
			setStatusMessage(getHint('noMarkerHere', editMode));
			logger.log_marker(`Нет маркера в (${robotPos.x},${robotPos.y})`);
		} else {
			setMarkers(p => {
				const n = {...p};
				delete n[k];
				return n;
			});
			setStatusMessage(getHint('pickMarker', editMode));
			logger.log_marker(`Маркер снят (${robotPos.x},${robotPos.y})`);
		}
	}, [robotPos, markers, setMarkers, setStatusMessage, editMode]);
	const paintCell = useCallback(() => {
		const k = `${robotPos.x},${robotPos.y}`;
		if (coloredCells.has(k)) {
			setStatusMessage(getHint('cellAlreadyPainted', editMode));
			logger.log_cell(`Клетка (${robotPos.x},${robotPos.y}) уже окрашена.`);
		} else {
			setColoredCells(p => new Set(p).add(k));
			setStatusMessage(getHint('paintCell', editMode));
			logger.log_cell(`Клетка (${robotPos.x},${robotPos.y}) окрашена.`);
		}
	}, [robotPos, coloredCells, setColoredCells, setStatusMessage, editMode]);
	const clearCell = useCallback(() => {
		const k = `${robotPos.x},${robotPos.y}`;
		if (!coloredCells.has(k)) {
			setStatusMessage(getHint('cellAlreadyClear', editMode));
			logger.log_cell(`Клетка (${robotPos.x},${robotPos.y}) уже чистая.`);
		} else {
			setColoredCells(p => {
				const n = new Set(p);
				n.delete(k);
				return n;
			});
			setStatusMessage(getHint('clearCell', editMode));
			logger.log_cell(`Клетка (${robotPos.x},${robotPos.y}) очищена.`);
		}
	}, [robotPos, coloredCells, setColoredCells, setStatusMessage, editMode]);

	// --- Edit Mode and Dimensions ---
	const toggleEditMode = useCallback(() => {
		const n = !editMode;
		setEditMode(n);
		setStatusMessage(getHint(n ? 'enterEditMode' : 'exitEditMode', n));
		logger.log_edit_mode_change(n);
	}, [editMode, setEditMode, setStatusMessage]);
	const changeDimension = useCallback((dim, delta) => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', false));
			logger.log_event(`Размер (${dim}) вне режима ред.`);
			return;
		}
		let c = dim === 'width' ? width : height;
		let n = c + delta;
		let s = dim === 'width' ? setWidth : setHeight;
		if (n < 1) {
			setStatusMessage(getHint(dim === 'width' ? 'widthCannotBeLessThan1' : 'heightCannotBeLessThan1', true));
			logger.log_dimension(`Уменьшение ${dim} < 1`);
		} else {
			s(n);
			setStatusMessage(getHint(delta > 0 ? (dim === 'width' ? 'increaseWidth' : 'increaseHeight') : (dim === 'width' ? 'decreaseWidth' : 'decreaseHeight'), true));
			logger.log_dimension_change(dim, c, n);
		}
	}, [editMode, width, height, setWidth, setHeight, setStatusMessage]);
	const increaseWidth = useCallback(() => changeDimension('width', 1), [changeDimension]);
	const decreaseWidth = useCallback(() => changeDimension('width', -1), [changeDimension]);
	const increaseHeight = useCallback(() => changeDimension('height', 1), [changeDimension]);
	const decreaseHeight = useCallback(() => changeDimension('height', -1), [changeDimension]);

	// --- File Import ---
	const handleImportClick = useCallback(() => fileInputRef.current?.click(), []);

	const parseAndApplyFieldFile = useCallback((content, filename = "unknown") => {
		if (!content || typeof content !== 'string') {
			throw new Error('Содержимое файла пустое.');
		}
		try {
			const lines = content.split('\n').map(line => line.trim()).filter(line => line.length > 0 && !line.startsWith(';'));
			if (lines.length < 2) throw new Error('Недостаточно строк данных (размеры/позиция).');

			const dimensions = lines[0].split(/\s+/).map(Number);
			if (dimensions.length < 2 || dimensions.some(isNaN) || dimensions[0] < 1 || dimensions[1] < 1) {
				throw new Error(`Неверный формат размеров ('${lines[0]}').`);
			}
			const [fileWidth, fileHeight] = dimensions;

			const robotCoords = lines[1].split(/\s+/).map(Number);
			if (robotCoords.length < 2 || robotCoords.some(isNaN)) {
				throw new Error(`Неверный формат координат ('${lines[1]}').`);
			}
			const [robotX, robotY] = robotCoords;
			const clampedRobotPos = {
				x: Math.min(Math.max(0, robotX), fileWidth - 1),
				y: Math.min(Math.max(0, robotY), fileHeight - 1)
			};

			const importedWalls = new Set();
			const importedColored = new Set();
			const importedMarkers = {};
			const importedSymbols = {}; // <-- Object for imported symbols
			const startIndexForData = 2;

			for (let i = startIndexForData; i < lines.length; i++) {
				const parts = lines[i].split(/\s+/);
				// x y wallcode colorflag Rad Temp Sym Sym1 Point
				// Min 4 required (up to colorflag)
				if (parts.length < 4) {
					logger.log_error(`Файл '${filename}', стр ${i + 1}: < 4 полей, пропуск.`);
					continue;
				}

				const cellX = parseInt(parts[0], 10);
				const cellY = parseInt(parts[1], 10);
				const wallCode = parseInt(parts[2], 10);
				const colorFlag = parts[3];
				// Safely access potentially missing fields
				const upperSymbolRaw = parts.length >= 7 ? parts[6] : '$'; // Sym is index 6
				const lowerSymbolRaw = parts.length >= 8 ? parts[7] : '$'; // Sym1 is index 7
				const markerFlag = parts.length >= 9 ? parts[8] : '0';    // Point is index 8

				if (cellX < 0 || cellY < 0 || cellX >= fileWidth || cellY >= fileHeight) {
					logger.log_event(`Файл '${filename}', стр ${i + 1}: коорд (${cellX},${cellY}) вне поля ${fileWidth}x${fileHeight}, пропуск.`);
					continue;
				}
				if (isNaN(cellX) || isNaN(cellY) || isNaN(wallCode)) {
					logger.log_error(`Файл '${filename}', стр ${i + 1}: неверные коорд/стены, пропуск.`);
					continue;
				}

				const cellKey = `${cellX},${cellY}`;
				if (colorFlag === '1') importedColored.add(cellKey);
				if (markerFlag === '1') importedMarkers[cellKey] = 1;

				// --- Process Symbols ---
				const upperSymbol = upperSymbolRaw !== '$' ? upperSymbolRaw : null;
				const lowerSymbol = lowerSymbolRaw !== '$' ? lowerSymbolRaw : null;
				if (upperSymbol || lowerSymbol) {
					importedSymbols[cellKey] = {};
					if (upperSymbol) importedSymbols[cellKey].upper = upperSymbol;
					if (lowerSymbol) importedSymbols[cellKey].lower = lowerSymbol;
				}
				// ---------------------

				const wallsToAdd = parseWallCode(wallCode, cellX, cellY);
				wallsToAdd.forEach(w => importedWalls.add(w));
			}

			logger.log_event(`Применение '${filename}': ${fileWidth}x${fileHeight}, Робот=(${clampedRobotPos.x},${clampedRobotPos.y})`);
			setWidth(fileWidth);
			setHeight(fileHeight);
			setRobotPos(clampedRobotPos);
			setWalls(importedWalls);
			setColoredCells(importedColored);
			setMarkers(importedMarkers);
			setSymbols(importedSymbols); // <-- Set the imported symbols
			setStatusMessage(`Поле (${fileWidth}x${fileHeight}) загружено.`);

		} catch (error) {
			const errMsg = error instanceof Error ? error.message : String(error);
			logger.log_error(`Ошибка парсинга '${filename}': ${errMsg}`);
			throw new Error(`Ошибка разбора '${filename}': ${errMsg}`);
		}
	}, [setWidth, setHeight, setRobotPos, setWalls, setColoredCells, setMarkers, setSymbols, setStatusMessage, logger]); // Added setSymbols dependency

	const handleFileChange = useCallback(async (e) => {
		const file = e.target.files?.[0];
		if (!file) return;
		try {
			const content = await file.text();
			logger.log_event(`Чтение '${file.name}'...`);
			parseAndApplyFieldFile(content, file.name);
			setStatusMessage(getHint('importSuccess', editMode));
			logger.log_file_import_success(file.name);
		} catch (error) {
			const errMsg = error instanceof Error ? error.message : String(error);
			setStatusMessage(getHint('importError', editMode) + errMsg);
			logger.log_file_import_error(file.name, errMsg);
		} finally {
			if (e.target) e.target.value = "";
		}
	}, [editMode, setStatusMessage, parseAndApplyFieldFile]);

	// --- Help Dialog ---
	const openHelpDialog = useCallback(() => setHelpOpen(true), []);
	const closeHelpDialog = useCallback(() => setHelpOpen(false), []);

	// --- Rendering ---
	return (
		<>
			<Card className="control-panel" elevation={3}>
				<CardHeader title="Панель управления"/>
				<CardContent>
					{/* ... (rest of the buttons remain the same) ... */}
					{/* Movement Buttons */}
					<Grid container spacing={1} justifyContent="center" alignItems="center" className="control-section">
						<Grid item xs={12} container justifyContent="center"><Tooltip title="Вверх"><Button
							onClick={() => moveRobot('up')} variant="contained" className="control-button small-button"><ArrowUpwardIcon/></Button></Tooltip></Grid>
						<Grid item xs={4} container justifyContent="flex-end"><Tooltip title="Влево"><Button
							onClick={() => moveRobot('left')} variant="contained"
							className="control-button small-button"><ArrowBackIcon/></Button></Tooltip></Grid>
						<Grid item xs={4}/>
						<Grid item xs={4} container justifyContent="flex-start"><Tooltip title="Вправо"><Button
							onClick={() => moveRobot('right')} variant="contained"
							className="control-button small-button"><ArrowForwardIcon/></Button></Tooltip></Grid>
						<Grid item xs={12} container justifyContent="center"><Tooltip title="Вниз"><Button
							onClick={() => moveRobot('down')} variant="contained"
							className="control-button small-button"><ArrowDownwardIcon/></Button></Tooltip></Grid>
					</Grid>
					{/* Marker/Paint Buttons */}
					<Grid container spacing={1} className="control-section">
						<Grid item xs={6}><Tooltip title="Положить маркер"><Button onClick={putMarker}
						                                                           startIcon={<AddLocationIcon/>}
						                                                           color="success" variant="contained"
						                                                           fullWidth
						                                                           className="control-button">Маркер</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Поднять маркер"><Button onClick={pickMarker}
						                                                          startIcon={<DeleteOutlineIcon/>}
						                                                          color="error" variant="contained"
						                                                          fullWidth
						                                                          className="control-button">Маркер</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Покрасить клетку"><Button onClick={paintCell}
						                                                            startIcon={<BrushIcon/>}
						                                                            color="warning" variant="contained"
						                                                            fullWidth
						                                                            className="control-button">Клетка</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Очистить клетку"><Button onClick={clearCell}
						                                                           startIcon={<ClearIcon/>} color="info"
						                                                           variant="contained" fullWidth
						                                                           className="control-button">Клетка</Button></Tooltip></Grid>
					</Grid>
					{/* Edit Mode/Dimension Buttons */}
					<Grid container spacing={1} className="control-section">
						<Grid item xs={12}><Tooltip title={editMode ? 'Выкл. режим ред.' : 'Вкл. режим ред.'}><Button
							onClick={toggleEditMode} startIcon={<EditIcon/>} color={editMode ? "secondary" : "primary"}
							variant="contained" fullWidth
							className="control-button">{editMode ? 'Выкл. Ред.' : 'Вкл. Ред.'}</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Поле шире (в режиме ред.)"><Button onClick={increaseWidth}
						                                                                     startIcon={<AddIcon/>}
						                                                                     variant="outlined"
						                                                                     fullWidth
						                                                                     className="control-button"
						                                                                     disabled={!editMode}>Шире</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Поле уже (в режиме ред.)"><Button onClick={decreaseWidth}
						                                                                    startIcon={<RemoveIcon/>}
						                                                                    variant="outlined" fullWidth
						                                                                    className="control-button"
						                                                                    disabled={!editMode || width <= 1}>Уже</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Поле выше (в режиме ред.)"><Button onClick={increaseHeight}
						                                                                     startIcon={<AddIcon/>}
						                                                                     variant="outlined"
						                                                                     fullWidth
						                                                                     className="control-button"
						                                                                     disabled={!editMode}>Выше</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Поле ниже (в режиме ред.)"><Button onClick={decreaseHeight}
						                                                                     startIcon={<RemoveIcon/>}
						                                                                     variant="outlined"
						                                                                     fullWidth
						                                                                     className="control-button"
						                                                                     disabled={!editMode || height <= 1}>Ниже</Button></Tooltip></Grid>
					</Grid>
					{/* Help/Import Buttons */}
					<Grid container spacing={1} className="control-section">
						<Grid item xs={6}><Tooltip title="Помощь"><Button onClick={openHelpDialog}
						                                                  startIcon={<HelpOutlineIcon/>} color="info"
						                                                  variant="text" fullWidth
						                                                  className="control-button">Помощь</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Импорт .fil"><Button onClick={handleImportClick}
						                                                       startIcon={<FileUploadIcon/>}
						                                                       color="secondary" variant="text"
						                                                       fullWidth className="control-button">Импорт
							.fil</Button></Tooltip></Grid>
					</Grid>
					<input type="file" accept=".fil" ref={fileInputRef} style={{display: 'none'}}
					       onChange={handleFileChange}/>
				</CardContent>
			</Card>
			<HelpDialog open={helpOpen} onClose={closeHelpDialog}/>
		</>
	);
});

export default ControlPanel;