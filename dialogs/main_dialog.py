# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import (
    MessageFactory,
    TurnContext,
    BotTelemetryClient,
    NullTelemetryClient,
)
from botbuilder.schema import InputHints

from booking_details import BookingDetails
from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper, Intent
from .booking_dialog import BookingDialog

from config import DefaultConfig
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from datetime import datetime
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module

class MainDialog(ComponentDialog):
    def __init__(
        self,
        luis_recognizer: FlightBookingRecognizer,
        booking_dialog: BookingDialog,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)
        self.telemetry_client = telemetry_client or NullTelemetryClient()

        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = self.telemetry_client

        booking_dialog.telemetry_client = self.telemetry_client
        self.logger = logging.getLogger(__name__)
        configuration = DefaultConfig()
        self.logger.addHandler(AzureLogHandler(connection_string=configuration.APPINSIGHTS_INSTRUMENTATION))

        stats = stats_module.stats
        view_manager = stats.view_manager
        stats_recorder = stats.stats_recorder

        self.accepted_measure = measure_module.MeasureInt("Accepted",
                                           "number of accepted booking",
                                           "Accepted")
        accepted_view = view_module.View("Accepted Booking view",
                               "number of Accepted booking",
                               [],
                               self.accepted_measure,
                               aggregation_module.CountAggregation())
        view_manager.register_view(accepted_view)

        self.canceled_measure = measure_module.MeasureInt("Canceled",
                                           "number of canceled booking",
                                           "Canceled")
        canceled_view = view_module.View("Canceled Booking view",
                               "number of Canceled booking",
                               [],
                               self.canceled_measure,
                               aggregation_module.CountAggregation())
        view_manager.register_view(canceled_view)


        self.accepted_mmap = stats_recorder.new_measurement_map()
        self.tmap_accepted = tag_map_module.TagMap()

        self.canceled_mmap = stats_recorder.new_measurement_map()
        self.tmap_canceled = tag_map_module.TagMap()

        configuration = DefaultConfig()
        exporter = metrics_exporter.new_metrics_exporter(connection_string=configuration.APPINSIGHTS_INSTRUMENTATION)
        view_manager.register_exporter(exporter)

        wf_dialog = WaterfallDialog(
            "WFDialog", [self.intro_step, self.act_step, self.final_step]
        )
        wf_dialog.telemetry_client = self.telemetry_client

        self._luis_recognizer = luis_recognizer
        self._booking_dialog_id = booking_dialog.id

        self.add_dialog(text_prompt)
        self.add_dialog(booking_dialog)
        self.add_dialog(wf_dialog)

        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)
        message_text = (
            str(step_context.options)
            if step_context.options
            else "What can I help you with today?"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            # LUIS is not configured, we just run the BookingDialog path with an empty BookingDetailsInstance.
            return await step_context.begin_dialog(
                self._booking_dialog_id, BookingDetails()
            )

        # Call LUIS and gather any potential booking details. (Note the TurnContext has the response to the prompt.)
        intent, luis_result = await LuisHelper.execute_luis_query(
            self._luis_recognizer, step_context.context
        )

        if intent == Intent.BOOK_FLIGHT.value and luis_result:
            # Show a warning for Origin and Destination if we can't resolve them.
            await MainDialog._show_warning_for_unsupported_cities(
                step_context.context, luis_result
            )

            # Run the BookingDialog giving it whatever details we have from the LUIS call.
            return await step_context.begin_dialog(self._booking_dialog_id, luis_result)

        if intent == Intent.GET_WEATHER.value:
            get_weather_text = "TODO: get weather flow here"
            get_weather_message = MessageFactory.text(
                get_weather_text, get_weather_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(get_weather_message)

        else:
            didnt_understand_text = (
                "Sorry, I didn't get that. Please try asking in a different way"
            )
            didnt_understand_message = MessageFactory.text(
                didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(didnt_understand_message)

        return await step_context.next(None)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # If the child dialog ("BookingDialog") was cancelled or the user failed to confirm,
        # the Result here will be null.
        if step_context.result is not None:
            result = step_context.result

            self.accepted_mmap.measure_int_put(self.accepted_measure, 1)
            self.accepted_mmap.record(self.tmap_accepted)

            departure_date = datetime.strptime(result.departure_date, "%Y-%m-%d").date()
            return_date = datetime.strptime(result.return_date, "%Y-%m-%d").date()
            msg_txt = (
                f"I have booked a fly from { result.origin } to { result.destination } on {departure_date.strftime('%B %d %Y')}"
                f" and return on {return_date.strftime('%B %d %Y')}."
                f" with a budget of {result.budget}."
            )
            self.logger.warning(f"Confirmed: {msg_txt}")
            message = MessageFactory.text(msg_txt, msg_txt, InputHints.ignoring_input)
            await step_context.context.send_activity(message)
        else:
            self.logger.error("The dialog had been canceled or not confirmed by user")
            self.canceled_mmap.measure_int_put(self.canceled_measure, 1)
            self.canceled_mmap.record(self.tmap_canceled)


        prompt_message = "What else can I do for you?"
        return await step_context.replace_dialog(self.id, prompt_message)

    @staticmethod
    async def _show_warning_for_unsupported_cities(
        context: TurnContext, luis_result: BookingDetails
    ) -> None:
        """
        Shows a warning if the requested From or To cities are recognized as entities but they are not in the Airport entity list.
        In some cases LUIS will recognize the From and To composite entities as a valid cities but the From and To Airport values
        will be empty if those entity values can't be mapped to a canonical item in the Airport.
        """
        if luis_result.unsupported_airports:
            message_text = (
                f"Sorry but the following airports are not supported:"
                f" {', '.join(luis_result.unsupported_airports)}"
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await context.send_activity(message)
