// /frontend/src/components/ControlPanel.jsx

import React, { useRef } from 'react';
import { Button, Card, CardHeader, CardContent, Grid, Typography } from '@mui/material';
import { ChevronUp, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react';

// Импорт функции для подсказок
import { getHint } from '../hints';

/**
 * Компонент панели управления (кнопки движения, маркеры, покраска,
 * изменение размеров поля, режим рисования, импорт .fil).
 */
function ControlPanel({
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
  setStatusMessage
}) {
  const fileInputRef = useRef(null);

  /**
   * Двигаем робота кнопками: учитываем стены (обычные + постоянные) и край поля.
   * Если движение успешно — выводим подсказку через getHint('moveRobotUp'...) и т.д.
   */
  const moveRobot = (direction) => {
    setRobotPos(prevPos => {
      let newPos = { ...prevPos };

      // Определяем ключ подсказки
      let hintKey = '';

      if (direction === 'up') {
        hintKey = 'moveRobotUp';
        if (
          newPos.y > 0 &&
          !walls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`) &&
          !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x + 1},${newPos.y}`)
        ) {
          newPos.y -= 1;
        } else {
          setStatusMessage('Робот не может пойти вверх (стена или край).');
          return prevPos;
        }
      } else if (direction === 'down') {
        hintKey = 'moveRobotDown';
        if (
          newPos.y < height - 1 &&
          !walls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`) &&
          !permanentWalls.has(`${newPos.x},${newPos.y + 1},${newPos.x + 1},${newPos.y + 1}`)
        ) {
          newPos.y += 1;
        } else {
          setStatusMessage('Робот не может пойти вниз (стена или край).');
          return prevPos;
        }
      } else if (direction === 'left') {
        hintKey = 'moveRobotLeft';
        if (
          newPos.x > 0 &&
          !walls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`) &&
          !permanentWalls.has(`${newPos.x},${newPos.y},${newPos.x},${newPos.y + 1}`)
        ) {
          newPos.x -= 1;
        } else {
          setStatusMessage('Робот не может пойти влево (стена или край).');
          return prevPos;
        }
      } else if (direction === 'right') {
        hintKey = 'moveRobotRight';
        if (
          newPos.x < width - 1 &&
          !walls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`) &&
          !permanentWalls.has(`${newPos.x + 1},${newPos.y},${newPos.x + 1},${newPos.y + 1}`)
        ) {
          newPos.x += 1;
        } else {
          setStatusMessage('Робот не может пойти вправо (стена или край).');
          return prevPos;
        }
      }

      setStatusMessage(getHint(hintKey, editMode));
      return newPos;
    });
  };

  /**
   * Положить маркер
   */
  const putMarker = () => {
    const posKey = `${robotPos.x},${robotPos.y}`;
    if (!markers[posKey]) {
      const newMarkers = { ...markers };
      newMarkers[posKey] = 1;
      setMarkers(newMarkers);
      setStatusMessage(getHint('putMarker', editMode));
    } else {
      setStatusMessage('Здесь уже лежит маркер.');
    }
  };

  /**
   * Поднять маркер
   */
  const pickMarker = () => {
    const posKey = `${robotPos.x},${robotPos.y}`;
    if (markers[posKey]) {
      const newMarkers = { ...markers };
      delete newMarkers[posKey];
      setMarkers(newMarkers);
      setStatusMessage(getHint('pickMarker', editMode));
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
      setStatusMessage(getHint('paintCell', editMode));
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
      setStatusMessage(getHint('clearCell', editMode));
    } else {
      setStatusMessage('Эта клетка и так не была покрашена.');
    }
  };

  /**
   * Включить/выключить режим рисования
   */
  const toggleEditMode = () => {
    const newMode = !editMode;
    setEditMode(newMode);
    if (newMode) {
      // Включили — getHint('enterEditMode')
      setStatusMessage(getHint('enterEditMode', newMode));
    } else {
      // Выключили — getHint('exitEditMode')
      setStatusMessage(getHint('exitEditMode', newMode));
    }
  };

  /**
   * Увеличить ширину поля
   */
  const increaseWidth = () => {
    if (!editMode) {
      setStatusMessage('Включите режим рисования для изменения поля.');
      return;
    }
    setWidth(width + 1);
    setStatusMessage(getHint('increaseWidth', editMode));
  };

  /**
   * Уменьшить ширину поля
   */
  const decreaseWidth = () => {
    if (!editMode) {
      setStatusMessage('Включите режим рисования для изменения поля.');
      return;
    }
    if (width > 1) {
      setWidth(width - 1);
      setStatusMessage(getHint('decreaseWidth', editMode));
    } else {
      setStatusMessage('Ширина не может быть < 1.');
    }
  };

  /**
   * Увеличить высоту поля
   */
  const increaseHeight = () => {
    if (!editMode) {
      setStatusMessage('Включите режим рисования для изменения поля.');
      return;
    }
    setHeight(height + 1);
    setStatusMessage(getHint('increaseHeight', editMode));
  };

  /**
   * Уменьшить высоту поля
   */
  const decreaseHeight = () => {
    if (!editMode) {
      setStatusMessage('Включите режим рисования для изменения поля.');
      return;
    }
    if (height > 1) {
      setHeight(height - 1);
      setStatusMessage(getHint('decreaseHeight', editMode));
    } else {
      setStatusMessage('Высота не может быть < 1.');
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
      setStatusMessage('Обстановка импортирована!');
    } catch (error) {
      setStatusMessage('Ошибка импорта: ' + error.message);
    }
  };

  /**
   * parseAndApplyFieldFile(content): логика чтения .fil
   */
  const parseAndApplyFieldFile = (content) => {
    try {
      setRobotPos({ x: 0, y: 0 });
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
      setRobotPos({ x: rx, y: ry });

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

  return (
    <Card className="card">
      <CardHeader
        title={
          <Typography variant="h6" style={{ textAlign: 'center' }}>
            Управление
          </Typography>
        }
      />
      <CardContent>
        <Grid container spacing={2} alignItems="center" justifyContent="center">

          {/* Кнопки движения (стрелки) */}
          <Grid item xs={4}></Grid>
          <Grid item xs={4}>
            <Button variant="contained" onClick={() => moveRobot('up')}>
              <ChevronUp />
            </Button>
          </Grid>
          <Grid item xs={4}></Grid>

          <Grid item xs={4}>
            <Button variant="contained" onClick={() => moveRobot('left')}>
              <ChevronLeft />
            </Button>
          </Grid>
          <Grid item xs={4}></Grid>
          <Grid item xs={4}>
            <Button variant="contained" onClick={() => moveRobot('right')}>
              <ChevronRight />
            </Button>
          </Grid>

          <Grid item xs={4}></Grid>
          <Grid item xs={4}>
            <Button variant="contained" onClick={() => moveRobot('down')}>
              <ChevronDown />
            </Button>
          </Grid>
          <Grid item xs={4}></Grid>

          {/* Маркеры */}
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

          {/* Покраска */}
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

          {/* Режим рисования */}
          <Grid item xs={12}>
            <Button
              variant="outlined"
              onClick={toggleEditMode}
              fullWidth
            >
              {editMode ? 'Выключить Режим рисования' : 'Включить Режим рисования'}
            </Button>
          </Grid>

          {/* Изменение размеров поля */}
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

          {/* Помощь (заглушка) */}
          <Grid item xs={12}>
            <Button variant="contained" color="secondary" fullWidth>
              Помощь
            </Button>
          </Grid>

          {/* Импорт .fil */}
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
              style={{ display: 'none' }}
              accept=".fil\"
              onChange={handleFileChange}
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}

export default ControlPanel;
