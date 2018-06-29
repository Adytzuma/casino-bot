#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Implementation that takes a collection of string chunks, sending the first to
a given channel. It then displays a set of reactions on the message that when
the user interacts with them, it will change the content of the message.

This emulates an interface that allows "turning of pages" by adding discord
reactions to the message.

====

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__all__ = (
    'BaseNavigator', 'StringNavigator', 'EmbedNavigator', 'FakeContext', 'CancelAction',
    'CancelIteration',
)


import abc
import asyncio
import collections
import enum
import traceback
from typing import Generic, Sequence, TypeVar, Union, Optional, TYPE_CHECKING

import async_timeout
import discord
from discord.ext import commands

# Stops looped lookups failing.
if TYPE_CHECKING:
    from . button import Button


PageT = TypeVar('PageT')

ChannelT = Union[discord.TextChannel, discord.DMChannel]


class Flag:
    """Settable/unsettable flag."""
    __slots__ = 'value',

    def __init__(self, value: bool):
        self.value = value

    def set(self):
        """Sets the flag."""
        self.value = True

    def reset(self):
        """Unsets the flag."""
        self.value = False

    def __bool__(self):
        return self.value


class CancelAction(enum.IntFlag):
    """Represents a cleanup action to perform on the navigator terminating."""
    DO_NOTHING = 0x0
    REMOVE_REACTS = 0x1
    REMOVE_NON_ROOT_MESSAGES = 0x2
    REMOVE_ROOT_MESSAGE = 0x4
    REMOVE_INVOCATION = 0x8

    REMOVE_ALL_SENT_MESSAGES = REMOVE_NON_ROOT_MESSAGES | REMOVE_ROOT_MESSAGE
    REMOVE_ALL_MESSAGES = REMOVE_ALL_SENT_MESSAGES | REMOVE_INVOCATION


class CancelIteration(Exception):
    """Raised to signal the navigator should terminate."""
    __slots__ = 'requested_behaviour',

    def __init__(self, requested_behaviour: Union[int, CancelAction]):
        """
        Init the exception.

        Args:
            requested_behaviour:
                Requested behaviour regarding how to tidy up messages on exit.
        """
        self.requested_behaviour = requested_behaviour


class FakeContext:
    """Context-compatible object."""
    __slots__ = 'author', 'message', 'bot'

    def __init__(self, author: discord.User, message: discord.Message, bot: discord.Client):
        self.author, self.message, self.bot = author, message, bot

    @property
    def guild(self) -> Optional[discord.Guild]:
        """The guild, or None if a DM."""
        return self.message.guild

    @property
    def channel(self) -> ChannelT:
        """The channel."""
        return self.message.channel


