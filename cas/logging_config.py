"""
cas/logging_config.py
Configures rotating file + console logging for the CAS simulator.
Log files are written to output/<run_id>/cas.log
"""

import logging
import logging.handlers
import os


def setup_logging(
    run_dir: str,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    max_bytes: int = 10_485_760,   # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure root logger with:
      - Console handler  (level = console_level, concise format)
      - Rotating file handler (level = file_level, verbose format)

    Parameters
    ----------
    run_dir : str
        Directory for this run's output; log file written here.
    console_level : str
        Logging level for stdout (DEBUG / INFO / WARNING / ERROR).
    file_level : str
        Logging level for the log file (usually DEBUG for full trace).
    max_bytes : int
        Max log file size before rotation.
    backup_count : int
        Number of rotated log files to retain.

    Returns
    -------
    logging.Logger
        Configured root logger.
    """
    os.makedirs(run_dir, exist_ok=True)
    log_path = os.path.join(run_dir, "cas.log")

    root = logging.getLogger("cas")
    root.setLevel(logging.DEBUG)  # Root captures everything; handlers filter

    # Avoid adding duplicate handlers if called twice
    if root.handlers:
        root.handlers.clear()

    # ── Console handler ───────────────────────────────────────────────────────
    console = logging.StreamHandler()
    console.setLevel(getattr(logging, console_level.upper(), logging.INFO))
    console.setFormatter(logging.Formatter(
        fmt="%(levelname)-8s %(message)s"
    ))
    root.addHandler(console)

    # ── Rotating file handler ─────────────────────────────────────────────────
    fh = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    fh.setLevel(getattr(logging, file_level.upper(), logging.DEBUG))
    fh.setFormatter(logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    root.addHandler(fh)

    root.info("Logging initialised → %s", log_path)
    return root
