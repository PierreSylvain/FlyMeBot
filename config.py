#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "b3e4cf5d-0dfc-426c-a3b6-3a031f3fc645")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "Ceciestunmot2passe>")
    LUIS_APP_ID = os.environ.get("LuisAppId", "4d592d65-9c86-4987-a131-c73f66f26f55")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "06517d0c606c4cafb0ab434f6ff14bfc")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "3cb89e6d-14fa-4d3b-ab8f-aec8200fd004"
    )
    APPINSIGHTS_INSTRUMENTATION = os.environ.get(
        "AppInsightsInstrumentationCnx", "InstrumentationKey=3cb89e6d-14fa-4d3b-ab8f-aec8200fd004;IngestionEndpoint=https://francecentral-1.in.applicationinsights.azure.com/"
    )
