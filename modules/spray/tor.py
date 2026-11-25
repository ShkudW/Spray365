from __future__ import annotations

import random
import time

import requests

from modules.core.output import console

newnym_min_gap = 10  # Tor ignores NEWNYM signals less than 10 seconds apart
newnym_retries = 5
request_retries = 3  # login attempts per credential, for when Tor drops a connection
exit_ip_url = "https://check.torproject.org/api/ip"


def _get_stem():
    try:
        import stem
        import stem.control
    except ImportError:
        console.print_error(
            "Tor support requires the 'stem' package (pip install stem)"
        )
    return stem


def describe_error(error: Exception) -> str:
    text = str(error)
    return text.split("Caused by ", 1)[1] if "Caused by " in text else text


class Tor:
    def __init__(self, proxy: str, control_address: str, countries: list[str]):
        self.proxies: dict[str, str] = {"http": proxy, "https": proxy}
        self._proxy: str = proxy
        self._control_address: str = control_address
        self._countries: list[str] = [country.lower() for country in countries]
        self._exit_ip: str = None
        self._last_newnym: float = None
        self._saved_config: tuple = None

    def prepare(self):
        try:
            with self._get_controller() as controller:
                for attempt in range(1, newnym_retries + 1):
                    if attempt > 1:
                        self._new_circuit(controller)
                    try:
                        self._exit_ip = self._read_exit_ip()
                        break
                    except requests.exceptions.InvalidSchema:
                        console.print_error(
                            "The 'requests' package cannot use SOCKS proxies. Install the 'pysocks' package (pip install pysocks)"
                        )
                    except requests.exceptions.ProxyError as e:
                        console.print_error(
                            "Unable to reach the Tor SOCKS proxy '%s': %s"
                            % (self._proxy, describe_error(e))
                        )
                    except Exception as e:
                        console.print_warning(
                            "Unable to reach Tor through '%s' (%s), requesting another circuit"
                            % (self._proxy, describe_error(e))
                        )
                else:
                    console.print_error(
                        "Unable to reach Tor through '%s' after %d attempts"
                        % (self._proxy, newnym_retries)
                    )
        except Exception as e:
            console.print_error(
                "Unable to connect to the Tor control service '%s': %s"
                % (self._control_address, e)
            )

        if self._countries:
            try:
                with self._get_controller() as controller:
                    self._saved_config = (
                        controller.get_conf("ExitNodes", None, multiple=True),
                        controller.get_conf("StrictNodes", None),
                    )
                    controller.set_conf("StrictNodes", "1")
            except Exception as e:
                console.print_error("Unable to set the Tor exit countries: %s" % e)

        console.print_info("Tor is reachable, current exit IP is %s" % self._exit_ip)

    def new_exit(self) -> str:
        country = None
        problem = None
        try:
            with self._get_controller() as controller:
                for attempt in range(1, newnym_retries + 1):
                    country = (
                        random.choice(self._countries) if self._countries else None
                    )
                    if country:
                        controller.set_conf("ExitNodes", "{%s}" % country)

                    self._new_circuit(controller)

                    try:
                        exit_ip = self._read_exit_ip()
                    except Exception as e:
                        exit_ip = None
                        console.print_warning(
                            "Unable to read the Tor exit IP (%s), requesting another circuit"
                            % describe_error(e)
                        )

                    if exit_ip and exit_ip != self._exit_ip:
                        self._exit_ip = exit_ip
                        if country:
                            console.print_info(
                                "Using Tor exit IP %s via %s"
                                % (exit_ip, country.upper())
                            )
                        else:
                            console.print_info("Using Tor exit IP %s" % exit_ip)
                        return exit_ip

                    problem = (
                        "Tor is still exiting through %s" % exit_ip
                        if exit_ip
                        else "Unable to read the Tor exit IP"
                    )
                    if exit_ip and attempt < newnym_retries:
                        console.print_warning(
                            "%s, requesting another circuit" % problem
                        )
        except Exception as e:
            console.print_error(
                "Unable to talk to the Tor control service '%s': %s"
                % (self._control_address, e)
            )

        if country:
            console.print_warning(
                "%s may have only a few or no exit relays" % country.upper()
            )
        console.print_error(
            "%s after %d attempts, aborting password spray" % (problem, newnym_retries)
        )

    def restore_config(self):
        if self._saved_config is None:
            return
        exit_nodes, strict_nodes = self._saved_config
        self._saved_config = None
        try:
            with self._get_controller() as controller:
                if exit_nodes:
                    controller.set_conf("ExitNodes", ",".join(exit_nodes))
                else:
                    controller.reset_conf("ExitNodes")
                if strict_nodes is None:
                    controller.reset_conf("StrictNodes")
                else:
                    controller.set_conf("StrictNodes", strict_nodes)
        except Exception as e:
            console.print_warning("Unable to restore the Tor exit settings: %s" % e)

    def _get_controller(self):
        address, port = self._control_address.rsplit(":", 1)
        controller = _get_stem().control.Controller.from_port(address, int(port))
        try:
            controller.authenticate()
        except Exception:
            controller.close()
            raise
        return controller

    def _new_circuit(self, controller):
        if (
            self._last_newnym is not None
            and time.monotonic() - self._last_newnym < newnym_min_gap
        ):
            time.sleep(newnym_min_gap - (time.monotonic() - self._last_newnym))
        controller.signal(_get_stem().Signal.NEWNYM)
        self._last_newnym = time.monotonic()
        time.sleep(5)

    def _read_exit_ip(self) -> str:
        return requests.get(exit_ip_url, proxies=self.proxies, timeout=30).json()["IP"]
