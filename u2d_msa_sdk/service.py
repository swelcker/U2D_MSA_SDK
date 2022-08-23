import os

import httpx
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import Json
from starlette.responses import JSONResponse

import healthcheck as health
from u2d_msa_sdk.msaapi import MSAFastAPI
from u2d_msa_sdk.schemas.service import MSAServiceDefinition, MSAHealthDefinition
import uvloop


class NoMasterService(Exception):
    def __init__(self, msg="MSAServiceBase is running as Slave"):
        self.msg = msg


async def healthcheck():
    return JSONResponse({"status": os.getenv("API_HEALTH_RESPONSE", "MSA Service is running")})


def register_service(service_definition: MSAServiceDefinition):
    httpx.put(os.getenv("API_REGISTER_PATH"), json=service_definition.json())


class MSAApp(MSAFastAPI):
    def __init__(
            self,
            is_master=False,
            healthdefinition: MSAHealthDefinition = MSAHealthDefinition(),
            *args,
            **kwargs
    ) -> None:

        # call super class __init__
        uvloop.install()
        super().__init__(*args, **kwargs)

        self.is_master = is_master
        self.services = []
        self.healthchecks = {}
        self.add_api_route(healthdefinition.path, healthcheck)

        if self.is_master:
            Instrumentator().instrument(self).expose(self)
            # add service registration
            self.add_api_route("/services/register", self.add_service)
            self.add_api_route("/services/status", self.get_services_status)
            self.add_api_route("/services/definition", self.get_services_openapi)

    async def get_services_status(self) -> JSONResponse:
        return JSONResponse(
            [
                {
                    "name": service.name,
                    "status": self.healthchecks[service.name].get_health()
                    if self.healthchecks.get(service.name, False)
                    else "No healthcheck!",
                }
                for service in self.services
            ]
        )

    async def add_service(self, service_definition: Json) -> JSONResponse:
        service_def: MSAServiceDefinition = MSAServiceDefinition.parse_obj(service_definition)
        self.services.append(service_def)
        if service_def.healthcheck:
            self.healthchecks[service_def.name] = health.MSAHealthCheck(
                service_def.healthcheck
            )
            self.healthchecks[service_def.name].start()
        return JSONResponse(
            [
                {
                    "name": service_def.name,
                    "status": "added"
                }
            ]
        )

    async def get_services_openapi(self) -> JSONResponse:
        def try_get_json(url):
            try:
                return httpx.get(url).json()
            except Exception as e:
                return {"status": "service is off"}

        return JSONResponse(
            [
                {
                    service.name: try_get_json(
                        "http://{}:{}/openapi.json".format(service.host, service.port)
                    ),
                }
                for service in self.services
            ]
        )
