from __future__ import annotations
import logging
from pathlib import Path
from typing_extensions import Literal
import datetime


def create_logger(
    log_path: Path | str = None,
    level: Literal['INFO', 'DEBUG', 'WARNING', 'ERROR'] = 'INFO',
    stack_depth: int = 2,
) -> logging.Logger:
    """生成logger

    Args:
        log_path (Path | str, optional): 日志保存路径. Defaults to None.
        level (Literal[INFO, DEBUG, WARNING, ERROR], optional): 日志输出级别. Defaults to 'DEBUG'.
        stack_depth (int, optional): 栈深度. Defaults to 2.

    Returns:
        (logging.Logger): logger对象
    """
    if log_path is None:
        try:
            is_ipython = __import__("IPython").get_ipython()
        except:
            is_ipython = False

        if is_ipython:
            folder = Path.cwd()
        else:
            import inspect, re
            stack = inspect.stack()
            folder = Path(stack[stack_depth].filename).resolve().parent
            while True:
                if re.findall(r'src|utils?|logs?|logging', folder.name,
                              re.IGNORECASE):
                    folder = folder.parent
                else:
                    break
        log_path = folder / f"log/larkpy_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    logger = logging.getLogger()
    logger.setLevel(level)
    # logger.setLevel('WARNING')
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s-%(levelname)s %(message)s")

    stream_handler = logging.StreamHandler()  # 输出到控制台的handler
    stream_handler.setFormatter(formatter)
    # stream_handler.setLevel('WARNING')  # 也可以不设置，不设置就默认用logger的level

    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8", mode="a")
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger
