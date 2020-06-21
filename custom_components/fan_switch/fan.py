"""Fan support for switch entities."""

import logging
from typing import Callable, Optional, Sequence, cast

import voluptuous as vol

from homeassistant.components import switch
from homeassistant.components.fan import PLATFORM_SCHEMA, FanEntity, SPEED_OFF
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_ENTITY_ID,
    CONF_NAME,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.core import CALLBACK_TYPE, State, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

# mypy: allow-untyped-calls, allow-untyped-defs, no-check-untyped-defs

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Fan Switch"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_ENTITY_ID): cv.entity_domain(switch.DOMAIN),
    }
)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable[[Sequence[Entity], bool], None],
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Initialize Fan Switch platform."""
    async_add_entities(
        [FanSwitch(cast(str, config.get(CONF_NAME)), config[CONF_ENTITY_ID])], True
    )

class FanSwitch(FanEntity):
    """Represents a Switch as a Fan."""

    def __init__(self, name: str, switch_entity_id: str) -> None:
        """Initialize Fan Switch."""
        self._name = name
        self._switch_entity_id = switch_entity_id
        self._is_on = False
        self._available = False
        self._async_unsub_state_changed: Optional[CALLBACK_TYPE] = None

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return true if fan switch is on."""
        return self._is_on

    @property
    def available(self) -> bool:
        """Return true if fan switch is on."""
        return self._available

    @property
    def should_poll(self) -> bool:
        """No polling needed for a fan switch."""
        return False

    async def async_turn_on(self, speed: Optional[str] = None, **kwargs):
        """Forward the turn_on command to the switch in this fan switch."""
        data = {ATTR_ENTITY_ID: self._switch_entity_id}

        if speed is SPEED_OFF:
            await self.async_turn_off()
        else:        
            await self.hass.services.async_call(
                switch.DOMAIN, switch.SERVICE_TURN_ON, data, blocking=True
            )

    async def async_turn_off(self, **kwargs):
        """Forward the turn_off command to the switch in this fan switch."""
        data = {ATTR_ENTITY_ID: self._switch_entity_id}
        await self.hass.services.async_call(
            switch.DOMAIN, switch.SERVICE_TURN_OFF, data, blocking=True
        )

    async def async_update(self):
        """Query the switch in this fan switch and determine the state."""
        switch_state = self.hass.states.get(self._switch_entity_id)

        if switch_state is None:
            self._available = False
            return

        self._is_on = switch_state.state == STATE_ON
        self._available = switch_state.state != STATE_UNAVAILABLE

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def async_state_changed_listener(
            entity_id: str, old_state: State, new_state: State
        ) -> None:
            """Handle child updates."""
            self.async_schedule_update_ha_state(True)

        assert self.hass is not None
        self._async_unsub_state_changed = async_track_state_change(
            self.hass, self._switch_entity_id, async_state_changed_listener
        )

    async def async_will_remove_from_hass(self):
        """Handle removal from Home Assistant."""
        if self._async_unsub_state_changed is not None:
            self._async_unsub_state_changed()
            self._async_unsub_state_changed = None
            self._available = False

