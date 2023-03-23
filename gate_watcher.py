import aiohttp

from soar_core.actions.base_action import BaseApp
from soar_core.functions import initialize_logger

logger = initialize_logger()


class App(BaseApp):
    NAME = "Gatewatcher NDR GW GCenter"
    ENDPOINT = {
        "base_url": "https://demo2.gatewatcher.com/",
        "auth_endpoint": "/api/auth/login/",
        "api_alerts_endpoint": "api/alerts/?sort_by=-date",
    }

    async def get_alert(self, payload):
        logger.info(f"Get alert called and parameters = {payload}")
        url = f'{self.ENDPOINT["base_url"]}{self.ENDPOINT["api_alerts_endpoint"]}'
        headers = {"API-KEY": await self.authorize()}

        async with aiohttp.ClientSession(
            headers=headers, connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            async with session.get(url, params=payload) as res:
                response_data = await res.json()
                if res.status == 400:
                    raise Exception(
                        f"Gate Watcher get_alert action response: {response_data}"
                    )

        return response_data

    async def black_list(self, payload: dict) -> dict:
        url = f"{self.base_url}/black-list/"
        return await self._send_request(url, payload)

    async def white_list(self, payload: dict) -> dict:
        url = f"{self.base_url}/white-list/"
        return await self._send_request(url, payload)

    async def _generate_token(self):
        url = f'{self.ENDPOINT["base_url"]}{self.ENDPOINT["auth_endpoint"]}'
        config = self.get_config()
        data = {"username": config["client"], "password": config["password"]}

        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            async with session.post(url, json=data) as res:
                response_data = await res.json()
                if res.status == 400:
                    raise Exception(
                        f"Token could not generate app id: {config['app_id']} client id: {config['client']}"
                    )

        token = response_data["token"]
        expiration_date = response_data["expiration_date"].replace("T", " ")
        self.save_token_data({"token": token, "expiration_date": expiration_date})
        return token

    async def _send_request(self, url, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=self.headers, params=payload
            ) as response:
                return await response.json()

    def validate_input(self, inp):
        pass

    def validate_output(self, out):
        pass

    def get_result_mapper():
        pass
