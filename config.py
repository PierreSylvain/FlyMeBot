#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "851864ee-9c18-44fc-9902-a43f474ac040")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "Ceciestunmot2passe")
    LUIS_APP_ID = os.environ.get("LuisAppId", "4d592d65-9c86-4987-a131-c73f66f26f55")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "06517d0c606c4cafb0ab434f6ff14bfc")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "ec490e47-b106-4b1b-a810-8d763f5129c9"
    )
    APPINSIGHTS_INSTRUMENTATION = os.environ.get(
        "AppInsightsInstrumentationCnx", "InstrumentationKey=ec490e47-b106-4b1b-a810-8d763f5129c9;IngestionEndpoint=https://switzerlandnorth-0.in.applicationinsights.azure.com/"
    )
    # https://flyme26.azurewebsites.net/api/messages
    # az ad app create --display-name "flyme26" --password "Ceciestunmot2passe" --available-to-other-tenants
