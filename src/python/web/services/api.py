import json
import re
from dataclasses import dataclass
from typing import Optional

import google.auth.transport.requests  # type: ignore
import google.oauth2.id_token  # type: ignore
import httpx
from common.models.yes_no_answer_classifier import YesNoAnswerInput, YesNoPrediction
from google.auth.credentials import Credentials  # type: ignore
from pydantic import BaseModel


@dataclass(frozen=True)
class ServicesConnection:
    host: str
    credentials: Optional[Credentials]


def init_services_connection(
    host: str,
    add_auth: bool,
) -> ServicesConnection:
    credentials = None
    if add_auth:
        auth_req = google.auth.transport.requests.Request()

        audience = host
        tagged_host = re.match("(https://.*---).*", host)
        if tagged_host:
            tag_prefix = tagged_host.groups()[0]
            audience = f"https://{host.removeprefix(tag_prefix)}"

        credentials = google.oauth2.id_token.fetch_id_token_credentials(
            request=auth_req,
            audience=audience,
        )

    return ServicesConnection(
        host=host,
        credentials=credentials,
    )


def _make_json_headers(cxn: ServicesConnection) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if cxn.credentials:
        if cxn.credentials.token is None or cxn.credentials.expired:
            auth_req = google.auth.transport.requests.Request()
            cxn.credentials.refresh(request=auth_req)
        headers["Authorization"] = f"Bearer {cxn.credentials.token}"
    return headers


class YesNoAnswerRequest(BaseModel):
    inputs: list[YesNoAnswerInput]
    query: str
    min_probability_threshold: Optional[float]


class YesNoAnswerResponse(BaseModel):
    predictions: list[YesNoPrediction]


async def predict_yes_no_answers(
    cxn: ServicesConnection,
    inputs: list[YesNoAnswerInput],
    query: str,
    min_probability_threshold: Optional[float],
) -> YesNoAnswerResponse:
    async with httpx.AsyncClient() as client:
        request = YesNoAnswerRequest(
            inputs=inputs,
            query=query,
            min_probability_threshold=min_probability_threshold,
        )
        response = await client.post(
            url=f"{cxn.host}/yes_no_answer",
            json=request.dict(),
            headers=_make_json_headers(cxn),
            timeout=30.0,
        )
        if response.status_code != httpx.codes.OK:
            response.raise_for_status()
        return YesNoAnswerResponse(**(json.loads(response.text)))
