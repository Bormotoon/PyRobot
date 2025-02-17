/**
 * @file UserLog.jsx
 * @description Компонент для отображения лог-сообщений.
 * Подписывается на обновления Logger и рендерит каждую строку с применением соответствующих стилей.
 * Добавлена автопрокрутка вниз после обновления.
 */

import React, {Component, createRef} from 'react';
import logger from '../../Logger';
import './UserLog.css';

class UserLog extends Component {
	constructor(props) {
		super(props);
		this.state = {
			logText: logger.getLog(),
		};
		this.handleLogUpdate = this.handleLogUpdate.bind(this);
		this.logContainer = createRef();
	}

	/**
	 * Обработчик обновления лог-сообщений.
	 * @param {string} newLog - Новое содержимое лога.
	 */
	handleLogUpdate(newLog) {
		this.setState({logText: newLog});
	}

	/**
	 * При монтировании компонента подписываемся на обновления лог-сообщений.
	 */
	componentDidMount() {
		logger.subscribe(this.handleLogUpdate);
		this.scrollToBottom();
	}

	/**
	 * При размонтировании отписываемся от обновлений лог-сообщений.
	 */
	componentWillUnmount() {
		logger.unsubscribe(this.handleLogUpdate);
	}

	/**
	 * После обновления состояния прокручиваем контейнер лог-сообщений вниз.
	 */
	componentDidUpdate(prevProps, prevState) {
		if (prevState.logText !== this.state.logText) {
			this.scrollToBottom();
		}
	}

	/**
	 * Прокручивает контейнер лог-сообщений в самый низ.
	 */
	scrollToBottom() {
		if (this.logContainer.current) {
			this.logContainer.current.scrollTop = this.logContainer.current.scrollHeight;
		}
	}

	/**
	 * Определяет CSS-класс для строки лога по её префиксу.
	 * @param {string} line - Строка лог-сообщения.
	 * @returns {string} CSS-класс.
	 */
	getLogCategoryClass(line) {
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
	}

	/**
	 * Рендерит лог-сообщения с чередованием оттенков для сообщений одного типа.
	 * @returns {JSX.Element} Разметка компонента.
	 */
	render() {
		const lines = this.state.logText ? this.state.logText.split('\n') : [];
		// Объект для отслеживания предыдущей строки для каждой категории
		const lastAlt = {};

		return (<div className="user-log console-card" ref={this.logContainer}>
				{lines.map((line, index) => {
					const category = this.getLogCategoryClass(line) || 'default';
					if (lastAlt[category] === undefined) {
						lastAlt[category] = false;
					} else {
						if (index > 0 && this.getLogCategoryClass(lines[index - 1]) === category) {
							lastAlt[category] = !lastAlt[category];
						} else {
							lastAlt[category] = false;
						}
					}
					const altClass = lastAlt[category] ? 'alt' : '';
					return (<div key={index} className={`log-message ${category} ${altClass}`}>
							{line}
						</div>);
				})}
			</div>);
	}
}

export default UserLog;