class BaseNavigator(abc.ABC, Generic[PageT]):
    """
    Navigation for a set of pages, given a set of button objects to display as reactions.

    Args:
        ctx:
            the command context to invoke in response to. If you are using this in
            an event listener, you can generate a ``FakeContext`` to go in here.
        pages:
            A sequence of elements to display.
        buttons:
            A sequence of ``Button`` objects.

    Keyword Args:
        timeout:
            An integer or floating point positive number representing the number of seconds
            to be inactive for before destroying this navigation session. Defaults to 300s
            (5 minutes).
        initial_page:
            The initial page index to start on. Defaults to 0.

    Attributes:
        owner:
            The original user who invoked the event leading to this navigator being displayed.
            Change this to alter who has control over the navigator. Set to None to unlock the
            navigator to all users for control.
        channel:
            The channel we are responding in.
        bot:
            The bot that is sending this paginator. Can be anything derived from discord.Client.
        pages:
            The sequence of pages to display from.
        buttons:
            The ordered mapping of emoji to button for reactions to display.
        timeout:
            The inactive timeout period.
        invoked_by:
            The original invoking message.
        _root:
            The root message. This is only used internally and by derived implementations.

    Notes:
        Buttons can take control of most parts of this object. To kill the pagination
        early, one should raise a ``CancelIteration`` from the button logic. This exception
        can take an argument that consists of a combination of one or more ``CancelAction``
        enumerations combined via bitwise-or. These flags allow custom specification of what
        to do on cleaning up (e.g. should we delete the root message, or just clear the reactions?)

    """
    def __init__(self,
                 ctx: Union[commands.Context, FakeContext],
                 pages: Sequence[PageT],
                 buttons: Sequence['Button']=None,
                 *,
                 timeout: float = 300,
                 initial_page: int = 0):
        if buttons is None:
            from . import button
            buttons = button.default_buttons()

        if timeout is None:
            raise TypeError('Expected int or float, not NoneType.')
        elif timeout <= 0:
            raise ValueError('Cannot have a non-positive timeout.')
        else:
            self._is_ready = asyncio.Event(loop=ctx.bot.loop)
            self._is_finished = asyncio.Event(loop=ctx.bot.loop)
            self._event_queue = asyncio.Queue(loop=ctx.bot.loop)
            # Messages sent by this navigator. The first in this list is considered
            # to be the root message.
            self._messages = []
            # Flag set internally if anything is altered. Saves bandwidth for
            # otherwise pointless operations.
            self._should_refresh = Flag(False)

            self.owner = ctx.author
            self.channel = ctx.channel
            self.bot = ctx.bot
            self.pages = pages

            self._page_index = 0
            self.page_index = initial_page

            # Register ownership.
            for button in buttons:
                button.owner = self
            self.buttons = collections.OrderedDict((btn.emoji, btn) for btn in buttons)

            self.timeout = timeout
            self.invoked_by = ctx.message

    def create_future(self, coro):
        """Creates a task and mutes any errors to single lines."""
        t = self.loop.create_task(coro)

        @t.add_done_callback
        def on_done(error):
            try:
                t.result()
            except Exception as ex:
                print(f'{coro} task raised {type(ex).__name__} {ex} because of {error}')

        return t

    @property
    def loop(self):
        """The main event loop the bot is running."""
        return self.bot.loop

    def __await__(self):
        """Await the completion of the Navigator."""
        return self._is_finished.wait()

    def __len__(self):
        return len(self.pages)

    @property
    def _root(self):
        return self._messages[0]

    async def send(self, *args, **kwargs):
        """Internal helper for sending messages."""
        add_to_list = kwargs.pop('add_to_list', True)

        m = await self.channel.send(*args, **kwargs)

        if add_to_list:
            self._messages.append(m)

        return m

    @_root.setter
    def _root(self, message):
        if not self._messages:
            self._messages = [message]
        else:
            self._messages[0] = message

    @property
    def current_page(self) -> PageT:
        """Gets the current page that should be being displayed."""
        return self.pages[self.page_index]

    @property
    def page_index(self):
        """Gets/sets the page index (0-based)."""
        return self._page_index

    @page_index.setter
    def page_index(self, index):
        size = len(self)

        while index < 0:
            index += size

        while index >= size:
            index -= size

        if index != self.page_index:
            self._should_refresh.set()

        self._page_index = index

    @property
    def page_number(self):
        """Gets/sets the page number (1-based, does not support out of range)."""
        return self.page_index + 1

    @page_number.setter
    def page_number(self, number):
        if 1 <= number <= len(self):
            self.page_index = number - 1
        else:
            raise ValueError('Invalid page number')

    def lock(self):
        """Reset the owner of the control."""
        self.owner = self.invoked_by.author

    def unlock(self):
        """Allow anyone to use the control."""
        self.owner = None

    async def __on_reaction_add(self, reaction, user):
        """Sends a reaction addition event."""

        if self._is_ready.is_set() and self._messages:
            if reaction.message.id != self._root.id:
                return

            # Update our state!
            self._root = reaction.message

            not_me = user != self.bot.user

            valid_button = reaction.emoji in self.buttons

            is_in_whitelist = (
                self.owner is None or user == self.owner or user == self.invoked_by.author
            )

            if not_me and valid_button and is_in_whitelist:
                await self._event_queue.put((reaction, user))

    async def __on_message_delete(self, message):
        """Sends a message deletion event for any message we made in this navigator."""
        if self._is_ready.is_set():
            message = discord.utils.get(self._messages, id=message.id)
            if message is not None:
                self._messages.remove(message)
            if self._messages and self._messages[0].id == message.id:
                self.__task.cancel()

    async def __handle_reaction(self, reaction, user):
        """Dispatches a reaction."""
        emoji = reaction.emoji
        # noinspection PyUnresolvedReferences
        await self.buttons[emoji].invoke(reaction, user)

    @abc.abstractmethod
    async def _edit_page(self):
        """Logic for changing whatever is on Discord to display the correct value."""
        ...

    def format_page_number(self) -> str:
        """Formats the page number."""
        return f'[{self.page_number}/{len(self)}]\n'

    def start(self):
        self.__task = self.loop.create_task(self._run())
        @self.__task.add_done_callback
        def on_done(_):
            del self.__task
            
        return self.__task    
        
    async def _run(self):
        """Runs the main logic loop for the navigator."""
        if self._is_ready.is_set():
            raise RuntimeError('Already running this navigator.')

        self.bot.listen('on_message_delete')(self.__on_message_delete)
        self.bot.listen('on_reaction_add')(self.__on_reaction_add)

        try:
            async def produce_page():
                # Initialise the first page.
                self._root = await self.send('Loading...')
                self.create_future(self._edit_page())
                return self._root

            await produce_page()

            self._is_finished.clear()
            self._is_ready.set()

            try:
                while True:
                    # Ensure the reactions are all correct. If they are not, then
                    # attempt to adjust them.
                    try:
                        # Refresh the root message state
                        # self.__root = await self.channel.get_message(self.__root.id)
                        try:
                            root = self._root
                        except IndexError:
                            root = await produce_page()

                        current_reacts = root.reactions
                        expected_reacts = [
                            b.emoji
                            for b in self.buttons.values()
                            if await b.should_show()
                        ]

                        for react in current_reacts:
                            # If the current react doesn't match the one at the list head,
                            # then we assume it should not be here, so we remove it. If we
                            # have got to the end of our targets list, we assume everything
                            # else is garbage, and thus we delete it.
                            if not expected_reacts or react.emoji != expected_reacts[0]:
                                async for user in react.users():
                                    self.create_future(root.remove_reaction(react, user))

                            # If there are still targets left to check and the current
                            # reaction is the next target, remove all reacts that are not by
                            # me.
                            elif react.emoji == expected_reacts[0]:
                                expected_reacts.pop(0)
                                async for user in react.users():
                                    # Ignore our own react. We want to keep that.
                                    if user != self.bot.user:
                                        self.create_future(root.remove_reaction(react, user))

                    except discord.Forbidden:
                        # If we can't update them, just continue.
                        pass
                    else:
                        # If we did not validate all targets by now, we know they are
                        # missing and should be added
                        if expected_reacts:
                            try:
                                for r in expected_reacts:
                                    await self._root.add_reaction(r)
                            except Exception:
                                await self.channel.send('I lack the ADD_REACTIONS permission.')
                                raise CancelIteration(CancelAction.REMOVE_ALL_MESSAGES)
                    # Get next event, or wait.
                    # This is essentially a polling pipe between the event captures
                    # and the handlers. I could have used wait_for, but that encouraged
                    # spaghetti code in the old paginator. This is more modular and
                    # easy to understand.
                    # This is required to enable us to intercept signals sent via
                    # exceptions.
                    with async_timeout.timeout(self.timeout):
                        reaction, user = await self._event_queue.get()
                        await self.__handle_reaction(reaction, user)

                    if self._should_refresh:
                        self.create_future(self._edit_page())
                        self._should_refresh.reset()

            except (asyncio.TimeoutError, discord.NotFound):
                raise CancelIteration(CancelAction.REMOVE_NON_ROOT_MESSAGES
                                      | CancelAction.REMOVE_REACTS)

        except CancelIteration as ex:
            # Request to shut down the navigator.
            r = ex.requested_behaviour

            if r & CancelAction.REMOVE_ROOT_MESSAGE:
                try:
                    await self._root.delete()
                except (discord.NotFound, discord.Forbidden, IndexError, ValueError):
                    pass
            elif r & CancelAction.REMOVE_REACTS:
                try:
                    await self._root.clear_reactions()
                except (discord.NotFound, discord.Forbidden, IndexError, ValueError):
                    pass

            if r & CancelAction.REMOVE_NON_ROOT_MESSAGES:
                try:
                    await asyncio.gather(*[m.delete() for m in self._messages[1:]])
                except (discord.NotFound, discord.Forbidden, IndexError, ValueError):
                    pass

            if r & CancelAction.REMOVE_INVOCATION:
                try:
                    await self.invoked_by.delete()
                except (discord.NotFound, discord.Forbidden, IndexError, ValueError):
                    pass

        finally:
            self._is_ready.clear()
            self._is_finished.set()

            # Remove the listeners.
            try:
                self.bot.remove_listener(self.__on_message_delete)
            except Exception as ex:
                traceback.print_exception(type(ex), ex, ex.__traceback__)

            try:
                self.bot.remove_listener(self.__on_reaction_add)
            except Exception as ex:
                traceback.print_exception(type(ex), ex, ex.__traceback__)


class StringNavigator(BaseNavigator[str]):
    """Navigator for string content."""
    async def _edit_page(self):
        """
        Edits the displayed page on Discord. This is the opportunity to add a page number
        to the content if there is room.
        """
        page_header = self.format_page_number()
        content = self.current_page

        if len(content) + len(page_header) <= 2000:
            content = page_header + content

        await self._root.edit(content=content)


class EmbedNavigator(BaseNavigator[discord.Embed]):
    """Navigator for embed content."""
    async def _edit_page(self):
        """
        Edits the displayed page on Discord.
        """
        page_header = self.format_page_number()
        content = self.current_page

        await self._root.edit(content=page_header, embed=content)
