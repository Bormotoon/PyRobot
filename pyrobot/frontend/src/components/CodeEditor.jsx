/**
 * CodeEditor.jsx
 *
 * В этом файле находится компонент для редактирования кода (CodeEditor).
 * При переходе на useReducer в RobotSimulator ничего не меняется в CodeEditor,
 * поскольку он лишь получает code и isRunning через пропы, а также вызывает
 * колбэки (onClearCode, onStop, onStart, onReset), которые внутри RobotSimulator
 * диспатчат действия в редюсер. Здесь мы просто дополнили код докстрингами на русском языке,
 * но сама логика не изменилась.
 */

import React from 'react';
import { Button, Typography } from '@mui/material';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';

/**
 * Подсветка синтаксиса языка КУМИР для Prism.
 */
Prism.languages.kumir = {
  'keyword': /\b(использовать|Робот|алг|нач|кон|влево|вправо|вверх|вниз|закрасить|если|иначе|для|пока|температура|радиация)\b/g,
  'comment': /#.*/g,
  'string': /".*?"/g,
  'number': /\b\d+\b/g,
  'operator': /\b(==|!=|<=|>=|<|>|\+|\-|\*|\/)\b/g,
};

/**
 * Компонент CodeEditor:
 * - Показывает поле для редактирования кода, с подсветкой (react-simple-code-editor + Prism).
 * - Кнопки: Очистить, Стоп, Пуск, Сброс — которые вызывают переданные колбэки.
 * - Не выводит никаких statusMessage (подсказок), т. к. вся логика находится в Field.
 * @param {Object} props - объект пропсов
 * @param {string} props.code - текущий текст программы
 * @param {function} props.setCode - колбэк для изменения текста кода
 * @param {boolean} props.isRunning - флаг, идёт ли сейчас исполнение
 * @param {function} props.onClearCode - колбэк, который очищает код
 * @param {function} props.onStop - колбэк, который останавливает выполнение
 * @param {function} props.onStart - колбэк, который запускает выполнение
 * @param {function} props.onReset - колбэк, который сбрасывает симулятор
 */
function CodeEditor({
  code,
  setCode,
  isRunning,
  onClearCode,
  onStop,
  onStart,
  onReset
}) {
  /**
   * Функция highlightCode(inputCode)
   * Использует Prism для подсветки синтаксиса КУМИР.
   * @param {string} inputCode - исходный код
   * @returns {string} строка HTML, содержащая подсвеченный код
   */
  const highlightCode = (inputCode) => {
    return Prism.highlight(inputCode, Prism.languages.kumir, 'kumir');
  };

  return (
    <div className="card code-editor">
      <Typography variant="h5" gutterBottom style={{ color: '#fff' }}>
        Редактор Кода
      </Typography>

      <Editor
        value={code}
        onValueChange={(newCode) => setCode(newCode)}
        highlight={highlightCode}
        padding={10}
        className="react-simple-code-editor"
        style={{
          fontFamily: '"Fira Code", monospace',
          fontSize: 14,
          flex: '1 1 auto',
          overflow: 'auto',
        }}
      />

      <div className="editor-controls">
        <Button
          variant="contained"
          color="secondary"
          onClick={onClearCode}
          fullWidth
        >
          Очистить
        </Button>

        <Button
          variant="contained"
          color="error"
          onClick={onStop}
          disabled={!isRunning}
          fullWidth
        >
          Стоп
        </Button>

        <Button
          variant="contained"
          color="success"
          onClick={onStart}
          disabled={isRunning}
          fullWidth
        >
          Пуск
        </Button>

        <Button
          variant="outlined"
          color="primary"
          onClick={onReset}
          fullWidth
        >
          Сбросить симулятор
        </Button>
      </div>
    </div>
  );
}

export default CodeEditor;
