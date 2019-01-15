# -*- coding: utf-8 -*-

import logging

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import random
import boto3
import os
import json

from alexa import data, util
from backing_track_generator.backing_track_generator import BackingTrackGenerator

from ask_sdk_model.services.directive import (
    SendDirectiveRequest, Header, SpeakDirective)

sb = CustomSkillBuilder(api_client=DefaultApiClient())
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ######################### INTENT HANDLERS #########################
# This section contains handlers for the built-in intents and generic
# request handlers like launch, session end, skill events etc.

class CheckAudioInterfaceHandler(AbstractRequestHandler):
    """Check if device supports audio play.

    This can be used as the first handler to be checked, before invoking
    other handlers, thus making the skill respond to unsupported devices
    without doing much processing.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        if handler_input.request_envelope.context.system.device:
            # Since skill events won't have device information
            return handler_input.request_envelope.context.system.device.supported_interfaces.audio_player is None
        else:
            return False

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CheckAudioInterfaceHandler")
        handler_input.response_builder.speak(
            data.DEVICE_NOT_SUPPORTED).set_should_end_session(True)
        return handler_input.response_builder.response


class SkillEventHandler(AbstractRequestHandler):
    """Close session for skill events or when session ends.

    Handler to handle session end or skill events (SkillEnabled,
    SkillDisabled etc.)
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (handler_input.request_envelope.request.object_type.startswith(
            "AlexaSkillEvent") or
                is_request_type("SessionEndedRequest")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SkillEventHandler")
        return handler_input.response_builder.response


class LaunchRequestOrPlayAudioHandler(AbstractRequestHandler):
    """Skill launch or PlayAudio intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("LaunchRequest")(handler_input) or
                is_intent_name("PlayAudio")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestOrPlayAudioHandler")

        request = handler_input.request_envelope.request

        # can add a default song here to play back
        speech = data.WELCOME_MSG.format(util.audio_data(request)["card"]["title"])
        return handler_input.response_builder.speak(speech).set_should_end_session(False).response
        #return util.play(url=util.audio_data(request)["url"],
        #                 offset=0,
        #                 text=data.WELCOME_MSG.format(
        #                     util.audio_data(request)["card"]["title"]),
        #                 card_data=util.audio_data(request)["card"],
        #                 response_builder=handler_input.response_builder)

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for providing help information to user."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")
        handler_input.response_builder.speak(
            data.HELP_MSG.format(
                util.audio_data(
                    handler_input.request_envelope.request)["card"]["title"])
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class UnhandledIntentHandler(AbstractRequestHandler):
    """Handler for fallback intent, for unmatched utterances.

    2018-July-12: AMAZON.FallbackIntent is currently available in all
    English locales. This handler will not be triggered except in that
    locale, so it can be safely deployed for any locale. More info
    on the fallback intent can be found here:
    https://developer.amazon.com/docs/custom-skills/standard-built-in-intents.html#fallback
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In UnhandledIntentHandler")

        handler_input.response_builder.speak(
            data.UNHANDLED_MSG).set_should_end_session(True)
        return handler_input.response_builder.response


class NextOrPreviousIntentHandler(AbstractRequestHandler):
    """Handler for next or previous intents."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.NextIntent")(handler_input) or
                is_intent_name("AMAZON.PreviousIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NextOrPreviousIntentHandler")

        handler_input.response_builder.speak(
            data.CANNOT_SKIP_MSG).set_should_end_session(True)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler for cancel, stop or pause intents."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        return util.stop(random.choice(data.STOP_MSG), handler_input.response_builder)


class ResumeIntentHandler(AbstractRequestHandler):
    """Handler for resume intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ResumeIntentHandler")
        request = handler_input.request_envelope.request

        # can add a default song here to play back
        speech = data.NOT_POSSIBLE_MSG
        return handler_input.response_builder.speak(speech).response
        #speech = data.RESUME_MSG.format(
        #    util.audio_data(request)["card"]["title"])
        #return util.play(
        #    url=util.audio_data(request)["url"], offset=0,
        #    text=speech, card_data=util.audio_data(request)["card"],
        #    response_builder=handler_input.response_builder)


class StartOverIntentHandler(AbstractRequestHandler):
    """Handler for start over, loop on/off, shuffle on/off intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.StartOverIntent")(handler_input) or
                is_intent_name("AMAZON.LoopOnIntent")(handler_input) or
                is_intent_name("AMAZON.LoopOffIntent")(handler_input) or
                is_intent_name("AMAZON.ShuffleOnIntent")(handler_input) or
                is_intent_name("AMAZON.ShuffleOffIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In StartOverIntentHandler")


        speech = data.NOT_POSSIBLE_MSG
        return handler_input.response_builder.speak(speech).response

class RepeatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.RepeatIntent")(handler_input))

    def get_context(self, user_id):
        filename = os.path.join("/tmp",user_id)
        s3path = os.path.join("user_context",user_id)
        print("Getting {}".format(s3path))
        s3 = boto3.resource('s3')
        s3.Bucket(BackingTrackGenerator.BUCKET_NAME).download_file(s3path, filename)

        with open(filename) as f:
            song_data = json.load(f)
        return song_data

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        request = handler_input.request_envelope.request
        user_id = handler_input.request_envelope.session.user.user_id
        song_data = self.get_context(user_id)

        generated_song_text = data.GENERATED_SONG.format(song_data["song_name"])
        if song_data["key"]:
            generated_song_text += data.GENERATED_SONG_KEY.format(song_data["key"])
        if song_data["tempo"]:
            generated_song_text += data.GENERATED_SONG_TEMPO.format(song_data["tempo"])
        return util.play(url=song_data["backing_track_url"],
                 offset=0,
                 text=generated_song_text,
                 card_data=util.audio_data(request)["card"],
                 response_builder=handler_input.response_builder)


class PlayGeneratedMusicHandler(AbstractRequestHandler):
    """Handler for playing generated music."""

    def get_song_resolved_value(self, slots):
        slot = slots.get("SongName")
        if slot:
            if slot.resolutions:
                if slot.resolutions.resolutions_per_authority[0].values:
                    return slot.resolutions.resolutions_per_authority[0].values[0].value.name
                return slot.value
            else:
                return slot.value

    def can_handle(self, handler_input):
        return is_intent_name("PlayGeneratedMusicIntent")(handler_input)

    def save_context(self, backing_track_url, user_id, song_name, tempo, key):
        filename = os.path.join("/tmp",user_id)

        if os.path.exists(filename):
          print("Removing preexisting file {}".format(filename))
          os.remove(filename)
        else:
          print("Preexisting file {} does not exist".format(filename))

        logger.info("Writing context file to {}".format(filename))
        filecontents = {"backing_track_url":backing_track_url,
                        "song_name":song_name,
                        "tempo":tempo,
                        "key":key}
        with open(filename, 'w') as file:
            json.dump(filecontents, file)

        s3path = os.path.join("user_context",user_id)
        logger.info("Writing context file to S3, path {}".format(s3path))
        s3 = boto3.resource('s3')
        s3.Bucket(BackingTrackGenerator.BUCKET_NAME).upload_file(filename, s3path)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlayGeneratedMusicHandler")
        request = handler_input.request_envelope.request

        request_id_holder = handler_input.request_envelope.request.request_id
        directive_header = Header(request_id=request_id_holder)
        speech = SpeakDirective(speech=random.choice(data.PROGRESSIVE_RESPONSE))
        directive_request = SendDirectiveRequest(
        header=directive_header, directive=speech)

        directive_service_client = handler_input.service_client_factory.get_directive_service()
        directive_service_client.enqueue(directive_request)
        
        user_id = handler_input.request_envelope.session.user.user_id

        slots = request.intent.slots
        song_name = self.get_song_resolved_value(slots)
        tempo = slots.get("Tempo").value
        key = slots.get("Key").value

        backing_track_url = BackingTrackGenerator().get_backing_track(slots)

        self.save_context(backing_track_url, user_id, song_name, tempo, key)

        generated_song_text = data.GENERATED_SONG.format(song_name)
        if key:
            generated_song_text += data.GENERATED_SONG_KEY.format(key)
        if tempo:
            generated_song_text += data.GENERATED_SONG_TEMPO.format(tempo)
        return util.play(url=backing_track_url,
                 offset=0,
                 text=generated_song_text,
                 card_data=util.audio_data(request)["card"],
                 response_builder=handler_input.response_builder)

# ###################################################################

# ########## AUDIOPLAYER INTERFACE HANDLERS #########################
# This section contains handlers related to Audioplayer interface

class PlaybackStartedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackStarted Directive received.

    Confirming that the requested audio file began playing.
    Do not send any specific response.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackStarted")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackStartedHandler")
        logger.info("Playback started")
        return handler_input.response_builder.response

class PlaybackFinishedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackFinished Directive received.

    Confirming that the requested audio file completed playing.
    Do not send any specific response.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackFinished")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackFinishedHandler")
        logger.info("Playback finished")
        return handler_input.response_builder.response


class PlaybackStoppedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackStopped Directive received.

    Confirming that the requested audio file stopped playing.
    Do not send any specific response.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackStopped")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackStoppedHandler")
        logger.info("Playback stopped")
        return handler_input.response_builder.response

class PlaybackNearlyFinishedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackNearlyFinished Directive received.

    Replacing queue with the URL again. This should not happen on live streams.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackNearlyFinished")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackNearlyFinishedHandler")
        logger.info("Playback nearly finished")
        request = handler_input.request_envelope.request
        return util.play_later(
            url=util.audio_data(request)["url"],
            card_data=util.audio_data(request)["card"],
            response_builder=handler_input.response_builder)


class PlaybackFailedHandler(AbstractRequestHandler):
    """AudioPlayer.PlaybackFailed Directive received.

    Logging the error and restarting playing with no output speech and card.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("AudioPlayer.PlaybackFailed")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlaybackFailedHandler")
        request = handler_input.request_envelope.request
        logger.info("Playback failed: {}".format(request.error))

        # can add a default song here to play back
        return handler_input.response_builder.response

        #return util.play(
        #    url=util.audio_data(request)["url"], offset=0, text=None,
        #    card_data=None,
        #    response_builder=handler_input.response_builder)


class ExceptionEncounteredHandler(AbstractRequestHandler):
    """Handler to handle exceptions from responses sent by AudioPlayer
    request.
    """
    def can_handle(self, handler_input):
        # type; (HandlerInput) -> bool
        return is_request_type("System.ExceptionEncountered")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("\n**************** EXCEPTION *******************")
        logger.info(handler_input.request_envelope)
        return handler_input.response_builder.response

# ###################################################################

# ########## PLAYBACK CONTROLLER INTERFACE HANDLERS #################
# This section contains handlers related to Playback Controller interface
# https://developer.amazon.com/docs/custom-skills/playback-controller-interface-reference.html#requests

class PlayCommandHandler(AbstractRequestHandler):
    """Handler for Play command from hardware buttons or touch control.

    This handler handles the play command sent through hardware buttons such
    as remote control or the play control from Alexa-devices with a screen.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type(
            "PlaybackController.PlayCommandIssued")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PlayCommandHandler")

        request = handler_input.request_envelope.request
        return handler_input.response_builder.response
        #return util.play(url=util.audio_data(request)["url"],
        #                 offset=0,
        #                 text=None,
        #                 card_data=None,
        #                 response_builder=handler_input.response_builder)


class NextOrPreviousCommandHandler(AbstractRequestHandler):
    """Handler for Next or Previous command from hardware buttons or touch
    control.

    This handler handles the next/previous command sent through hardware
    buttons such as remote control or the next/previous control from
    Alexa-devices with a screen.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type(
            "PlaybackController.NextCommandIssued")(handler_input) or
                is_request_type(
                    "PlaybackController.PreviousCommandIssued")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NextOrPreviousCommandHandler")
        return handler_input.response_builder.response


class PauseCommandHandler(AbstractRequestHandler):
    """Handler for Pause command from hardware buttons or touch control.

    This handler handles the pause command sent through hardware
    buttons such as remote control or the pause control from
    Alexa-devices with a screen.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("PlaybackController.PauseCommandIssued")(
            handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PauseCommandHandler")
        return util.stop(text=None,
                         response_builder=handler_input.response_builder)

# ###################################################################

# ################## EXCEPTION HANDLERS #############################
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(data.UNHANDLED_MSG).ask(
            data.HELP_MSG.format(
                util.audio_data(
                    handler_input.request_envelope.request)["card"]["title"]))

        return handler_input.response_builder.response

# ###################################################################

# ############# REQUEST / RESPONSE INTERCEPTORS #####################
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))

class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))

# ###################################################################


# ############# REGISTER HANDLERS #####################
# Request Handlers
sb.add_request_handler(CheckAudioInterfaceHandler())
sb.add_request_handler(SkillEventHandler())
sb.add_request_handler(LaunchRequestOrPlayAudioHandler())
sb.add_request_handler(PlayCommandHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExceptionEncounteredHandler())
sb.add_request_handler(UnhandledIntentHandler())
sb.add_request_handler(NextOrPreviousIntentHandler())
sb.add_request_handler(NextOrPreviousCommandHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(PauseCommandHandler())
sb.add_request_handler(ResumeIntentHandler())
sb.add_request_handler(StartOverIntentHandler())
sb.add_request_handler(PlaybackStartedHandler())
sb.add_request_handler(PlaybackFinishedHandler())
sb.add_request_handler(PlaybackStoppedHandler())
sb.add_request_handler(RepeatIntentHandler())
# not used yet sb.add_request_handler(PlaybackNearlyFinishedHandler())
sb.add_request_handler(PlaybackStartedHandler())
sb.add_request_handler(PlaybackFailedHandler())
sb.add_request_handler(PlayGeneratedMusicHandler())

# Exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# Interceptors
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# AWS Lambda handler
lambda_handler = sb.lambda_handler()
