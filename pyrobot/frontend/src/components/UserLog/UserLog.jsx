/**
 * @file UserLog.jsx
 * @description Компонент для отображения лог-сообщений.
 * Подписывается на обновления Logger и рендерит каждую строку с применением соответствующих стилей.
 * Добавлена автопрокрутка вниз после обновления. Отображает шаги выполнения и ошибки.
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

	handleLogUpdate(newLog) {
		this.setState({logText: newLog});
	}

	componentDidMount() {
		logger.subscribe(this.handleLogUpdate);
		this.scrollToBottom();
	}

	componentWillUnmount() {
		logger.unsubscribe(this.handleLogUpdate);
	}

	componentDidUpdate(prevProps, prevState) {
		if (prevState.logText !== this.state.logText || prevProps.steps !== this.props.steps || prevProps.error !== this.props.error) {
			this.scrollToBottom();
		}
	}

	scrollToBottom() {
		if (this.logContainer.current) {
			this.logContainer.current.scrollTop = this.logContainer.current.scrollHeight;
		}
	}

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
		if (line.startsWith('[Step]')) return 'log-step';
		return '';
	}

	render() {
		const {steps = [], error = ''} = this.props; // Добавляем пропс error
		const lines = this.state.logText ? this.state.logText.split('\n') : [];
		const lastAlt = {};

		const stepLines = steps.map((step, index) =>
			`[Step] Шаг ${index + 1}: Робот на (${step.robot.x}, ${step.robot.y}), закрашенные клетки: ${step.coloredCells.length > 0 ? step.coloredCells.join(', ') : 'нет'}`
		);

		const finalLines = [...lines, ...stepLines];
		if (error) {
			finalLines.push(`[Error] ${error}`);
			finalLines.push('[Error] Выполнение прервано из-за ошибки.');
		} else if (steps.length > 0 && steps[steps.length - 1].robot.x === steps[0].robot.x && steps[steps.length - 1].robot.y === steps[0].robot.y && steps.length > 1) {
			// Если робот не сдвинулся, но шаги есть, это ошибка
			finalLines.push('[Error] Робот не смог двигаться из-за стен.');
			finalLines.push('[Error] Выполнение прервано из-за ошибки.');
		} else if (steps.length > 0) {
			finalLines.push('[Event] Код выполнен успешно.');
		}

		return (
			<div className="user-log console-card" ref={this.logContainer}>
				{finalLines.map((line, index) => {
					const category = this.getLogCategoryClass(line) || 'default';
					if (lastAlt[category] === undefined) {
						lastAlt[category] = false;
					} else {
						if (index > 0 && this.getLogCategoryClass(finalLines[index - 1]) === category) {
							lastAlt[category] = !lastAlt[category];
						} else {
							lastAlt[category] = false;
						}
					}
					const altClass = lastAlt[category] ? 'alt' : '';
					return (
						<div key={index} className={`log-message ${category} ${altClass}`}>
							{line}
						</div>
					);
				})}
			</div>
		);
	}
}

export default UserLog;