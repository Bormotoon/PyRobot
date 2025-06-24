/**
 * @file Logger.js
 * @description Синглтон для централизованного логирования в симуляторе робота.
 * Предоставляет методы для записи лог-сообщений и механизм подписки, позволяющий компонентам обновлять отображение.
 */

class Logger {
	constructor() {
		// Массив, содержащий все лог-сообщения.
		this.entries = [];
		// Массив подписчиков, которым будут переданы обновления лога.
		this.subscribers = [];
	}

	/**
	 * Подписывает callback на обновления лог-сообщений.
	 * Если такой callback уже зарегистрирован, он не добавляется повторно.
	 * @param {function(string): void} callback - Функция, вызываемая при обновлении лога.
	 */
	subscribe(callback) {
		if (!this.subscribers.includes(callback)) {
			this.subscribers.push(callback);
		}
	}

	/**
	 * Отписывает callback от обновлений лог-сообщений.
	 * @param {function(string): void} callback - Функция для удаления из списка подписчиков.
	 */
	unsubscribe(callback) {
		this.subscribers = this.subscribers.filter(cb => cb !== callback);
	}

	/**
	 * Уведомляет всех подписчиков об изменении лога.
	 * @private
	 */
	_notify() {
		const logText = this.getLog();
		this.subscribers.forEach(cb => cb(logText));
	}

	/**
	 * Записывает произвольное сообщение в лог.
	 * Если последнее сообщение уже совпадает с новым, запись не производится.
	 * @param {string} message - Сообщение для записи.
	 */
	log(message) {
		// Если последнее сообщение такое же, не добавляем его повторно
		if (this.entries.length > 0 && this.entries[this.entries.length - 1] === message) {
			return;
		}
		this.entries.push(message);
		this._notify();
	}

	// Методы логирования с соответствующими префиксами:
	log_movement(message) {
		this.log(`[Movement] ${message}`);
	}

	log_event(message) {
		this.log(`[Event] ${message}`);
	}

	log_command(command) {
		this.log(`[Command] Выполнена команда: ${command}.`);
	}

	log_measurement(measurement, value) {
		this.log(`[Measurement] Измерение '${measurement}': ${value}.`);
	}

	log_error(error_message) {
		this.log(`[Error] ${error_message}.`);
	}

	log_declaration(variable_name, var_type, is_table = false) {
		const tableStr = is_table ? " (таблица)" : "";
		this.log(`[Declaration] Объявлена переменная: '${variable_name}' типа '${var_type}'${tableStr}.`);
	}

	log_assignment(variable_name, value) {
		this.log(`[Assignment] Присвоено переменной '${variable_name}' значение: ${value}.`);
	}

	log_output(content) {
		this.log(`[Output] Вывод: ${content}.`);
	}

	log_input(prompt, received_input) {
		this.log(`[Input] Запрос: '${prompt}'. Получено: ${received_input}.`);
	}

	log_control(control_command, condition_expr, result) {
		this.log(`[Control] Команда '${control_command}' с условием '${condition_expr}' выполнена. Результат: ${result}.`);
	}

	log_conversion(function_name, input_value, result_value) {
		this.log(`[Conversion] Функция '${function_name}' вызвана с входным значением '${input_value}'. Результат: ${result_value}.`);
	}

	log_math_function(function_name, input_value, result_value) {
		this.log(`[Math] Функция '${function_name}' вызвана с аргументом ${input_value}. Результат: ${result_value}.`);
	}

	log_string_function(function_name, input_value, result_value) {
		this.log(`[String] Функция '${function_name}' вызвана с аргументом '${input_value}'. Результат: '${result_value}'.`);
	}

	log_file_operation(operation, filename, result) {
		this.log(`[File] Операция '${operation}' для файла '${filename}' выполнена. Результат: ${result}.`);
	}

	log_system_function(function_name, input_value, result_value) {
		this.log(`[System] Функция '${function_name}' вызвана с аргументом ${input_value}. Результат: ${result_value}.`);
	}

	log_random_event(function_name, input_range, result_value) {
		this.log(`[Random] Функция '${function_name}' вызвана с диапазоном ${input_range}. Результат: ${result_value}.`);
	}

