// FILE START: ControlPanel.jsx
import React, {memo, useCallback, useRef, useState} from 'react';
import {
	Button, 
	Card, 
	CardContent, 
	Typography, 
	Grid, 
	Tooltip, 
	Box,
	Divider,
	Chip,
	IconButton,
	Switch,
	FormControlLabel,
	TextField,
	Paper,
	Accordion,
	AccordionSummary,
	AccordionDetails
} from '@mui/material';
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
	Settings as SettingsIcon,
	SmartToy as RobotIcon,
	GridOn as GridIcon,
	ExpandMore as ExpandMoreIcon,
	Palette as PaletteIcon,
	LocationOn as LocationOnIcon
} from '@mui/icons-material';
import {getHint} from '../hints';
import './ControlPanel.css';
import HelpDialog from '../Help/HelpDialog';
import logger from '../../Logger';

const parseWallCode = (code, x, y) => {
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
	                           radiation, setRadiation,
	                           temperature, setTemperature,
	                           width, setWidth, height, setHeight,
	                           editMode, setEditMode, setStatusMessage,
                           }) => {
	const fileInputRef = useRef(null);
	const [helpOpen, setHelpOpen] = useState(false);

	// --- Обработчики действий ---

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

	// --->>> ИСПРАВЛЯЕМ ВЫЗОВ ЛОГГЕРА ЗДЕСЬ <<<---
	const moveRobot = useCallback((dir) => {
		if (!robotPos) return;
		let {x, y} = robotPos;
		let nX = x, nY = y;
		let blocked = false;
		let hintSuccess = '', hintBlocked = '', logDirection = '';
		switch (dir) {
			case 'up':
				hintSuccess = 'moveRobotUp';
				hintBlocked = 'moveRobotUpBlocked';
				logDirection = 'Up';
				if (!isBlocked(x, y, 'up')) nY--; else blocked = true;
				break;
			case 'down':
				hintSuccess = 'moveRobotDown';
				hintBlocked = 'moveRobotDownBlocked';
				logDirection = 'Down';
				if (!isBlocked(x, y, 'down')) nY++; else blocked = true;
				break;
			case 'left':
				hintSuccess = 'moveRobotLeft';
				hintBlocked = 'moveRobotLeftBlocked';
				logDirection = 'Left';
				if (!isBlocked(x, y, 'left')) nX--; else blocked = true;
				break;
			case 'right':
				hintSuccess = 'moveRobotRight';
				hintBlocked = 'moveRobotRightBlocked';
				logDirection = 'Right';
				if (!isBlocked(x, y, 'right')) nX++; else blocked = true;
				break;
			default:
				logger.log_error(`[Movement] Unknown direction: ${dir}`);
				return;
		}
		if (blocked) {
			setStatusMessage(getHint(hintBlocked, editMode));
			// Используем log_event вместо log_warning
			logger.log_event(`[MovementBlocked] Blocked trying to move ${logDirection} from (${x},${y})`);
		} else {
			setRobotPos({x: nX, y: nY});
			setStatusMessage(getHint(hintSuccess, editMode));
			logger.log_event(`[Movement] Robot moved ${logDirection} -> (${nX},${nY})`);
		}
	}, [robotPos, isBlocked, editMode, setRobotPos, setStatusMessage]);
	// --- <<< КОНЕЦ ИСПРАВЛЕНИЙ >>> ---

	const putMarker = useCallback(() => {
		if (!robotPos) return;
		const k = `${robotPos.x},${robotPos.y}`;
		if (markers[k]) {
			setStatusMessage(getHint('markerAlreadyExists', editMode));
			logger.log_event(`[Marker] Attempt to put marker on already marked cell (${k})`);
		} // Используем log_event
		else {
			setMarkers(p => ({...p, [k]: 1}));
			setStatusMessage(getHint('putMarker', editMode));
			logger.log_event(`[Marker] Marker placed at (${k})`);
		}
	}, [robotPos, markers, setMarkers, setStatusMessage, editMode]);

	const pickMarker = useCallback(() => {
		if (!robotPos) return;
		const k = `${robotPos.x},${robotPos.y}`;
		if (!markers[k]) {
			setStatusMessage(getHint('noMarkerHere', editMode));
			logger.log_event(`[Marker] Attempt to pick marker from empty cell (${k})`);
		} // Используем log_event
		else {
			setMarkers(p => {
				const n = {...p};
				delete n[k];
				return n;
			});
			setStatusMessage(getHint('pickMarker', editMode));
			logger.log_event(`[Marker] Marker picked from (${k})`);
		}
	}, [robotPos, markers, setMarkers, setStatusMessage, editMode]);

	const paintCell = useCallback(() => {
		if (!robotPos) return;
		const k = `${robotPos.x},${robotPos.y}`;
		if (coloredCells.has(k)) {
			setStatusMessage(getHint('cellAlreadyPainted', editMode));
			logger.log_event(`[Cell] Attempt to paint already painted cell (${k})`);
		} // Используем log_event
		else {
			setColoredCells(p => new Set(p).add(k));
			setStatusMessage(getHint('paintCell', editMode));
			logger.log_event(`[Cell] Cell painted at (${k})`);
		}
	}, [robotPos, coloredCells, setColoredCells, setStatusMessage, editMode]);

	const clearCell = useCallback(() => {
		if (!robotPos) return;
		const k = `${robotPos.x},${robotPos.y}`;
		if (!coloredCells.has(k)) {
			setStatusMessage(getHint('cellAlreadyClear', editMode));
			logger.log_event(`[Cell] Attempt to clear already clear cell (${k})`);
		} // Используем log_event
		else {
			setColoredCells(p => {
				const n = new Set(p);
				n.delete(k);
				return n;
			});
			setStatusMessage(getHint('clearCell', editMode));
			logger.log_event(`[Cell] Cell cleared at (${k})`);
		}
	}, [robotPos, coloredCells, setColoredCells, setStatusMessage, editMode]);

	const toggleEditMode = useCallback(() => {
		const nextMode = !editMode;
		setEditMode(nextMode);
		setStatusMessage(getHint(nextMode ? 'enterEditMode' : 'exitEditMode', nextMode));
		logger.log_edit_mode_change(nextMode);
	}, [editMode, setEditMode, setStatusMessage]);

	const changeDimension = useCallback((dim, delta) => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', false));
			return;
		}
		let currentSize = dim === 'width' ? width : height;
		let newSize = currentSize + delta;
		let setter = dim === 'width' ? setWidth : setHeight;
		if (newSize < 1) {
			setStatusMessage(getHint(dim === 'width' ? 'widthCannotBeLessThan1' : 'heightCannotBeLessThan1', true));
		} else {
			setter(newSize);
			setStatusMessage(getHint(delta > 0 ? (dim === 'width' ? 'increaseWidth' : 'increaseHeight') : (dim === 'width' ? 'decreaseWidth' : 'decreaseHeight'), true));
			logger.log_dimension_change(dim, currentSize, newSize);
		}
	}, [editMode, width, height, setWidth, setHeight, setStatusMessage]);
	const increaseWidth = useCallback(() => changeDimension('width', 1), [changeDimension]);
	const decreaseWidth = useCallback(() => changeDimension('width', -1), [changeDimension]);
	const increaseHeight = useCallback(() => changeDimension('height', 1), [changeDimension]);
	const decreaseHeight = useCallback(() => changeDimension('height', -1), [changeDimension]);

	const openHelpDialog = useCallback(() => {
		setHelpOpen(true);
		setStatusMessage(getHint('helpOpen'));
		logger.log_event('Help dialog opened.');
	}, [setStatusMessage]);
	const closeHelpDialog = useCallback(() => setHelpOpen(false), []);

	const handleImportClick = useCallback(() => {
		setStatusMessage(getHint('importTrigger'));
		logger.log_event('Import file button clicked.');
		fileInputRef.current?.click();
	}, [setStatusMessage]);

	const parseAndApplyFieldFile = useCallback((content, filename = "unknown") => {
		if (!content || typeof content !== 'string') {
			throw new Error('Content is empty or not a string.');
		}
		try {
			const lines = content.split('\n').map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith(';'));
			if (lines.length < 2) throw new Error('File must contain at least 2 lines (dimensions and robot position).');
			const dims = lines[0].split(/\s+/).map(Number);
			if (dims.length < 2 || dims.some(isNaN) || dims[0] < 1 || dims[1] < 1) {
				throw new Error(`Invalid dimensions line: '${lines[0]}'`);
			}
			const [fileWidth, fileHeight] = dims;
			const coords = lines[1].split(/\s+/).map(Number);
			if (coords.length < 2 || coords.some(isNaN)) {
				throw new Error(`Invalid robot coordinates line: '${lines[1]}'`);
			}
			const [robotX, robotY] = coords;
			const initialRobotPos = {
				x: Math.min(Math.max(0, robotX), fileWidth - 1),
				y: Math.min(Math.max(0, robotY), fileHeight - 1)
			};
			const newWalls = new Set(), newColored = new Set(), newMarkers = {}, newSymbols = {}, newRadiation = {},
				newTemperature = {};
			for (let i = 2; i < lines.length; i++) {
				const parts = lines[i].split(/\s+/);
				if (parts.length < 4) {
					logger.log_event(`[File Import] Skipping line ${i + 1} in '${filename}': less than 4 fields.`);
					continue;
				}
				const x = parseInt(parts[0], 10), y = parseInt(parts[1], 10), wallCode = parseInt(parts[2], 10);
				if (isNaN(x) || isNaN(y) || isNaN(wallCode) || x < 0 || y < 0 || x >= fileWidth || y >= fileHeight) {
					logger.log_event(`[File Import] Skipping line ${i + 1} in '${filename}': invalid coordinates or wall code.`);
					continue;
				}
				const key = `${x},${y}`;
				if (parts[3] === '1') newColored.add(key);
				if (parts.length >= 9 && parts[8] === '1') newMarkers[key] = 1;
				if (parts.length >= 5 && !isNaN(parseFloat(parts[4]))) newRadiation[key] = parseFloat(parts[4]);
				if (parts.length >= 6 && !isNaN(parseInt(parts[5], 10))) newTemperature[key] = parseInt(parts[5], 10);
				const symU = parts.length >= 7 && parts[6] !== '$' ? parts[6] : null;
				const symL = parts.length >= 8 && parts[7] !== '$' ? parts[7] : null;
				if (symU || symL) newSymbols[key] = {...(symU && {upper: symU}), ...(symL && {lower: symL})};
				parseWallCode(wallCode, x, y).forEach(w => newWalls.add(w));
			}
			logger.log_event(`[File Import] Applying field from '${filename}': ${fileWidth}x${fileHeight}, Robot=(${initialRobotPos.x},${initialRobotPos.y})`);
			setWidth(fileWidth);
			setHeight(fileHeight);
			setRobotPos(initialRobotPos);
			setWalls(newWalls);
			setColoredCells(newColored);
			setMarkers(newMarkers);
			setSymbols(newSymbols);
			setRadiation(newRadiation);
			setTemperature(newTemperature);
		} catch (e) {
			logger.log_error(`[File Import] Error parsing file '${filename}': ${e.message}`);
			throw new Error(`Ошибка разбора файла '${filename}': ${e.message}`);
		}
	}, [setWidth, setHeight, setRobotPos, setWalls, setColoredCells, setMarkers, setSymbols, setRadiation, setTemperature]);

	const handleFileChange = useCallback(async (e) => {
		const file = e.target.files?.[0];
		if (!file) {
			setStatusMessage("");
			return;
		}
		const fileName = file.name;
		setStatusMessage(`Читаю файл ${fileName}...`);
		try {
			const content = await file.text();
			logger.log_event(`[File Import] Reading file '${fileName}' (${(file.size / 1024).toFixed(1)} KB)`);
			parseAndApplyFieldFile(content, fileName);
			setStatusMessage(`${getHint('importSuccess')} '${fileName}'`);
			logger.log_event(`[File Import] Successfully imported and applied '${fileName}'.`);
		} catch (err) {
			const errorMsg = err instanceof Error ? err.message : String(err);
			const hintKey = errorMsg.includes("Ошибка разбора") ? 'importErrorParse' : 'importErrorRead';
			setStatusMessage(`${getHint(hintKey)} '${fileName}': ${errorMsg}`);
			logger.log_error(`[File Import] Failed to import '${fileName}': ${errorMsg}`);
		} finally {
			if (e.target) e.target.value = "";
		}
	}, [setStatusMessage, parseAndApplyFieldFile]);

	return (
		<Box sx={{ 
			display: 'flex', 
			flexDirection: 'column', 
			gap: 1.5, 
			width: '100%'
		}}>
			{/* Управление роботом */}
			<Card elevation={2} sx={{ borderRadius: 3 }}>
				<CardContent sx={{ pb: 2 }}>
					<Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
						<RobotIcon color="primary" />
						<Typography variant="h6" component="h2" fontWeight={600}>
							Управление Роботом
						</Typography>
						<Chip 
							label={`(${robotPos?.x ?? '?'}, ${robotPos?.y ?? '?'})`} 
							size="small" 
							color="primary" 
							variant="outlined"
						/>
					</Box>

					{/* Стрелки управления */}
					<Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
						<Tooltip title="Вверх (W)">
							<IconButton 
								onClick={() => moveRobot('up')}
								color="primary"
								sx={{ 
									bgcolor: 'primary.50',
									'&:hover': { bgcolor: 'primary.100' }
								}}
							>
								<ArrowUpwardIcon />
							</IconButton>
						</Tooltip>
						
						<Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
							<Tooltip title="Влево (A)">
								<IconButton 
									onClick={() => moveRobot('left')}
									color="primary"
									sx={{ 
										bgcolor: 'primary.50',
										'&:hover': { bgcolor: 'primary.100' }
									}}
								>
									<ArrowBackIcon />
								</IconButton>
							</Tooltip>
							
							<Box sx={{ width: 40, height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
								<LocationOnIcon color="primary" />
							</Box>
							
							<Tooltip title="Вправо (D)">
								<IconButton 
									onClick={() => moveRobot('right')}
									color="primary"
									sx={{ 
										bgcolor: 'primary.50',
										'&:hover': { bgcolor: 'primary.100' }
									}}
								>
									<ArrowForwardIcon />
								</IconButton>
							</Tooltip>
						</Box>
						
						<Tooltip title="Вниз (S)">
							<IconButton 
								onClick={() => moveRobot('down')}
								color="primary"
								sx={{ 
									bgcolor: 'primary.50',
									'&:hover': { bgcolor: 'primary.100' }
								}}
							>
								<ArrowDownwardIcon />
							</IconButton>
						</Tooltip>
					</Box>

					{/* Действия с маркерами и клетками */}
					<Box sx={{ mt: 3 }}>
						<Grid container spacing={1}>
							<Grid item xs={6}>
								<Tooltip title="Поставить маркер (Q)">
									<Button 
										onClick={putMarker}
										startIcon={<AddLocationIcon />}
										color="success"
										variant="contained" 
										fullWidth
										size="small"
										sx={{ borderRadius: 2 }}
									>
										+ Маркер
									</Button>
								</Tooltip>
							</Grid>
							<Grid item xs={6}>
								<Tooltip title="Убрать маркер (E)">
									<Button 
										onClick={pickMarker}
										startIcon={<DeleteOutlineIcon />}
										color="error" 
										variant="contained"
										fullWidth
										size="small"
										sx={{ borderRadius: 2 }}
									>
										- Маркер
									</Button>
								</Tooltip>
							</Grid>
							<Grid item xs={6}>
								<Tooltip title="Закрасить клетку (Z)">
									<Button 
										onClick={paintCell}
										startIcon={<BrushIcon />}
										color="warning"
										variant="contained" 
										fullWidth
										size="small"
										sx={{ borderRadius: 2 }}
									>
										Закрасить
									</Button>
								</Tooltip>
							</Grid>
							<Grid item xs={6}>
								<Tooltip title="Очистить клетку (X)">
									<Button 
										onClick={clearCell}
										startIcon={<ClearIcon />}
										color="info" 
										variant="contained"
										fullWidth
										size="small"
										sx={{ borderRadius: 2 }}
									>
										Очистить
									</Button>
								</Tooltip>
							</Grid>
						</Grid>
					</Box>
				</CardContent>
			</Card>

			{/* Настройки поля */}
			<Card elevation={2} sx={{ borderRadius: 3 }}>
				<CardContent sx={{ pb: 2 }}>
					<Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
						<SettingsIcon color="primary" />
						<Typography variant="h6" component="h2" fontWeight={600}>
							Настройки Поля
						</Typography>
						<Chip 
							label={`${width}×${height}`} 
							size="small" 
							color="secondary" 
							variant="outlined"
						/>
					</Box>

					{/* Режим редактирования */}
					<Box sx={{ mb: 2 }}>
						<FormControlLabel
							control={
								<Switch
									checked={editMode}
									onChange={toggleEditMode}
									color="primary"
								/>
							}
							label={
								<Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
									<EditIcon fontSize="small" />
									<Typography variant="body2">
										Режим редактирования
									</Typography>
								</Box>
							}
						/>
					</Box>

					{/* Управление размерами */}
					<Accordion disabled={!editMode} sx={{ boxShadow: 1, borderRadius: 2 }}>
						<AccordionSummary expandIcon={<ExpandMoreIcon />}>
							<Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
								<GridIcon fontSize="small" />
								<Typography variant="body2">Размеры поля</Typography>
							</Box>
						</AccordionSummary>
						<AccordionDetails>
							<Grid container spacing={1}>
								<Grid item xs={6}>
									<Typography variant="caption" color="text.secondary">
										Ширина
									</Typography>
									<Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
										<Button 
											onClick={decreaseWidth}
											variant="outlined"
											size="small"
											disabled={!editMode || width <= 1}
											sx={{ minWidth: 30, borderRadius: 2 }}
										>
											<RemoveIcon fontSize="small" />
										</Button>
										<TextField
											value={width}
											size="small"
											disabled
											sx={{ 
												width: 60,
												'& .MuiInputBase-input': { 
													textAlign: 'center',
													fontSize: '0.875rem'
												}
											}}
										/>
										<Button 
											onClick={increaseWidth}
											variant="outlined"
											size="small"
											disabled={!editMode}
											sx={{ minWidth: 30, borderRadius: 2 }}
										>
											<AddIcon fontSize="small" />
										</Button>
									</Box>
								</Grid>
								<Grid item xs={6}>
									<Typography variant="caption" color="text.secondary">
										Высота
									</Typography>
									<Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
										<Button 
											onClick={decreaseHeight}
											variant="outlined"
											size="small"
											disabled={!editMode || height <= 1}
											sx={{ minWidth: 30, borderRadius: 2 }}
										>
											<RemoveIcon fontSize="small" />
										</Button>
										<TextField
											value={height}
											size="small"
											disabled
											sx={{ 
												width: 60,
												'& .MuiInputBase-input': { 
													textAlign: 'center',
													fontSize: '0.875rem'
												}
											}}
										/>
										<Button 
											onClick={increaseHeight}
											variant="outlined"
											size="small"
											disabled={!editMode}
											sx={{ minWidth: 30, borderRadius: 2 }}
										>
											<AddIcon fontSize="small" />
										</Button>
									</Box>
								</Grid>
							</Grid>
						</AccordionDetails>
					</Accordion>
				</CardContent>
			</Card>

			{/* Дополнительные функции */}
			<Card elevation={1} sx={{ borderRadius: 3 }}>
				<CardContent sx={{ pb: 2 }}>
					<Typography variant="h6" component="h2" fontWeight={600} sx={{ mb: 2 }}>
						Дополнительно
					</Typography>
					
					<Grid container spacing={1}>
						<Grid item xs={6}>
							<Tooltip title="Открыть справку (F1)">
								<Button 
									onClick={openHelpDialog}
									startIcon={<HelpOutlineIcon />}
									color="info" 
									variant="outlined"
									fullWidth
									size="small"
									sx={{ borderRadius: 2 }}
								>
									Помощь
								</Button>
							</Tooltip>
						</Grid>
						<Grid item xs={6}>
							<Tooltip title="Импортировать обстановку из файла .fil">
								<Button 
									onClick={handleImportClick}
									startIcon={<FileUploadIcon />}
									color="secondary"
									variant="outlined" 
									fullWidth
									size="small"
									sx={{ borderRadius: 2 }}
								>
									Импорт
								</Button>
							</Tooltip>
							<input 
								type="file" 
								accept=".fil" 
								ref={fileInputRef} 
								style={{ display: 'none' }}
								onChange={handleFileChange}
							/>
						</Grid>
					</Grid>
				</CardContent>
			</Card>

			<HelpDialog open={helpOpen} onClose={closeHelpDialog} />
		</Box>
	);
});

export default ControlPanel;
// FILE END: ControlPanel.jsx