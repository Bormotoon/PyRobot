/**
 * @file ControlPanel.jsx
 * @description Компонент панели управления симулятором робота.
 * Позволяет управлять перемещением робота, маркерами, окраской клеток и размерами поля.
 */

import React, {memo, useCallback, useRef, useState} from 'react';
import {Button, Card, CardContent, CardHeader, Grid} from '@mui/material';
import {
	Add,
	AddLocation,
	ArrowBack,
	ArrowDownward,
	ArrowForward,
	ArrowUpward,
	Brush,
	Clear,
	DeleteOutline,
	Edit,
	FileUpload,
	HelpOutline,
	Remove,
} from '@mui/icons-material';
import {getHint} from '../hints';
import './ControlPanel.css';
import HelpDialog from '../Help/HelpDialog';
// Обновлён импорт логгера: теперь импортируем синглтон logger
import logger from '../../Logger';

const parseWallCode = (code, x, y) => {
	const arr = [];
	if (code & 8) arr.push(`${x},${y},${x + 1},${y}`);
	if (code & 4) arr.push(`${x + 1},${y},${x + 1},${y + 1}`);
	if (code & 2) arr.push(`${x},${y + 1},${x + 1},${y + 1}`);
	if (code & 1) arr.push(`${x},${y},${x},${y + 1}`);
	return arr;
};