	log_loop_enter(loop_type, parameters = "") {
		this.log(`[Loop] Вход в цикл '${loop_type}' ${parameters}.`);
	}

	log_loop_iteration(iteration, loop_type) {
		this.log(`[Loop] Итерация ${iteration} цикла '${loop_type}'.`);
	}

	log_loop_exit(loop_type) {
		this.log(`[Loop] Выход из цикла '${loop_type}'.`);
	}

	log_if_enter(condition_expr) {
		this.log(`[If] Вход в условный оператор с условием: ${condition_expr}.`);
	}

	log_if_result(condition_expr, result, branch = "then") {
		this.log(`[If] Условие '${condition_expr}' оценено как ${result}. Ветка '${branch}' выполнена.`);
	}

	log_if_exit() {
		this.log("[If] Выход из условного оператора.");
	}

	log_select_enter() {
		this.log("[Select] Вход в оператор выбора.");
	}

	log_select_branch(condition_expr, result, branch = "при") {
		this.log(`[Select] Условие '${condition_expr}' оценено как ${result}. Ветка '${branch}' выполнена.`);
	}

	log_select_exit() {
		this.log("[Select] Выход из оператора выбора.");
	}

	log_pause() {
		this.log("[Pause] Ожидание продолжения...");
	}

	log_stop() {
		this.log("[Stop] Прерывание выполнения программы.");
	}

	log_exit_command() {
		this.log("[Exit] Выход из цикла/алгоритма.");
	}

	log_marker_added(position) {
		this.log(`[Marker] Маркер добавлен в позицию: ${position}.`);
	}

	log_marker_removed(position) {
		this.log(`[Marker] Маркер удалён из позиции: ${position}.`);
	}

	log_cell_painted(position) {
		this.log(`[Cell] Клетка ${position} закрашена.`);
	}

	log_cell_cleared(position) {
		this.log(`[Cell] Клетка ${position} очищена.`);
	}

	log_edit_mode_change(new_mode) {
		const modeStr = new_mode ? "включён" : "выключен";
		this.log(`[EditMode] Режим редактирования поля ${modeStr}.`);
	}

	log_dimension_change(dimension, old_value, new_value) {
		this.log(`[Dimension] ${dimension} изменена: ${old_value} -> ${new_value}.`);
	}

	log_file_import_success(filename) {
		this.log(`[FileImport] Импорт поля из файла '${filename}' выполнен успешно.`);
	}

	log_file_import_error(filename, error_message) {
		this.log(`[FileImport] Ошибка импорта файла '${filename}': ${error_message}.`);
	}

	log_robot_drag_start() {
		this.log("[Drag] Начало перетаскивания робота.");
	}

	log_robot_drag_update(new_position) {
		this.log(`[Drag] Обновление перетаскивания робота. Новая позиция: (${new_position.x}, ${new_position.y}).`);
	}

	log_robot_drag_end(final_position) {
		this.log(`[Drag] Перетаскивание робота завершено. Итоговая позиция: (${final_position.x}, ${final_position.y}).`);
	}

	log_wall_added(wall_description) {
		this.log(`[Wall] Стена добавлена: ${wall_description}.`);
	}

	log_wall_removed(wall_description) {
		this.log(`[Wall] Стена удалена: ${wall_description}.`);
	}

	log_canvas_marker_added(position) {
		this.log(`[CanvasMarker] Маркер добавлен через правый клик в позицию: ${position}.`);
	}

	log_canvas_marker_removed(position) {
		this.log(`[CanvasMarker] Маркер удалён через правый клик из позиции: ${position}.`);
	}

	/**
	 * Возвращает полный лог в виде одной строки, где строки разделены символом перевода строки.
	 * @returns {string} Строка лог-сообщений.
	 */
	getLog() {
		return this.entries.join('\n');
	}

	/**
	 * Очищает все записи в логе и уведомляет подписчиков об изменении.
	 */
	clearLog() {
		this.entries = [];
		this._notify();
	}
}

const logger = new Logger();
export default logger;
