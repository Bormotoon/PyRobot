import React, {useEffect, useRef, useState} from 'react';
import logger from '../../Logger';
import './UserLog.css';

const UserLog = () => {
	// Инициализируем состояние лога как массив строк
	const [logMessages, setLogMessages] = useState(logger.getLog().split('\n'));
	const logContainer = useRef(null);

	useEffect(() => {
		// Функция-обработчик обновления лога
		const handleLogUpdate = (newLog) => {
			setLogMessages(newLog.split('\n'));
		};
		logger.subscribe(handleLogUpdate);
		return () => {
			logger.unsubscribe(handleLogUpdate);
		};
	}, []);

	// Автопрокрутка вниз при изменении лог-сообщений
	useEffect(() => {
		if (logContainer.current) {
			logContainer.current.scrollTop = logContainer.current.scrollHeight;
		}
	}, [logMessages]);

	const getLogCategoryClass = (line) => {
		if (line.startsWith('[Movement]')) return 'log-movement';
		if (line.startsWith('[Event]')) return 'log-event';
		if (line.startsWith('[Command]')) return 'log-command';
		if (line.startsWith('[Measurement]')) return 'log-measurement';
		if (line.startsWith('[Error]')) return 'log-error';
		if (line.startsWith('[Declaration]')) return 'log-declaration';
		if (line.startsWith('[Assignment]')) return 'log-assignment';
		if (line.startsWith('[Output]')) return 'log-output';
		if (line.startsWith('[Input]')) return 'log-input';
		if (line.startsWith('[Control]')) return 'log-control';
		if (line.startsWith('[Conversion]')) return 'log-conversion';
		if (line.startsWith('[Math]')) return 'log-math';
		if (line.startsWith('[String]')) return 'log-string';
		if (line.startsWith('[File]')) return 'log-file';
		if (line.startsWith('[System]')) return 'log-system';
		if (line.startsWith('[Random]')) return 'log-random';
		if (line.startsWith('[Loop]')) return 'log-loop';
		if (line.startsWith('[If]')) return 'log-if';
		if (line.startsWith('[Select]')) return 'log-select';
		if (line.startsWith('[Pause]')) return 'log-pause';
		if (line.startsWith('[Stop]')) return 'log-stop';
		if (line.startsWith('[Exit]')) return 'log-exit';
		if (line.startsWith('[Marker]')) return 'log-marker';
		if (line.startsWith('[Cell]')) return 'log-cell';
		if (line.startsWith('[EditMode]')) return 'log-editmode';
		if (line.startsWith('[Dimension]')) return 'log-dimension';
		if (line.startsWith('[FileImport]')) return 'log-fileimport';
		if (line.startsWith('[Drag]')) return 'log-drag';
		if (line.startsWith('[Wall]')) return 'log-wall';
		if (line.startsWith('[CanvasMarker]')) return 'log-canvasmarker';
		return '';
	};

	// Рендерим строки лога с чередованием стилей для сообщений одной категории
	const renderedMessages = [];
	const lastAlt = {};
	logMessages.forEach((line, index) => {
		const category = getLogCategoryClass(line) || 'default';
		if (lastAlt[category] === undefined) {
			lastAlt[category] = false;
		} else {
			if (index > 0 && getLogCategoryClass(logMessages[index - 1]) === category) {
				lastAlt[category] = !lastAlt[category];
			} else {
				lastAlt[category] = false;
			}
		}
		const altClass = lastAlt[category] ? 'alt' : '';
		renderedMessages.push(
			<div key={index} className={`log-message ${category} ${altClass}`}>
				{line}
			</div>
		);
	});

	return (
		<div className="user-log console-card" ref={logContainer}>
			{renderedMessages}
		</div>
	);
};

export default UserLog;
