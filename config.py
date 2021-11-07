#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "426d7f96-c527-4de8-9146-18e6a9b8ef47")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "CeciEstUnMot2PasseAssezLong")
    LUIS_APP_ID = os.environ.get("LuisAppId", "4d592d65-9c86-4987-a131-c73f66f26f55")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "06517d0c606c4cafb0ab434f6ff14bfc")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "99aff7b0-2faa-4bb2-86c1-b8f6ee7cbf34"
    )
    APPINSIGHTS_INSTRUMENTATION = os.environ.get(
        "AppInsightsInstrumentationCnx", "InstrumentationKey=99aff7b0-2faa-4bb2-86c1-b8f6ee7cbf34;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/"
    )
