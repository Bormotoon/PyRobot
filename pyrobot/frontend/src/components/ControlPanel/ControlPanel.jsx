/**
 * @file ControlPanel.jsx
 * @description Компонент панели управления симулятором робота.
 * Панель позволяет управлять перемещением робота, установкой и снятием маркеров, окраской клеток,
 * а также изменением размеров игрового поля. Кроме того, предусмотрены функции импорта поля из файла
 * и вызова диалога помощи.
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
import './ControlPanel.css'; // Стили для .control-panel и .control-button
// Импорт компонента диалога с инструкцией
import HelpDialog from '../Help/HelpDialog';

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
 * @param {boolean} props.editMode - Флаг, указывающий включен ли режим редактирования.
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
	// Ссылка на элемент input для импорта файла поля
	const fileInputRef = useRef(null);
	// Локальное состояние для управления видимостью диалога помощи
	const [helpOpen, setHelpOpen] = useState(false);

	/**
	 * Функция для перемещения робота в указанном направлении.
	 *
	 * @param {string} direction - Направление перемещения ('up', 'down', 'left', 'right').
	 */
	const moveRobot = useCallback((direction) => {
		setRobotPos((prevPos) => {
			// Копируем предыдущую позицию робота
			let newPos = {...prevPos};
			// Ключ для получения подсказки при успешном перемещении
			let hintKey = '';
			// Ключ для получения подсказки при блокировке перемещения
			let actionKey = '';

			if (direction === 'up') {
				hintKey = 'moveRobotUp';
				actionKey = 'moveRobotUpBlocked';
				// Проверяем, можно ли переместиться вверх: позиция не выходит за пределы поля и нет стены сверху
				if (newPos.y > 0 && !walls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`) && !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`)) {
					newPos.y -= 1;
				} else {
					// Если движение заблокировано, устанавливаем соответствующее сообщение и возвращаем прежнюю позицию
					setStatusMessage(getHint(actionKey, editMode));
					return prevPos;
				}
			} else if (direction === 'down') {
				hintKey = 'moveRobotDown';
				actionKey = 'moveRobotDownBlocked';
				// Проверяем, можно ли переместиться вниз
				if (newPos.y < height - 1 && !walls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`) && !permanentWalls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`)) {
					newPos.y += 1;
				} else {
					setStatusMessage(getHint(actionKey, editMode));
					return prevPos;
				}
			} else if (direction === 'left') {
				hintKey = 'moveRobotLeft';
				actionKey = 'moveRobotLeftBlocked';
				// Проверяем возможность перемещения влево
				if (newPos.x > 0 && !walls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`) && !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`)) {
					newPos.x -= 1;
				} else {
					setStatusMessage(getHint(actionKey, editMode));
					return prevPos;
				}
			} else if (direction === 'right') {
				hintKey = 'moveRobotRight';
				actionKey = 'moveRobotRightBlocked';
				// Проверяем возможность перемещения вправо
				if (newPos.x < width - 1 && !walls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`) && !permanentWalls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`)) {
					newPos.x += 1;
				} else {
					setStatusMessage(getHint(actionKey, editMode));
					return prevPos;
				}
			}

			// Устанавливаем сообщение с подсказкой для успешного перемещения
			setStatusMessage(getHint(hintKey, editMode));
			return newPos;
		});
	}, [height, width, walls, permanentWalls, editMode, setStatusMessage, setRobotPos]);

	/**
	 * Функция для установки маркера в текущей позиции робота.
	 */
	const putMarker = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		// Если маркер отсутствует, добавляем его
		if (!markers[posKey]) {
			const newMarkers = {...markers};
			newMarkers[posKey] = 1;
			setMarkers(newMarkers);
			setStatusMessage(getHint('putMarker', editMode));
		} else {
			// Если маркер уже установлен, выводим сообщение об ошибке
			setStatusMessage(getHint('markerAlreadyExists', editMode));
		}
	};

	/**
	 * Функция для снятия маркера с текущей позиции робота.
	 */
	const pickMarker = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		// Если маркер существует, удаляем его
		if (markers[posKey]) {
			const newMarkers = {...markers};
			delete newMarkers[posKey];
			setMarkers(newMarkers);
			setStatusMessage(getHint('pickMarker', editMode));
		} else {
			setStatusMessage(getHint('noMarkerHere', editMode));
		}
	};

	/**
	 * Функция для окрашивания текущей клетки.
	 */
	const paintCell = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		// Если клетка еще не окрашена, добавляем ее в множество окрашенных
		if (!coloredCells.has(posKey)) {
			const newSet = new Set(coloredCells);
			newSet.add(posKey);
			setColoredCells(newSet);
			setStatusMessage(getHint('paintCell', editMode));
		} else {
			setStatusMessage(getHint('cellAlreadyPainted', editMode));
		}
	};

	/**
	 * Функция для очистки окрашенной клетки.
	 */
	const clearCell = () => {
		const posKey = `${robotPos.x},${robotPos.y}`;
		// Если клетка окрашена, удаляем ее из множества окрашенных
		if (coloredCells.has(posKey)) {
			const newSet = new Set(coloredCells);
			newSet.delete(posKey);
			setColoredCells(newSet);
			setStatusMessage(getHint('clearCell', editMode));
		} else {
			setStatusMessage(getHint('cellAlreadyClear', editMode));
		}
	};

	/**
	 * Функция для переключения режима редактирования (рисования).
	 * При активации режима выводится сообщение о входе в режим, при деактивации — сообщение о выходе.
	 */
	const toggleEditMode = () => {
		const newMode = !editMode;
		setEditMode(newMode);
		if (newMode) {
			setStatusMessage(getHint('enterEditMode', newMode));
		} else {
			setStatusMessage(getHint('exitEditMode', newMode));
		}
	};

	/**
	 * Функция для увеличения ширины игрового поля.
	 * Работает только в режиме редактирования.
	 */
	const increaseWidth = () => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', editMode));
			return;
		}
		setWidth(width + 1);
		setStatusMessage(getHint('increaseWidth', editMode));
	};

	/**
	 * Функция для уменьшения ширины игрового поля.
	 * Работает только в режиме редактирования, и ширина не может быть меньше 1.
	 */
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

	/**
	 * Функция для увеличения высоты игрового поля.
	 * Работает только в режиме редактирования.
	 */
	const increaseHeight = () => {
		if (!editMode) {
			setStatusMessage(getHint('editModeRequired', editMode));
			return;
		}
		setHeight(height + 1);
		setStatusMessage(getHint('increaseHeight', editMode));
	};

	/**
	 * Функция для уменьшения высоты игрового поля.
	 * Работает только в режиме редактирования, и высота не может быть меньше 1.
	 */
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

	/**
	 * Функция для обработки импорта файла поля.
	 * Инициирует клик по скрытому input для выбора файла.
	 */
	const handleImportField = () => {
		fileInputRef.current.click();
	};

	/**
	 * Обработчик изменения выбранного файла для импорта.
	 * Считывает содержимое файла и вызывает парсинг.
	 *
	 * @param {Event} e - Событие изменения файла.
	 */
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

	/**
	 * Функция для парсинга и применения содержимого файла поля.
	 *
	 * @param {string} content - Содержимое файла.
	 */
	const parseAndApplyFieldFile = (content) => {
		try {
			// Сброс текущих данных поля
			setRobotPos({x: 0, y: 0});
			setWalls(new Set());
			setColoredCells(new Set());
			setMarkers({});
			// Разбиваем содержимое файла на строки и отфильтровываем пустые строки и комментарии (начинающиеся с ';')
			const lines = content.split('\n').filter(line => line.trim() !== '' && !line.startsWith(';'));
			// Первая строка файла содержит размеры поля
			const [wFile, hFile] = lines[0].split(/\s+/).map(Number);
			setWidth(wFile);
			setHeight(hFile);
			// Вторая строка файла содержит начальную позицию робота
			const [rx, ry] = lines[1].split(/\s+/).map(Number);
			setRobotPos({x: rx, y: ry});
			// Инициализируем новые множества и объекты для стен, окрашенных клеток и маркеров
			const newWalls = new Set();
			const newColored = new Set();
			const newMarkers = {};
			// Обрабатываем оставшиеся строки файла, содержащие информацию о клетках
			for (let i = 2; i < lines.length; i++) {
				const parts = lines[i].split(/\s+/);
				const xx = parseInt(parts[0], 10);
				const yy = parseInt(parts[1], 10);
				const wcode = parseInt(parts[2], 10);
				const color = parts[3];
				const point = parts[8];
				// Если значение color равно '1', добавляем клетку в множество окрашенных
				if (color === '1') newColored.add(`${xx},${yy}`);
				// Если значение point равно '1', устанавливаем маркер в данной клетке
				if (point === '1') newMarkers[`${xx},${yy}`] = 1;
				// Парсим код стен для данной клетки и добавляем каждую стену в множество
				const wallsParsed = parseWallCode(wcode, xx, yy);
				wallsParsed.forEach(w => newWalls.add(w));
			}
			// Применяем полученные данные
			setWalls(newWalls);
			setColoredCells(newColored);
			setMarkers(newMarkers);
		} catch (error) {
			setStatusMessage(getHint('parseError', editMode) + error.message);
		}
	};

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
		// Если установлен бит 8, добавляем верхнюю стену
		if (code & 8) arr.push(`${x},${y},${x + 1},${y}`);
		// Если установлен бит 4, добавляем правую стену
		if (code & 4) arr.push(`${x + 1},${y},${x + 1},${y + 1}`);
		// Если установлен бит 2, добавляем нижнюю стену
		if (code & 2) arr.push(`${x},${y + 1},${x + 1},${y + 1}`);
		// Если установлен бит 1, добавляем левую стену
		if (code & 1) arr.push(`${x},${y},${x},${y + 1}`);
		return arr;
	};

	// Разметка панели управления
	return (<>
			<Card className="control-panel">
				<CardHeader title="Управление"/>
				<CardContent>
					<Grid container spacing={2}>
						{/* Кнопки для перемещения робота */}
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

						{/* Кнопки для работы с маркерами */}
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

						{/* Кнопки для окрашивания и очистки клетки */}
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

						{/* Кнопка для переключения режима редактирования */}
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

						{/* Кнопки для изменения размеров игрового поля */}
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

						{/* Кнопки для вызова диалога помощи и импорта файла */}
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
							{/* Скрытый input для выбора файла */}
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
			{/* Диалог помощи */}
			<HelpDialog open={helpOpen} onClose={() => setHelpOpen(false)}/>
		</>);
});

export default ControlPanel;
