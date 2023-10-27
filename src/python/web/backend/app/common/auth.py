import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import jwt
from common.config.secret_manager import SecretId, access_secret
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from loguru import logger

# Number of chunks the Clerk verification key is split into
# See documentation for details:
# https://clerk.dev/docs/request-authentication/validate-session-tokens#using-the-jwt-verification-key
CLERK_JWT_KEY_SPLIT_LEN = 64
CLERK_JWT_VERIFICATION_KEY = None


class AuthEnv(Enum):
    """
    All supported Clerk environments.
    """

    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


def _get_clerk_jwt_verification_key(env: AuthEnv) -> str:
    if env == AuthEnv.LOCAL:
        return access_secret(SecretId.CLERK_JWT_VERIFICATION_KEY_LOCAL, use_env_var=True)
    elif env == AuthEnv.DEV:
        return access_secret(SecretId.CLERK_JWT_VERIFICATION_KEY_DEV)
    elif env == AuthEnv.PROD:
        return access_secret(SecretId.CLERK_JWT_VERIFICATION_KEY_PROD)
    else:
        raise ValueError(f"Failed to get clerk jwt verification key: unknown env {env}")


def _get_consensus_test_api_key(env: AuthEnv) -> Optional[str]:
    if env == AuthEnv.LOCAL:
        return access_secret(SecretId.CONSENSUS_TEST_API_KEY, use_env_var=True)
    else:
        return access_secret(SecretId.CONSENSUS_TEST_API_KEY, use_env_var=False)


@dataclass(frozen=True)
class ClerkAuthToken:
    user_id: str
    auth_token_expiry: str


@dataclass(frozen=True)
class User:
    auth: Optional[ClerkAuthToken]
    verified_by_api_key: bool
    ip_address: Optional[str]


def get_verified_clerk_user(request: Request, env: AuthEnv) -> Optional[ClerkAuthToken]:
    """
    Returns a parsed fields from the JWT auth token or None if not found.

    Raises:
        ValueError: if decoded JWT token is missing expected fields
    """
    authorization = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        return None

    key = _get_clerk_jwt_verification_key(env)
    x = CLERK_JWT_KEY_SPLIT_LEN
    split_pem = "\n".join([key[i : i + x] for i in range(0, len(key), x)])  # noqa: E203
    public_key = f"-----BEGIN PUBLIC KEY-----\n{split_pem}\n-----END PUBLIC KEY-----"

    # Parse values from decoded token
    # https://clerk.dev/docs/request-authentication/customizing-session-tokens#customizing-session-tokens
    header_data = jwt.get_unverified_header(token)
    token_claims = jwt.decode(
        token,
        public_key,
        algorithms=[
            header_data["alg"],
        ],
    )
    user = token_claims["sub"]
    if user is None:
        raise ValueError("Failed to decode auth_token: jwt missing sub: {token_claims}")

    expiry = token_claims["exp"]
    if expiry is None:
        raise ValueError("Failed to decode auth_token: jwt missing exp: {token_claims}")

    return ClerkAuthToken(
        user_id=user,
        auth_token_expiry=expiry,
    )


def _is_google_health_check(request: Request) -> bool:
    """
    Returns whether the request has a GoogleHC user agent.
    """
    user_agent = str(request.headers.get("user-agent", ""))
    return user_agent == "GoogleHC/1.0"


def _is_verified_by_test_api_key(request: Request, env: AuthEnv) -> bool:
    """
    Returns whether the request is verified by a test api key, which indicates
    that the request is a part of a test.
    """
    x_api_key = str(request.headers.get("x-api-key", ""))
    return x_api_key == _get_consensus_test_api_key(env)


def _get_ip_address(request: Request) -> Optional[str]:
    """
    Returns the client's IP address or None if could not parse.
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if not x_forwarded_for:
        logger.error("Failed to get IP address: missing X-Forwarded-For header")
        return None

    forwarded_ips = re.split(", ", x_forwarded_for)
    if len(forwarded_ips) <= 0:
        logger.error(f"Failed to get IP address: found 0 ips: {x_forwarded_for}")
        return None

    return str(forwarded_ips[0])


def get_user(request: Request, env: AuthEnv) -> User:
    """
    Returns a parsed fields from the JWT auth token or None if not found.

    Raises:
        ValueError: if decoded JWT token is missing expected fields
    """

    clerk_user = get_verified_clerk_user(request, env)
    verified_by_api_key = _is_verified_by_test_api_key(request, env)
    is_google_hc = _is_google_health_check(request)
    ip_address = _get_ip_address(request) if not is_google_hc else "google_hc"

    return User(
        auth=clerk_user,
        verified_by_api_key=verified_by_api_key,
        ip_address=ip_address,
    )
