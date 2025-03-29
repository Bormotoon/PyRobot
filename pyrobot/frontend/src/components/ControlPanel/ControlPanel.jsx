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
const parseWallCode = (code, x, y) => { /* ... unchanged ... */
	const w = [];
	if (code & 8) w.push(`${x},${y},${x + 1},${y}`);
	if (code & 4) w.push(`${x + 1},${y},${x + 1},${y + 1}`);
	if (code & 2) w.push(`${x},${y + 1},${x + 1},${y + 1}`);
	if (code & 1) w.push(`${x},${y},${x},${y + 1}`);
	return w;
};

const ControlPanel = memo(({
	                           robotPos, setRobotPos, walls, setWalls, permanentWalls,
	                           markers, setMarkers, coloredCells, setColoredCells,
	                           symbols, setSymbols,
	                           radiation, setRadiation, // <-- Receive radiation/temp state/setters
	                           temperature, setTemperature,
	                           width, setWidth, height, setHeight,
	                           editMode, setEditMode, setStatusMessage,
                           }) => {
	const fileInputRef = useRef(null);
	const [helpOpen, setHelpOpen] = useState(false);

	// isBlocked function - unchanged
	const isBlocked = useCallback((x, y, dir) => {
		let k = '';
		switch (dir) {
			case 'up':
				if (y <= 0) return true;
				k = `${x},${y},${x + 1},${y}`;
				break;
			case 'down':
				if (y >= height - 1) return true;
				k = `${x},${y + 1},${x + 1},${y + 1}`;
				break;
			case 'left':
				if (x <= 0) return true;
				k = `${x},${y},${x},${y + 1}`;
				break;
			case 'right':
				if (x >= width - 1) return true;
				k = `${x + 1},${y},${x + 1},${y + 1}`;
				break;
			default:
				return true;
		}
		return permanentWalls.has(k) || walls.has(k);
	}, [walls, permanentWalls, width, height]);
	// moveRobot function - unchanged
	const moveRobot = useCallback((dir) => {
		let {x, y} = robotPos;
		let nX = x, nY = y;
		let b = false, hS = '', hB = '', lD = '';
		switch (dir) {
			case 'up':
				hS = 'moveRobotUp';
				hB = 'moveRobotUpBlocked';
				lD = 'вверх';
				if (!isBlocked(x, y, 'up')) nY--; else b = true;
				break;
			case 'down':
				hS = 'moveRobotDown';
				hB = 'moveRobotDownBlocked';
				lD = 'вниз';
				if (!isBlocked(x, y, 'down')) nY++; else b = true;
				break;
			case 'left':
				hS = 'moveRobotLeft';
				hB = 'moveRobotLeftBlocked';
				lD = 'влево';
				if (!isBlocked(x, y, 'left')) nX--; else b = true;
				break;
			case 'right':
				hS = 'moveRobotRight';
				hB = 'moveRobotRightBlocked';
				lD = 'вправо';
				if (!isBlocked(x, y, 'right')) nX++; else b = true;
				break;
			default:
				logger.log_error(`Dir? ${dir}`);
				return;
		}
		if (b) {
			setStatusMessage(getHint(hB, editMode));
			logger.log_movement(`Блок ${lD} в (${x},${y})`);
		} else {
			setRobotPos({x: nX, y: nY});
			setStatusMessage(getHint(hS, editMode));
			logger.log_movement(`Робот ${lD}->(${nX},${nY})`);
		}
	}, [robotPos, isBlocked, editMode, setRobotPos, setStatusMessage]);
	// Marker/Cell functions - unchanged
	const putMarker = useCallback(() => {
		const k = `${robotPos.x},${robotPos.y}`;
		if (markers[k]) {
			setStatusMessage(getHint('markerAlreadyExists', editMode));
			logger.log_marker(`Уже есть маркер (${k})`);
		} else {
			setMarkers(p => ({...p, [k]: 1}));
			setStatusMessage(getHint('putMarker', editMode));
			logger.log_marker(`Маркер (${k})`);
		}
	}, [robotPos, markers, setMarkers, setStatusMessage, editMode]);
	const pickMarker = useCallback(() => {
		const k = `${robotPos.x},${robotPos.y}`;
		if (!markers[k]) {
			setStatusMessage(getHint('noMarkerHere', editMode));
			logger.log_marker(`Нет маркера (${k})`);
		} else {
			setMarkers(p => {
				const n = {...p};
				delete n[k];
				return n;
			});
			setStatusMessage(getHint('pickMarker', editMode));
			logger.log_marker(`Снят маркер (${k})`);
		}
	}, [robotPos, markers, setMarkers, setStatusMessage, editMode]);
	const paintCell = useCallback(() => {
		const k = `${robotPos.x},${robotPos.y}`;
		if (coloredCells.has(k)) {
			setStatusMessage(getHint('cellAlreadyPainted', editMode));
			logger.log_cell(`Кл (${k}) уже закр.`);
		} else {
			setColoredCells(p => new Set(p).add(k));
			setStatusMessage(getHint('paintCell', editMode));
			logger.log_cell(`Кл (${k}) закр.`);
		}
	}, [robotPos, coloredCells, setColoredCells, setStatusMessage, editMode]);
	const clearCell = useCallback(() => {
		const k = `${robotPos.x},${robotPos.y}`;
		if (!coloredCells.has(k)) {
			setStatusMessage(getHint('cellAlreadyClear', editMode));
			logger.log_cell(`Кл (${k}) уже чист.`);
		} else {
			setColoredCells(p => {
				const n = new Set(p);
				n.delete(k);
				return n;
			});
			setStatusMessage(getHint('clearCell', editMode));
			logger.log_cell(`Кл (${k}) очищ.`);
		}
	}, [robotPos, coloredCells, setColoredCells, setStatusMessage, editMode]);
	// Edit Mode / Dimensions - unchanged
	const toggleEditMode = useCallback(() => {
		const n = !editMode;
		setEditMode(n);
		setStatusMessage(getHint(n ? 'enterEditMode' : 'exitEditMode', n));
		logger.log_edit_mode_change(n);
	}, [editMode, setEditMode, setStatusMessage]);
	const changeDimension = useCallback((dim, delta) => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', false));
			return;
		}
		let c = dim === 'width' ? width : height;
		let n = c + delta;
		let s = dim === 'width' ? setWidth : setHeight;
		if (n < 1) {
			setStatusMessage(getHint(dim === 'width' ? 'widthCannotBeLessThan1' : 'heightCannotBeLessThan1', true));
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
	// Help Dialog - unchanged
	const openHelpDialog = useCallback(() => setHelpOpen(true), []);
	const closeHelpDialog = useCallback(() => setHelpOpen(false), []);
	// File Import trigger - unchanged
	const handleImportClick = useCallback(() => fileInputRef.current?.click(), []);

	// Parse and Apply File Function
	const parseAndApplyFieldFile = useCallback((content, filename = "unknown") => {
		if (!content || typeof content !== 'string') {
			throw new Error('Файл пуст.');
		}
		try {
			const lines = content.split('\n').map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith(';'));
			if (lines.length < 2) throw new Error('Нет данных о размере/позиции.');
			const dims = lines[0].split(/\s+/).map(Number);
			if (dims.length < 2 || dims.some(isNaN) || dims[0] < 1 || dims[1] < 1) {
				throw new Error(`Размеры ('${lines[0]}')?`);
			}
			const [fileWidth, fileHeight] = dims;
			const coords = lines[1].split(/\s+/).map(Number);
			if (coords.length < 2 || coords.some(isNaN)) {
				throw new Error(`Координаты ('${lines[1]}')?`);
			}
			const [robotX, robotY] = coords;
			const pos = {
				x: Math.min(Math.max(0, robotX), fileWidth - 1),
				y: Math.min(Math.max(0, robotY), fileHeight - 1)
			};
			const walls = new Set(), colored = new Set(), markers = {}, symbols = {}, radiation = {}, temperature = {}; // Init new states

			for (let i = 2; i < lines.length; i++) {
				const parts = lines[i].split(/\s+/);
				// x(0) y(1) wall(2) color(3) rad(4) temp(5) symU(6) symL(7) mark(8)
				if (parts.length < 4) {
					logger.log_error(`Файл ${filename}:${i + 1} < 4 полей`);
					continue;
				}
				const x = parseInt(parts[0], 10), y = parseInt(parts[1], 10), wc = parseInt(parts[2], 10);
				if (isNaN(x) || isNaN(y) || isNaN(wc) || x < 0 || y < 0 || x >= fileWidth || y >= fileHeight) {
					logger.log_error(`Файл ${filename}:${i + 1} неверные коорд/стены`);
					continue;
				}
				const key = `${x},${y}`;
				if (parts[3] === '1') colored.add(key);
				if (parts.length >= 9 && parts[8] === '1') markers[key] = 1;
				// --- Read radiation/temp ---
				if (parts.length >= 5 && !isNaN(parseFloat(parts[4]))) radiation[key] = parseFloat(parts[4]);
				if (parts.length >= 6 && !isNaN(parseInt(parts[5], 10))) temperature[key] = parseInt(parts[5], 10);
				// -------------------------
				const symU = parts.length >= 7 && parts[6] !== '$' ? parts[6] : null;
				const symL = parts.length >= 8 && parts[7] !== '$' ? parts[7] : null;
				if (symU || symL) symbols[key] = {...(symU && {upper: symU}), ...(symL && {lower: symL})};
				parseWallCode(wc, x, y).forEach(w => walls.add(w));
			}
			logger.log_event(`Применение ${filename}: ${fileWidth}x${fileHeight}, R=(${pos.x},${pos.y})`);
			setWidth(fileWidth);
			setHeight(fileHeight);
			setRobotPos(pos);
			setWalls(walls);
			setColoredCells(colored);
			setMarkers(markers);
			setSymbols(symbols);
			setRadiation(radiation);
			setTemperature(temperature); // <-- Set new states
			setStatusMessage(`Поле ${fileWidth}x${fileHeight} загружено.`);
		} catch (e) {
			logger.log_error(`Парсинг ${filename}: ${e.message}`);
			throw new Error(`Разбор ${filename}:${e.message}`);
		}
	}, [setWidth, setHeight, setRobotPos, setWalls, setColoredCells, setMarkers, setSymbols, setRadiation, setTemperature, setStatusMessage, logger]); // Added new setters

	// File change handler - unchanged logic, relies on parseAndApplyFieldFile
	const handleFileChange = useCallback(async (e) => { /* ... unchanged ... */
		const f = e.target.files?.[0];
		if (!f) return;
		try {
			const c = await f.text();
			logger.log_event(`Чт ${f.name}`);
			parseAndApplyFieldFile(c, f.name);
			setStatusMessage(getHint('importSuccess', editMode));
			logger.log_file_import_success(f.name);
		} catch (err) {
			const m = err instanceof Error ? err.message : String(err);
			setStatusMessage(getHint('importError', editMode) + m);
			logger.log_file_import_error(f.name, m);
		} finally {
			if (e.target) e.target.value = "";
		}
	}, [editMode, setStatusMessage, parseAndApplyFieldFile]);

	// --- Rendering ---
	return (
		<>
			<Card className="control-panel" elevation={3}>
				<CardHeader title="Панель управления"/>
				<CardContent>
					{/* Buttons remain visually the same */}
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
						<Grid item xs={6}><Tooltip title="Маркер +"><Button onClick={putMarker}
						                                                    startIcon={<AddLocationIcon/>}
						                                                    color="success" variant="contained"
						                                                    fullWidth
						                                                    className="control-button">Маркер</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Маркер -"><Button onClick={pickMarker}
						                                                    startIcon={<DeleteOutlineIcon/>}
						                                                    color="error" variant="contained" fullWidth
						                                                    className="control-button">Маркер</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Клетка +"><Button onClick={paintCell} startIcon={<BrushIcon/>}
						                                                    color="warning" variant="contained"
						                                                    fullWidth
						                                                    className="control-button">Клетка</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Клетка -"><Button onClick={clearCell} startIcon={<ClearIcon/>}
						                                                    color="info" variant="contained" fullWidth
						                                                    className="control-button">Клетка</Button></Tooltip></Grid>
					</Grid>
					{/* Edit Mode/Dimension Buttons */}
					<Grid container spacing={1} className="control-section">
						<Grid item xs={12}><Tooltip title={editMode ? 'Выкл Ред' : 'Вкл Ред'}><Button
							onClick={toggleEditMode} startIcon={<EditIcon/>} color={editMode ? "secondary" : "primary"}
							variant="contained" fullWidth
							className="control-button">{editMode ? 'Выкл' : 'Вкл'} Ред.</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Шире (Ред)"><Button onClick={increaseWidth}
						                                                      startIcon={<AddIcon/>} variant="outlined"
						                                                      fullWidth className="control-button"
						                                                      disabled={!editMode}>Шире</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Уже (Ред)"><Button onClick={decreaseWidth}
						                                                     startIcon={<RemoveIcon/>}
						                                                     variant="outlined" fullWidth
						                                                     className="control-button"
						                                                     disabled={!editMode || width <= 1}>Уже</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Выше (Ред)"><Button onClick={increaseHeight}
						                                                      startIcon={<AddIcon/>} variant="outlined"
						                                                      fullWidth className="control-button"
						                                                      disabled={!editMode}>Выше</Button></Tooltip></Grid>
						<Grid item xs={6}><Tooltip title="Ниже (Ред)"><Button onClick={decreaseHeight}
						                                                      startIcon={<RemoveIcon/>}
						                                                      variant="outlined" fullWidth
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