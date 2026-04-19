import time
import random
import asyncio
from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class SerialConfig:
    port: str = "COM1"
    baudrate: int = 9600
    bytesize: int = 8
    parity: str = "N"
    stopbits: int = 1
    timeout: float = 1.0


@dataclass
class WeightData:
    weight: float
    is_stable: bool
    timestamp: float


class WeightSimulator:
    def __init__(self, config: Optional[SerialConfig] = None):
        self.config = config or SerialConfig()
        self._is_running = False
        self._is_stable = False
        self._current_weight = 0.0
        self._target_weight = 0.0
        self._callbacks = []

    def add_callback(self, callback: Callable[[WeightData], None]):
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[WeightData], None]):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_callbacks(self, data: WeightData):
        for callback in self._callbacks:
            callback(data)

    def start_weighing(self, target_weight: float = 1234.56):
        self._is_running = True
        self._is_stable = False
        self._target_weight = target_weight
        self._current_weight = 0.0

    def stop_weighing(self):
        self._is_running = False
        self._is_stable = False

    def is_running(self) -> bool:
        return self._is_running

    def is_stable(self) -> bool:
        return self._is_stable

    def get_current_weight(self) -> float:
        return self._current_weight

    async def simulate_weighing_process(self):
        if not self._is_running:
            return

        start_time = time.time()
        stabilization_duration = 3.0
        elapsed = 0.0

        initial_variation = self._target_weight * 0.1

        while elapsed < stabilization_duration and self._is_running:
            progress = elapsed / stabilization_duration

            variation_scale = 1.0 - (progress * 0.95)
            current_variation = initial_variation * variation_scale

            base_weight = self._target_weight * (0.5 + progress * 0.5)

            noise = random.uniform(-current_variation, current_variation)
            self._current_weight = base_weight + noise
            self._current_weight = max(0, self._current_weight)

            data = WeightData(
                weight=self._current_weight,
                is_stable=False,
                timestamp=time.time()
            )
            self._notify_callbacks(data)

            update_interval = 0.05 + (progress * 0.2)
            await asyncio.sleep(update_interval)
            elapsed = time.time() - start_time

        if self._is_running:
            self._current_weight = self._target_weight
            self._is_stable = True

            data = WeightData(
                weight=self._current_weight,
                is_stable=True,
                timestamp=time.time()
            )
            self._notify_callbacks(data)

            self._is_running = False


class SerialPortSimulator:
    def __init__(self, config: Optional[SerialConfig] = None):
        self.config = config or SerialConfig()
        self._is_open = False
        self._weight_simulator = WeightSimulator(config)

    @property
    def weight_simulator(self) -> WeightSimulator:
        return self._weight_simulator

    def open(self):
        self._is_open = True

    def close(self):
        self._is_open = False

    def is_open(self) -> bool:
        return self._is_open

    def read_weight(self) -> Optional[float]:
        if not self._is_open:
            return None
        return self._weight_simulator.get_current_weight()

    def start_weighing(self, target_weight: float = 1234.56):
        self._weight_simulator.start_weighing(target_weight)

    def stop_weighing(self):
        self._weight_simulator.stop_weighing()

    def is_stable(self) -> bool:
        return self._weight_simulator.is_stable()