const ControlPanel = memo(({
	                           robotPos,
	                           setRobotPos,
	                           walls,
	                           setWalls,
	                           permanentWalls,
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
	                           setStatusMessage,
                           }) => {
	const fileInputRef = useRef(null);
	const [helpOpen, setHelpOpen] = useState(false);

	/**
	 * Функция перемещения робота.
	 * @param {string} direction - Направление перемещения.
	 */
	const moveRobot = useCallback((direction) => {
		let newPos = {...robotPos};
		let hintKey = '';
		let actionKey = '';

		if (direction === 'up') {
			hintKey = 'moveRobotUp';
			actionKey = 'moveRobotUpBlocked';
			if (
				newPos.y > 0 &&
				!walls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`) &&
				!permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`)
			) {
				newPos.y -= 1;
			} else {
				setStatusMessage(getHint(actionKey, editMode));
				logger.log_movement(`Попытка перемещения вверх заблокирована. Текущая позиция: (${robotPos.x}, ${robotPos.y})`);
				return;
			}
		} else if (direction === 'down') {
			hintKey = 'moveRobotDown';
			actionKey = 'moveRobotDownBlocked';
			if (
				newPos.y < height - 1 &&
				!walls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`) &&
				!permanentWalls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`)
			) {
				newPos.y += 1;
			} else {
				setStatusMessage(getHint(actionKey, editMode));
				logger.log_movement(`Попытка перемещения вниз заблокирована. Текущая позиция: (${robotPos.x}, ${robotPos.y})`);
				return;
			}
		} else if (direction === 'left') {
			hintKey = 'moveRobotLeft';
			actionKey = 'moveRobotLeftBlocked';
			if (
				newPos.x > 0 &&
				!walls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`) &&
				!permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`)
			) {
				newPos.x -= 1;
			} else {
				setStatusMessage(getHint(actionKey, editMode));
				logger.log_movement(`Попытка перемещения влево заблокирована. Текущая позиция: (${robotPos.x}, ${robotPos.y})`);
				return;
			}
		} else if (direction === 'right') {
			hintKey = 'moveRobotRight';
			actionKey = 'moveRobotRightBlocked';
			if (
				newPos.x < width - 1 &&
				!walls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`) &&
				!permanentWalls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`)
			) {
				newPos.x += 1;
			} else {
				setStatusMessage(getHint(actionKey, editMode));
				logger.log_movement(`Попытка перемещения вправо заблокирована. Текущая позиция: (${robotPos.x}, ${robotPos.y})`);
				return;
			}
		}

		setRobotPos(newPos);
		setStatusMessage(getHint(hintKey, editMode));
		logger.log_movement(`Робот перемещён ${direction}. Новая позиция: (${newPos.x}, ${newPos.y})`);
	}, [robotPos, walls, permanentWalls, editMode, setRobotPos, setStatusMessage, width, height]);

	// Функции для управления маркерами и окраской клеток
	const putMarker = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (!markers[posKey]) {
			const newMarkers = {...markers, [posKey]: 1};
			setMarkers(newMarkers);
			setStatusMessage(getHint('putMarker', editMode));
			logger.log_event(`Маркер установлен в позиции: (${robotPos.x}, ${robotPos.y})`);
		} else {
			setStatusMessage(getHint('markerAlreadyExists', editMode));
		}
	};

	const pickMarker = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (markers[posKey]) {
			const newMarkers = {...markers};
			delete newMarkers[posKey];
			setMarkers(newMarkers);
			setStatusMessage(getHint('pickMarker', editMode));
			logger.log_event(`Маркер снят из позиции: (${robotPos.x}, ${robotPos.y})`);
		} else {
			setStatusMessage(getHint('noMarkerHere', editMode));
		}
	};

	const paintCell = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (!coloredCells.has(posKey)) {
			const newColored = new Set(coloredCells);
			newColored.add(posKey);
			setColoredCells(newColored);
			setStatusMessage(getHint('paintCell', editMode));
			logger.log_event(`Клетка (${robotPos.x}, ${robotPos.y}) закрашена.`);
		} else {
			setStatusMessage(getHint('cellAlreadyPainted', editMode));
		}
	};

	const clearCell = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (coloredCells.has(posKey)) {
			const newColored = new Set(coloredCells);
			newColored.delete(posKey);
			setColoredCells(newColored);
			setStatusMessage(getHint('clearCell', editMode));
			logger.log_event(`Клетка (${robotPos.x}, ${robotPos.y}) очищена.`);
		} else {
			setStatusMessage(getHint('cellAlreadyClear', editMode));
		}
	};

	const toggleEditMode = () => {
		const newMode = !editMode;
		setEditMode(newMode);
		if (newMode) {
			setStatusMessage(getHint('enterEditMode', newMode));
			logger.log_event("Режим редактирования включён.");
		} else {
			setStatusMessage(getHint('exitEditMode', newMode));
			logger.log_event("Режим редактирования выключен.");
		}
	};

	const increaseWidth = () => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', editMode));
			return;
		}
		setWidth(width + 1);
		setStatusMessage(getHint('increaseWidth', editMode));
		logger.log_event(`Ширина поля увеличена до ${width + 1}.`);
	};

	const decreaseWidth = () => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', editMode));
			return;
		}
		if (width > 1) {
			setWidth(width - 1);
			setStatusMessage(getHint('decreaseWidth', editMode));
			logger.log_event(`Ширина поля уменьшена до ${width - 1}.`);
		} else {
			setStatusMessage(getHint('widthCannotBeLessThan1', editMode));
		}
	};

	const increaseHeight = () => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', editMode));
			return;
		}
		setHeight(height + 1);
		setStatusMessage(getHint('increaseHeight', editMode));
		logger.log_event(`Высота поля увеличена до ${height + 1}.`);
	};

	const decreaseHeight = () => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', editMode));
			return;
		}
		if (height > 1) {
			setHeight(height - 1);
			setStatusMessage(getHint('decreaseHeight', editMode));
			logger.log_event(`Высота поля уменьшена до ${height - 1}.`);
		} else {
			setStatusMessage(getHint('heightCannotBeLessThan1', editMode));
		}
	};

	const handleImportField = () => {
		fileInputRef.current.click();
	};

	const handleFileChange = async (e) => {
		const file = e.target.files[0];
		if (!file) return;
		try {
			const content = await file.text();
			parseAndApplyFieldFile(content);
			setStatusMessage(getHint('importSuccess', editMode));
			logger.log_event("Файл поля успешно импортирован.");
		} catch (error) {
			setStatusMessage(getHint('importError', editMode) + error.message);
			logger.log_event(`Ошибка при импорте файла: ${error.message}`);
		} finally {
			e.target.value = "";
		}
	};

	const parseAndApplyFieldFile = (content) => {
		try {
			const lines = content.split('\n').filter(line => line.trim() !== '' && !line.startsWith(';'));
			const [wFile, hFile] = lines[0].split(/\s+/).map(Number);
			const [rx, ry] = lines[1].split(/\s+/).map(Number);
			const newWalls = new Set();
			const newColored = new Set();
			const newMarkers = {};

			for (let i = 2; i < lines.length; i++) {
				const parts = lines[i].split(/\s+/);
				const xx = parseInt(parts[0], 10);
				const yy = parseInt(parts[1], 10);
				const wcode = parseInt(parts[2], 10);
				const color = parts[3];
				const point = parts[8];

				if (color === '1') newColored.add(`${xx},${yy}`);
				if (point === '1') newMarkers[`${xx},${yy}`] = 1;

				const wallsParsed = parseWallCode(wcode, xx, yy);
				wallsParsed.forEach(w => newWalls.add(w));
			}

			setWidth(wFile);
			setHeight(hFile);
			setRobotPos({x: rx, y: ry});
			setWalls(newWalls);
			setColoredCells(newColored);
			setMarkers(newMarkers);
			setStatusMessage("Поле успешно обновлено из файла.");
			logger.log_event("Поле обновлено из импортированного файла.");
		} catch (error) {
			setStatusMessage("Ошибка при импорте файла: " + error.message);
			logger.log_event(`Ошибка при импорте файла: ${error.message}`);
		}
	};

	return (
		<>
			<Card className="control-panel">
				<CardHeader title="Управление"/>
				<CardContent>
					<Grid container spacing={2}>
						<Grid item xs={12} style={{textAlign: 'center'}}>
							<Button onClick={() => moveRobot('up')} color="primary" variant="contained"
							        className="control-button" aria-label="Вверх">
								<ArrowUpward/>
								Вверх
							</Button>
						</Grid>
						<Grid item xs={6} style={{textAlign: 'right'}}>
							<Button onClick={() => moveRobot('left')} color="primary" variant="contained"
							        className="control-button" aria-label="Влево">
								<ArrowBack/>
								Влево
							</Button>
						</Grid>
						<Grid item xs={6} style={{textAlign: 'left'}}>
							<Button onClick={() => moveRobot('right')} color="primary" variant="contained"
							        className="control-button" aria-label="Вправо">
								<ArrowForward/>
								Вправо
							</Button>
						</Grid>
						<Grid item xs={12} style={{textAlign: 'center'}}>
							<Button onClick={() => moveRobot('down')} color="primary" variant="contained"
							        className="control-button" aria-label="Вниз">
								<ArrowDownward/>
								Вниз
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button onClick={putMarker} color="success" variant="contained" className="control-button"
							        aria-label="Положить маркер">
								<AddLocation style={{marginRight: '8px'}}/>
								Положить маркер
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button onClick={pickMarker} color="error" variant="contained" className="control-button"
							        aria-label="Поднять маркер">
								<DeleteOutline style={{marginRight: '8px'}}/>
								Поднять маркер
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button onClick={paintCell} color="warning" variant="contained" className="control-button"
							        aria-label="Покрасить">
								<Brush style={{marginRight: '8px'}}/>
								Покрасить
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button onClick={clearCell} color="info" variant="contained" className="control-button"
							        aria-label="Очистить">
								<Clear style={{marginRight: '8px'}}/>
								Очистить
							</Button>
						</Grid>
						<Grid item xs={12}>
							<Button onClick={toggleEditMode} color="secondary" variant="contained"
							        className="control-button" aria-label="Toggle Edit Mode">
								<Edit style={{marginRight: '8px'}}/>
								{editMode ? 'Выключить Режим рисования' : 'Включить Режим рисования'}
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button onClick={increaseWidth} color="primary" variant="contained"
							        className="control-button" aria-label="Increase Field Width">
								<Add style={{marginRight: '8px'}}/>
								Поле шире
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button onClick={decreaseWidth} color="primary" variant="contained"
							        className="control-button" aria-label="Decrease Field Width">
								<Remove style={{marginRight: '8px'}}/>
								Поле уже
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button onClick={increaseHeight} color="primary" variant="contained"
							        className="control-button" aria-label="Increase Field Height">
								<Add style={{marginRight: '8px'}}/>
								Поле выше
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button onClick={decreaseHeight} color="primary" variant="contained"
							        className="control-button" aria-label="Decrease Field Height">
								<Remove style={{marginRight: '8px'}}/>
								Поле ниже
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button onClick={() => setHelpOpen(true)} color="info" variant="contained"
							        className="control-button" aria-label="Help">
								<HelpOutline style={{marginRight: '8px'}}/>
								Помощь
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button onClick={handleImportField} color="secondary" variant="contained"
							        className="control-button" aria-label="Import .fil">
								<FileUpload style={{marginRight: '8px'}}/>
								Импорт .fil
							</Button>
							<input
								type="file"
								ref={fileInputRef}
								style={{display: 'none'}}
								onChange={handleFileChange}
							/>
						</Grid>
					</Grid>
				</CardContent>
			</Card>
			<HelpDialog open={helpOpen} onClose={() => setHelpOpen(false)}/>
		</>
	);
});

export default ControlPanel;
