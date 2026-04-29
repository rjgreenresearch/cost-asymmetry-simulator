"""
cas/config.py
Loads and validates YAML configuration files for weapon systems,
threat systems, and simulation parameters.
"""

import os
import logging
import yaml

log = logging.getLogger("cas.config")

# Default config directory relative to this file's package root
_DEFAULT_CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config"
)


def _load_yaml(path: str) -> dict:
    """
    Load and return a YAML file as a dict.

    Raises
    ------
    FileNotFoundError  - file does not exist
    ValueError         - file is empty or not valid YAML
    PermissionError    - process lacks read access
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Config file not found: {path}\n"
            f"  Tip: run from the project root, or pass an explicit --weapon-config path."
        )
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ValueError(
            f"YAML parse error in {path}: {exc}\n"
            f"  Tip: validate at yaml.org/start.html"
        ) from exc
    if data is None:
        raise ValueError(f"Config file is empty: {path}")
    log.debug("Loaded config: %s", path)
    return data


def load_weapon_systems(path: str | None = None) -> dict:
    """
    Load weapon_systems.yaml.
    Returns dict keyed by system ID (e.g. 'THAAD', 'LUCAS').
    """
    path = path or os.path.join(_DEFAULT_CONFIG_DIR, "weapon_systems.yaml")
    raw = _load_yaml(path)
    systems = raw.get("systems", {})
    log.info("Loaded %d weapon systems from %s", len(systems), path)
    return systems


def load_threat_systems(path: str | None = None) -> dict:
    """Load threat_systems.yaml. Returns dict keyed by threat ID."""
    path = path or os.path.join(_DEFAULT_CONFIG_DIR, "threat_systems.yaml")
    raw = _load_yaml(path)
    threats = raw.get("threats", {})
    log.info("Loaded %d threat systems from %s", len(threats), path)
    return threats


def load_simulation_params(path: str | None = None) -> dict:
    """Load simulation.yaml and return the full parameter dict."""
    path = path or os.path.join(_DEFAULT_CONFIG_DIR, "simulation.yaml")
    params = _load_yaml(path)
    log.info("Loaded simulation params from %s", path)
    return params


class Config:
    """
    Unified configuration object that bundles all three YAML files
    and exposes convenience accessors used throughout the simulator.

    Usage
    -----
    cfg = Config()                              # loads all defaults
    cfg = Config(weapon_systems_path="my.yaml") # override one file
    """

    def __init__(
        self,
        weapon_systems_path: str | None = None,
        threat_systems_path: str | None = None,
        simulation_path: str | None = None,
    ):
        self.weapons  = load_weapon_systems(weapon_systems_path)
        self.threats  = load_threat_systems(threat_systems_path)
        self._sim     = load_simulation_params(simulation_path)

        # Convenience accessors
        self.n_sims              = self._sim["simulation"]["n_simulations"]
        self.random_seed         = self._sim["simulation"].get("random_seed")
        self.theater_correlation = self._sim["simulation"]["theater_correlation"]
        self.horizons            = self._sim["horizons"]
        self.targets             = self._sim["targets"]
        self.portfolio_caps      = self._sim["targets"].get("portfolio_caps", {})
        self.scenarios           = self._sim.get("scenarios", {})
        self.output_cfg          = self._sim.get("output", {})
        self.logging_cfg         = self._sim.get("logging", {})

    # ── Helpers ───────────────────────────────────────────────────────────────

    def weapon(self, key: str) -> dict:
        """Return single weapon system config; raises KeyError if not found."""
        if key not in self.weapons:
            raise KeyError(f"Unknown weapon system: '{key}'. "
                           f"Available: {sorted(self.weapons)}")
        return self.weapons[key]

    def threat(self, key: str) -> dict:
        """Return single threat system config."""
        if key not in self.threats:
            raise KeyError(f"Unknown threat: '{key}'. "
                           f"Available: {sorted(self.threats)}")
        return self.threats[key]

    def horizon(self, name: str = "long") -> int:
        """Return a named horizon in days (short/medium/long/extended)."""
        return self.horizons.get(name, 90)

    def tier_cap(self, tier: str) -> float:
        """Return the max budget fraction for a tier. 1.0 = no cap."""
        return float(self.portfolio_caps.get(tier, 1.0))

    def consumable_systems(self) -> dict:
        """Return only weapon systems that have consumption_rates defined."""
        return {k: v for k, v in self.weapons.items()
                if "consumption_rates" in v
                and v["consumption_rates"]["theater_1"]["mean"] > 0}

    def summary(self) -> str:
        """Return a one-line config summary for logging."""
        return (f"{len(self.weapons)} weapons | {len(self.threats)} threats | "
                f"n_sims={self.n_sims} | seed={self.random_seed}")
