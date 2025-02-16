/**
 * @file ControlPanel.jsx
 * @description Компонент панели управления симулятором робота.
 * Панель позволяет управлять перемещением робота, установкой и снятием маркеров, окраской клеток,
 * а также изменением размеров игрового поля. Кроме того, предусмотрены функции импорта поля из файла
 * (.FIL) и вызова диалога помощи.
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
import './ControlPanel.css'; // Стили для панели управления
import HelpDialog from '../Help/HelpDialog';

/**
 * Функция для парсинга кода стен для заданной клетки.
 *
 * @param {number} code - Числовой код, определяющий наличие стен.
 * @param {number} x - Координата x клетки.
 * @param {number} y - Координата y клетки.
 * @returns {string[]} Массив строк, каждая из которых описывает стену в формате "x1,y1,x2,y2".
 */
const parseWallCode = (code, x, y) => {
	const arr = [];
	if (code & 8) arr.push(`${x},${y},${x + 1},${y}`);
	if (code & 4) arr.push(`${x + 1},${y},${x + 1},${y + 1}`);
	if (code & 2) arr.push(`${x},${y + 1},${x + 1},${y + 1}`);
	if (code & 1) arr.push(`${x},${y},${x},${y + 1}`);
	return arr;
};

/**
 * Компонент панели управления.
 *
 * @param {Object} props - Свойства компонента.
 * @param {Object} props.robotPos - Текущая позиция робота ({x, y}).
 * @param {function} props.setRobotPos - Функция для обновления позиции робота.
 * @param {Set} props.walls - Множество временных стен.
 * @param {function} props.setWalls - Функция для обновления множества стен.
 * @param {Set} props.permanentWalls - Множество постоянных стен.
 * @param {Object} props.markers - Объект с маркерами, ключами являются координаты.
 * @param {function} props.setMarkers - Функция для обновления маркеров.
 * @param {Set} props.coloredCells - Множество закрашенных клеток.
 * @param {function} props.setColoredCells - Функция для обновления закрашенных клеток.
 * @param {number} props.width - Ширина игрового поля.
 * @param {function} props.setWidth - Функция для изменения ширины поля.
 * @param {number} props.height - Высота игрового поля.
 * @param {function} props.setHeight - Функция для изменения высоты поля.
 * @param {number} props.cellSize - Размер клетки.
 * @param {function} props.setCellSize - Функция для изменения размера клетки.
 * @param {boolean} props.editMode - Флаг, указывающий, включен ли режим редактирования.
 * @param {function} props.setEditMode - Функция для переключения режима редактирования.
 * @param {function} props.setStatusMessage - Функция для обновления статусного сообщения.
 * @returns {JSX.Element} Разметка панели управления.
 */
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

	const moveRobot = useCallback((direction) => {
		let newPos = {...robotPos};
		let hintKey = '';
		let actionKey = '';

		if (direction === 'up') {
			hintKey = 'moveRobotUp';
			actionKey = 'moveRobotUpBlocked';
			if (newPos.y > 0 && !walls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`) && !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`)) {
				newPos.y -= 1;
			} else {
				setStatusMessage(getHint(actionKey, editMode));
				return;
			}
		} else if (direction === 'down') {
			hintKey = 'moveRobotDown';
			actionKey = 'moveRobotDownBlocked';
			if (newPos.y < height - 1 && !walls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`) && !permanentWalls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`)) {
				newPos.y += 1;
			} else {
				setStatusMessage(getHint(actionKey, editMode));
				return;
			}
		} else if (direction === 'left') {
			hintKey = 'moveRobotLeft';
			actionKey = 'moveRobotLeftBlocked';
			if (newPos.x > 0 && !walls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`) && !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`)) {
				newPos.x -= 1;
			} else {
				setStatusMessage(getHint(actionKey, editMode));
				return;
			}
		} else if (direction === 'right') {
			hintKey = 'moveRobotRight';
			actionKey = 'moveRobotRightBlocked';
			if (newPos.x < width - 1 && !walls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`) && !permanentWalls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`)) {
				newPos.x += 1;
			} else {
				setStatusMessage(getHint(actionKey, editMode));
				return;
			}
		}

		setRobotPos(newPos);
		setStatusMessage(getHint(hintKey, editMode));
		// Удалён вызов fetch обновления – обновление состояния теперь централизовано в RobotSimulator.
	}, [robotPos, walls, permanentWalls, editMode, setRobotPos, setStatusMessage, width]);

	const putMarker = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (!markers[posKey]) {
			const newMarkers = {...markers, [posKey]: 1};
			setMarkers(newMarkers);
			setStatusMessage(getHint('putMarker', editMode));
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
		} else {
			setStatusMessage(getHint('cellAlreadyClear', editMode));
		}
	};

	const toggleEditMode = () => {
		const newMode = !editMode;
		setEditMode(newMode);
		if (newMode) {
			setStatusMessage(getHint('enterEditMode', newMode));
		} else {
			setStatusMessage(getHint('exitEditMode', newMode));
		}
	};

	const increaseWidth = () => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', editMode));
			return;
		}
		setWidth(width + 1);
		setStatusMessage(getHint('increaseWidth', editMode));
	};

	const decreaseWidth = () => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', editMode));
			return;
		}
		if (width > 1) {
			setWidth(width - 1);
			setStatusMessage(getHint('decreaseWidth', editMode));
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
	};

	const decreaseHeight = () => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', editMode));
			return;
		}
		if (height > 1) {
			setHeight(height - 1);
			setStatusMessage(getHint('decreaseHeight', editMode));
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
		} catch (error) {
			setStatusMessage(getHint('importError', editMode) + error.message);
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

			const computePermanentWalls = (width, height) => {
				const pWalls = new Set();
				for (let x = 0; x < width; x++) {
					pWalls.add(`${x},0,${x + 1},0`);
					pWalls.add(`${x},${height},${x + 1},${height}`);
				}
				for (let y = 0; y < height; y++) {
					pWalls.add(`0,${y},0,${y + 1}`);
					pWalls.add(`${width},${y},${width},${y + 1}`);
				}
				return pWalls;
			};

			setWidth(wFile);
			setHeight(hFile);
			setRobotPos({x: rx, y: ry});
			setWalls(newWalls);
			setColoredCells(newColored);
			setMarkers(newMarkers);
			setStatusMessage("Поле успешно обновлено из файла.");
		} catch (error) {
			setStatusMessage("Ошибка при импорте файла: " + error.message);
		}
	};

	return (
		<>
			<Card className="control-panel">
				<CardHeader title="Управление"/>
				<CardContent>
					<Grid container spacing={2}>
						<Grid item xs={12} style={{textAlign: 'center'}}>
							<Button
								onClick={() => moveRobot('up')}
								color="primary"
								variant="contained"
								className="control-button"
								aria-label="Вверх"
							>
								<ArrowUpward/>
								Вверх
							</Button>
						</Grid>
						<Grid item xs={6} style={{textAlign: 'right'}}>
							<Button
								onClick={() => moveRobot('left')}
								color="primary"
								variant="contained"
								className="control-button"
								aria-label="Влево"
							>
								<ArrowBack/>
								Влево
							</Button>
						</Grid>
						<Grid item xs={6} style={{textAlign: 'left'}}>
							<Button
								onClick={() => moveRobot('right')}
								color="primary"
								variant="contained"
								className="control-button"
								aria-label="Вправо"
							>
								<ArrowForward/>
								Вправо
							</Button>
						</Grid>
						<Grid item xs={12} style={{textAlign: 'center'}}>
							<Button
								onClick={() => moveRobot('down')}
								color="primary"
								variant="contained"
								className="control-button"
								aria-label="Вниз"
							>
								<ArrowDownward/>
								Вниз
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button
								onClick={putMarker}
								color="success"
								variant="contained"
								className="control-button"
								aria-label="Положить маркер"
							>
								<AddLocation style={{marginRight: '8px'}}/>
								Положить маркер
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button
								onClick={pickMarker}
								color="error"
								variant="contained"
								className="control-button"
								aria-label="Поднять маркер"
							>
								<DeleteOutline style={{marginRight: '8px'}}/>
								Поднять маркер
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button
								onClick={paintCell}
								color="warning"
								variant="contained"
								className="control-button"
								aria-label="Покрасить"
							>
								<Brush style={{marginRight: '8px'}}/>
								Покрасить
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button
								onClick={clearCell}
								color="info"
								variant="contained"
								className="control-button"
								aria-label="Очистить"
							>
								<Clear style={{marginRight: '8px'}}/>
								Очистить
							</Button>
						</Grid>
						<Grid item xs={12}>
							<Button
								onClick={toggleEditMode}
								color="secondary"
								variant="contained"
								className="control-button"
								aria-label="Toggle Edit Mode"
							>
								<Edit style={{marginRight: '8px'}}/>
								{editMode ? 'Выключить Режим рисования' : 'Включить Режим рисования'}
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button
								onClick={increaseWidth}
								color="primary"
								variant="contained"
								className="control-button"
								aria-label="Increase Field Width"
							>
								<Add style={{marginRight: '8px'}}/>
								Поле шире
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button
								onClick={decreaseWidth}
								color="primary"
								variant="contained"
								className="control-button"
								aria-label="Decrease Field Width"
							>
								<Remove style={{marginRight: '8px'}}/>
								Поле уже
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button
								onClick={increaseHeight}
								color="primary"
								variant="contained"
								className="control-button"
								aria-label="Increase Field Height"
							>
								<Add style={{marginRight: '8px'}}/>
								Поле выше
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button
								onClick={decreaseHeight}
								color="primary"
								variant="contained"
								className="control-button"
								aria-label="Decrease Field Height"
							>
								<Remove style={{marginRight: '8px'}}/>
								Поле ниже
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button
								onClick={() => setHelpOpen(true)}
								color="info"
								variant="contained"
								className="control-button"
								aria-label="Help"
							>
								<HelpOutline style={{marginRight: '8px'}}/>
								Помощь
							</Button>
						</Grid>
						<Grid item xs={6}>
							<Button
								onClick={handleImportField}
								color="secondary"
								variant="contained"
								className="control-button"
								aria-label="Import .fil"
							>
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
