import logging
import uuid
import base64
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Text

from rasa.core.channels.channel import InputChannel, OutputChannel, UserMessage
import rasa.shared.utils.io
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from socketio import AsyncServer

from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json

logger = logging.getLogger(__name__)

class SocketVoiceBlueprint(Blueprint):
    def __init__(self, sio: AsyncServer, socketio_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sio = sio
        self.socketio_path = socketio_path


    def register(self, app, options) -> None:
        self.sio.attach(app, self.socketio_path)
        super().register(app, options)


class SocketIOVoiceOutput(OutputChannel):
    @classmethod
    def name(cls) -> Text:
        return "socketiovoice"

    def __init__(self, sio: AsyncServer, bot_message_evt: Text, botium_speech_url: Text, botium_speech_apikey: Text, botium_speech_language: Text, botium_speech_voice: Text) -> None:
        self.sio = sio
        self.bot_message_evt = bot_message_evt
        self.botium_speech_url = botium_speech_url
        self.botium_speech_apikey = botium_speech_apikey
        self.botium_speech_language = botium_speech_language
        self.botium_speech_voice = botium_speech_voice

    async def _send_message(self, socket_id: Text, response: Any) -> None:
        """Sends a message to the recipient using the bot event."""

        if response.get("text"):
          q = {
            'text': response['text']
          }
          if self.botium_speech_voice:
            q['voice'] = self.botium_speech_voice

          audioEndpoint = f"{self.botium_speech_url}/api/tts/{self.botium_speech_language}?{urlencode(q)}"
          audio = urlopen(audioEndpoint).read()
          logger.debug(f"_send_message- Calling Speech Endpoint: {audioEndpoint}")

          audioBase64 = base64.b64encode(audio).decode('ascii')
          audioUri = "data:audio/wav;base64," + audioBase64
          response['link'] = audioUri

        await self.sio.emit(self.bot_message_evt, response, room=socket_id)

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        """Send a message through this channel."""

        for message_part in text.strip().split("\n\n"):
            await self._send_message(recipient_id, {"text": message_part})

    async def send_image_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        """Sends an image to the output"""

        message = {"attachment": {"type": "image", "payload": {"src": image}}}
        await self._send_message(recipient_id, message)

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any,
    ) -> None:
        """Sends buttons to the output."""

        # split text and create a message for each text fragment
        # the `or` makes sure there is at least one message we can attach the quick
        # replies to
        message_parts = text.strip().split("\n\n") or [text]
        messages = [{"text": message, "quick_replies": []} for message in message_parts]

        # attach all buttons to the last text fragment
        for button in buttons:
            messages[-1]["quick_replies"].append(
                {
                    "content_type": "text",
                    "title": button["title"],
                    "payload": button["payload"],
                }
            )

        for message in messages:
            await self._send_message(recipient_id, message)

    async def send_elements(
        self, recipient_id: Text, elements: Iterable[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Sends elements to the output."""

        for element in elements:
            message = {
                "attachment": {
                    "type": "template",
                    "payload": {"template_type": "generic", "elements": element},
                }
            }

            await self._send_message(recipient_id, message)

    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Sends custom json to the output"""

        json_message.setdefault("room", recipient_id)

        await self.sio.emit(self.bot_message_evt, **json_message)

    async def send_attachment(
        self, recipient_id: Text, attachment: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Sends an attachment to the user."""
        await self._send_message(recipient_id, {"attachment": attachment})


class SocketIOVoiceInput(InputChannel):
    """A socket.io input channel."""

    @classmethod
    def name(cls) -> Text:
        return "socketiovoice"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        credentials = credentials or {}
        return cls(
            credentials.get("user_message_evt", "user_uttered"),
            credentials.get("bot_message_evt", "bot_uttered"),
            credentials.get("namespace"),
            credentials.get("session_persistence", False),
            credentials.get("socketio_path", "/socket.io"),
            credentials.get("botium_speech_url"),
            credentials.get("botium_speech_apikey"),
            credentials.get("botium_speech_language", "en"),
            credentials.get("botium_speech_voice"),
        )

    def __init__(
        self,
        user_message_evt: Text = "user_uttered",
        bot_message_evt: Text = "bot_uttered",
        namespace: Optional[Text] = None,
        session_persistence: bool = False,
        socketio_path: Optional[Text] = "/socket.io",
        botium_speech_url: Text = None,
        botium_speech_apikey: Optional[Text] = None,
        botium_speech_language: Text = "en",
        botium_speech_voice: Optional[Text] = False,
    ):
        self.bot_message_evt = bot_message_evt
        self.session_persistence = session_persistence
        self.user_message_evt = user_message_evt
        self.namespace = namespace
        self.socketio_path = socketio_path
        self.botium_speech_url = botium_speech_url
        self.botium_speech_apikey = botium_speech_apikey
        self.botium_speech_language = botium_speech_language
        self.botium_speech_voice = botium_speech_voice
        self.sio = None

    def get_output_channel(self) -> Optional["OutputChannel"]:
        if self.sio is None:
            rasa.shared.utils.io.raise_warning(
                "SocketIO output channel cannot be recreated. "
                "This is expected behavior when using multiple Sanic "
                "workers or multiple Rasa Open Source instances. "
                "Please use a different channel for external events in these "
                "scenarios."
            )
            return
        return SocketIOVoiceOutput(self.sio, self.bot_message_evt, self.botium_speech_url, self.botium_speech_apikey, self.botium_speech_language, self.botium_speech_voice)

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        # Workaround so that socketio works with requests from other origins.
        # https://github.com/miguelgrinberg/python-socketio/issues/205#issuecomment-493769183
        sio = AsyncServer(async_mode="sanic", cors_allowed_origins=[])
        socketio_webhook = SocketVoiceBlueprint(
            sio, self.socketio_path, "socketio_webhook", __name__
        )

        # make sio object static to use in get_output_channel
        self.sio = sio

        @socketio_webhook.route("/", methods=["GET"])
        async def health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @sio.on("connect", namespace=self.namespace)
        async def connect(sid: Text, _) -> None:
            logger.debug(f"User {sid} connected to socketIO endpoint.")

        @sio.on("disconnect", namespace=self.namespace)
        async def disconnect(sid: Text) -> None:
            logger.debug(f"User {sid} disconnected from socketIO endpoint.")

        @sio.on("session_request", namespace=self.namespace)
        async def session_request(sid: Text, data: Optional[Dict]):
            if data is None:
                data = {}
            if "session_id" not in data or data["session_id"] is None:
                data["session_id"] = uuid.uuid4().hex
            if self.session_persistence:
                sio.enter_room(sid, data["session_id"])
            await sio.emit("session_confirm", data["session_id"], room=sid)
            logger.debug(f"User {sid} connected to socketIO endpoint.")

        @sio.on(self.user_message_evt, namespace=self.namespace)
        async def handle_message(sid: Text, data: Dict) -> Any:
            output_channel = SocketIOVoiceOutput(sio, self.bot_message_evt, self.botium_speech_url, self.botium_speech_apikey, self.botium_speech_language, self.botium_speech_voice)

            if self.session_persistence:
                if not data.get("session_id"):
                    rasa.shared.utils.io.raise_warning(
                        "A message without a valid session_id "
                        "was received. This message will be "
                        "ignored. Make sure to set a proper "
                        "session id using the "
                        "`session_request` socketIO event."
                    )
                    return
                sender_id = data["session_id"]
            else:
                sender_id = sid

            if data['message'] and data['message'].startswith('data:'):
                header, encoded = data['message'].split(",", 1)

                audioData = base64.b64decode(encoded.encode('ascii'))

                convertEndpoint = f"{self.botium_speech_url}/api/convert/WAVTOMONOWAV"
                logger.debug(f"handle_message - Calling Convert Endpoint: {convertEndpoint}")
                res = urlopen(Request(url=convertEndpoint, data=audioData, method='POST', headers= { 'content-type': 'audio/wav' }))
                audioDataWav = res.read()

                #with open('decoded_image.wav', 'wb') as file_to_save:
                #    file_to_save.write(audioData)

                audioEndpoint = f"{self.botium_speech_url}/api/stt/{self.botium_speech_language}"
                logger.debug(f"handle_message - Calling Speech Endpoint: {audioEndpoint}")
                res = urlopen(Request(url=audioEndpoint, data=audioDataWav, method='POST', headers= { 'content-type': 'audio/wav' }))
                resJson = json.loads(res.read().decode('utf-8'))
                logger.debug(f"handle_message - Calling Speech Endpoint: {audioEndpoint} => {resJson}")
                message = resJson["text"]

                await sio.emit(self.user_message_evt, {"text": message}, room=sid)
            else:
                message = data['message']

            message = UserMessage(
                message, output_channel, sender_id, input_channel=self.name()
            )
            await on_new_message(message)

        return socketio_webhook
