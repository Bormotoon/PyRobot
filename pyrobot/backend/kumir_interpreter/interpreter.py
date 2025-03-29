import logging
import re
# from .robot_state import SimulatedRobot, RobotError # Imported below
from .execution import execute_lines, KumirExecutionError  # Import execution logic
from .preprocessing import preprocess_code, separate_sections, parse_algorithm_header  # Import preprocessing
# from .declarations import ALLOWED_TYPES # Not directly used here
# from .identifiers import is_valid_identifier # Not directly used here
from .safe_eval import safe_eval, get_eval_env, KumirEvalError  # Import safe evaluation
from .robot_state import RobotError, SimulatedRobot  # Ensure Robot imports are here

# Constants
MAX_INT = 2147483647
МАКСЦЕЛ = MAX_INT

logger = logging.getLogger('KumirInterpreter')


class KumirLanguageInterpreter:
    """
    Интерпретатор языка КУМИР с поддержкой пошагового исполнения.
    """

    def __init__(self, code, initial_field_state=None):
        """ Инициализирует интерпретатор. """
        self.code = code
        self.env = {}
        self.algorithms = {}
        self.main_algorithm = None
        self.introduction = []
        self.output = ""
        self.logger = logger
        default_state = {'width': 7, 'height': 7, 'robotPos': {'x': 0, 'y': 0},
                         'walls': set(), 'markers': {}, 'coloredCells': set(), 'symbols': {}}  # Added symbols default
        current_state = initial_field_state if initial_field_state else default_state
        self.width = current_state.get('width', default_state['width'])
        self.height = current_state.get('height', default_state['height'])
        if not isinstance(self.width, int) or self.width < 1: self.logger.warning(
            f"Invalid W({self.width})"); self.width = default_state['width']
        if not isinstance(self.height, int) or self.height < 1: self.logger.warning(
            f"Invalid H({self.height})"); self.height = default_state['height']
        self.robot = SimulatedRobot(
            width=self.width, height=self.height,
            initial_pos=current_state.get('robotPos', default_state['robotPos']),
            initial_walls=set(current_state.get('walls', default_state['walls'])),
            initial_markers=current_state.get('markers', default_state['markers']),
            initial_colored_cells=set(current_state.get('coloredCells', default_state['coloredCells'])),
            initial_symbols=current_state.get('symbols', default_state['symbols'])  # Pass symbols
        )
        self.logger.info(f"Interpreter init: {self.width}x{self.height}, Robot@ {self.robot.robot_pos}")

    def get_state(self):
        """ Возвращает текущее состояние (копия). """
        # === Include symbols state ===
        return {
            "env": self.env.copy(),
            "robot": self.robot.robot_pos.copy(),
            "coloredCells": list(self.robot.colored_cells),
            "symbols": self.robot.symbols.copy()  # <-- Get copy of symbols
        }

    # ============================

    def parse(self):
        """ Парсит код во вступление и алгоритмы. """
        self.logger.info("Parsing code...")
        try:
            lines = preprocess_code(self.code)
            self.introduction, algo_sections = separate_sections(lines)
            if not algo_sections: raise KumirExecutionError("В программе не найдены алгоритмы ('алг').")
            self.main_algorithm = algo_sections[0]
            self.main_algorithm["header_info"] = parse_algorithm_header(self.main_algorithm["header"])
            self.logger.debug(f"Parsed main alg: {self.main_algorithm['header_info']}")
            for alg in algo_sections[1:]:
                info = parse_algorithm_header(alg["header"])
                alg["header_info"] = info
                if info["name"]:
                    if info["name"] in self.algorithms: self.logger.warning(f"Algo '{info['name']}' redefined.")
                    self.algorithms[info["name"]] = alg;
                    self.logger.debug(f"Parsed aux alg '{info['name']}'")
                else:
                    self.logger.warning(f"Unnamed alg after first: {info['raw']}")
            self.logger.info("Code parsing completed.")
        except Exception as e:
            self.logger.error(f"Parsing failed: {e}", exc_info=True); raise KumirExecutionError(f"Ошибка разбора: {e}")

    def _execute_block(self, lines, phase_name, trace, progress_callback=None):
        """ Выполняет блок кода (вступление/тело), генерирует trace и вызывает callback. """
        for idx, line in enumerate(lines):
            line = line.strip()  # Ensure line is stripped before processing/logging
            if not line: continue
            state_before = self.get_state();
            output_before = self.output
            # Event before (optional if trace size is a concern)
            # trace.append({ "phase": phase_name, "commandIndex": idx, "command": line, "stateBefore": state_before, "outputBefore": output_before })
            try:
                # Pass self as interpreter context
                # execute_lines processes one line at a time if given a list of one
                execute_lines([line], self.env, self.robot, self)  # Pass self.robot
            except (RobotError, KumirEvalError, KumirExecutionError, Exception) as e:
                error_msg = f"Ошибка: {str(e)}"  # User-friendly message
                self.logger.error(f"{error_msg} в строке {idx + 1}: '{line}'", exc_info=False)  # Log simply
                self.output += f"{error_msg} (строка {idx + 1})\n"  # Append error to output buffer
                state_after_error = self.get_state();
                output_after_error = self.output
                trace.append({"phase": phase_name, "commandIndex": idx, "command": line, "error": str(e),
                              "stateAfter": state_after_error, "outputAfter": output_after_error})
                if progress_callback: progress_callback(
                    {"phase": phase_name, "commandIndex": idx, "output": self.output,
                     "robotPos": state_after_error["robot"], "error": str(e)})
                return {"success": False, "error": str(e), "errorIndex": idx}  # Stop block execution

            state_after = self.get_state();
            output_after = self.output
            trace.append({"phase": phase_name, "commandIndex": idx, "command": line, "stateAfter": state_after,
                          "outputAfter": output_after})
            if progress_callback: progress_callback(
                {"phase": phase_name, "commandIndex": idx, "output": self.output, "robotPos": state_after["robot"]})
        return {"success": True}  # Block completed

    def interpret(self, progress_callback=None):
        """ Полный цикл: парсинг и выполнение. """
        trace = []
        try:
            self.parse()
            self.logger.info("Executing introduction...")
            intro_result = self._execute_block(self.introduction, "introduction", trace, progress_callback)
            if not intro_result["success"]:
                self.logger.error("Error in introduction.")
                final_state = self.get_state();
                final_state["output"] = self.output
                return {"trace": trace, "finalState": final_state, "success": False,
                        "message": intro_result.get("error"), "errorIndex": intro_result.get("errorIndex")}

            self.logger.info("Executing main algorithm...")
            if not self.main_algorithm: raise KumirExecutionError("Основной алгоритм не найден.")
            algo_result = self._execute_block(self.main_algorithm["body"], "main", trace, progress_callback)
            final_state = self.get_state();
            final_state["output"] = self.output

            if not algo_result["success"]:
                self.logger.error("Error in main algorithm.")
                return {"trace": trace, "finalState": final_state, "success": False,
                        "message": algo_result.get("error"), "errorIndex": algo_result.get("errorIndex")}

            self.logger.info("Interpretation successful.")
            return {"trace": trace, "finalState": final_state, "success": True}
        except (RobotError, KumirEvalError, KumirExecutionError, Exception) as e:
            error_msg = f"Крит. ошибка: {str(e)}"
            self.logger.error(error_msg, exc_info=True);
            self.output += f"{error_msg}\n"
            try:
                state_on_error = self.get_state()
            except:
                state_on_error = {"env": self.env, "robot": None, "coloredCells": [], "symbols": {}}  # Fallback
            state_on_error["output"] = self.output
            return {"trace": trace, "finalState": state_on_error, "success": False, "message": error_msg}