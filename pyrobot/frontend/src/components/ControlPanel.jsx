import React, {memo, useCallback, useRef} from 'react';
import {Button, Card, CardContent, CardHeader, Grid} from '@mui/material';
import {getHint} from '../hints';

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

	const moveRobot = useCallback((direction) => {
		setRobotPos((prevPos) => {
			let newPos = {...prevPos};
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
					return prevPos;
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
					return prevPos;
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
					return prevPos;
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
					return prevPos;
				}
			}

			setStatusMessage(getHint(hintKey, editMode));
			return newPos;
		});
	}, [height, width, walls, permanentWalls, editMode, setStatusMessage]);

	const putMarker = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (!markers[posKey]) {
			const newMarkers = {...markers};
			newMarkers[posKey] = 1;
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
			const newSet = new Set(coloredCells);
			newSet.add(posKey);
			setColoredCells(newSet);
			setStatusMessage(getHint('paintCell', editMode));
		} else {
			setStatusMessage(getHint('cellAlreadyPainted', editMode));
		}
	};

	const clearCell = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		if (coloredCells.has(posKey)) {
			const newSet = new Set(coloredCells);
			newSet.delete(posKey);
			setColoredCells(newSet);
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
		}
	};

	const parseAndApplyFieldFile = (content) => {
		try {
			setRobotPos({x: 0, y: 0});
			setWalls(new Set());
			setColoredCells(new Set());
			setMarkers({});
			const lines = content.split('\n').filter(line => {
				return !line.startsWith(';') && line.trim() !== '';
			});
			const [wFile, hFile] = lines[0].split(/\s+/).map(Number);
			setWidth(wFile);
			setHeight(hFile);
			const [rx, ry] = lines[1].split(/\s+/).map(Number);
			setRobotPos({x: rx, y: ry});
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
			setWalls(newWalls);
			setColoredCells(newColored);
			setMarkers(newMarkers);
		} catch (error) {
			setStatusMessage(getHint('parseError', editMode) + error.message);
		}
	};

	const parseWallCode = (code, x, y) => {
		const arr = [];
		if (code & 8) arr.push(`${x},${y},${x + 1},${y}`);
		if (code & 4) arr.push(`${x + 1},${y},${x + 1},${y + 1}`);
		if (code & 2) arr.push(`${x},${y + 1},${x + 1},${y + 1}`);
		if (code & 1) arr.push(`${x},${y},${x},${y + 1}`);
		return arr;
	};

	return (
		<Card className="control-panel">
			<CardHeader title="Управление"/>
			<CardContent>
				<Grid container spacing={2}>
					<Grid item xs={12}>
						<Button onClick={() => moveRobot('up')} className="control-button">
							Вверх
						</Button>
					</Grid>
					<Grid item xs={6}>
						<Button onClick={() => moveRobot('left')} className="control-button">
							Влево
						</Button>
					</Grid>
					<Grid item xs={6}>
						<Button onClick={() => moveRobot('right')} className="control-button">
							Вправо
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={() => moveRobot('down')} className="control-button">
							Вниз
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={putMarker} className="control-button">
							Положить маркер
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={pickMarker} className="control-button">
							Поднять маркер
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={paintCell} className="control-button">
							Покрасить
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={clearCell} className="control-button">
							Очистить
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={toggleEditMode} className="control-button">
							{editMode ? 'Выключить Режим рисования' : 'Включить Режим рисования'}
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={increaseWidth} className="control-button">
							Поле шире
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={decreaseWidth} className="control-button">
							Поле уже
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={increaseHeight} className="control-button">
							Поле выше
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={decreaseHeight} className="control-button">
							Поле ниже
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={() => setStatusMessage(getHint('help', editMode))} className="control-button">
							Помощь
						</Button>
					</Grid>
					<Grid item xs={12}>
						<Button onClick={handleImportField} className="control-button">
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
	);
});

export default ControlPanel;
