import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from .const import DOMAIN, DEFAULT_PORT, DEFAULT_NAME
from .tascam import TascamClient

class TascamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        self._host = None
        self._port = None

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            client = TascamClient(host, port)
            try:
                await client.connect()
                await client.disconnect()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                self._host = host
                self._port = port
                return await self.async_step_name()

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        })
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

    async def async_step_name(self, user_input=None):
        if user_input and CONF_NAME in user_input:
            name = user_input[CONF_NAME]
            return self.async_create_entry(
                title=name,
                data={
                    CONF_HOST: self._host,
                    CONF_PORT: self._port,
                    CONF_NAME: name,
                },
            )

        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        })
        return self.async_show_form(
            step_id="name",
            data_schema=data_schema
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return TascamOptionsFlowHandler(config_entry)

class TascamOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input:
            return self.async_create_entry(title="", data=user_input)
        schema = vol.Schema({
            vol.Required(CONF_HOST, default=self.config_entry.data[CONF_HOST]): str,
            vol.Optional(CONF_PORT, default=self.config_entry.data.get(CONF_PORT, DEFAULT_PORT)): int,
            vol.Required(CONF_NAME, default=self.config_entry.data.get(CONF_NAME, self.config_entry.title)): str,
        })
        return self.async_show_form(
            step_id="init",
            data_schema=schema
        )
