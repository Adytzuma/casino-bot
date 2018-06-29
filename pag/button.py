#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Decorator for execution logic for a given reaction to a message.

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
__all__ = 'Button', 'button_class', 'default_buttons',


import asyncio
import inspect
from typing import Any, Callable

import discord
from discord.ext import commands

from tools import funcmods, search

# Navigator object owning the button instance.
from . import navigator

OwnerT = Any

InvokePredicateT = Callable[['Button', discord.Reaction, discord.User], bool]
DisplayPredicateT = Callable[['Button'], bool]
CallbackT = Callable[['Button', discord.Reaction, discord.User], None]


class Button:
    """
    Both the callback and predicates can be either coroutines or functions. They
    will automatically be converted to coroutine types if they are not already.

    Navigators and controls are expected to set the ``owner`` attribute.
    """

    def __init__(self, callback: CallbackT, *, emoji: str, name=None) -> None:
        self.callback = funcmods.ensure_coroutine_function(callback)
        self.name = name or callback.__name__
        self.emoji = emoji
        self.description = inspect.cleandoc(inspect.getdoc(callback) or '')
        self._display_conditions = []
        self._invoke_conditions = []
        self.owner: navigator.BaseNavigator = None

    def invoke_if(self, predicate: InvokePredicateT) -> InvokePredicateT:
        """
        Decorates a predicate that determines if the button should respond to
        a given reaction.

        This predicate takes the same signature that ``Client.on_reaction_add``
        would, but a reference to this button object is the first parameter.
        Unless all predicates return True, then we do not invoke the button.

        Access the owner navigation state via the button's ``owner`` attribute.
        """
        coro = funcmods.ensure_coroutine_function(predicate)
        self._invoke_conditions.append(coro)
        return predicate

    def display_if(self, predicate: DisplayPredicateT) -> DisplayPredicateT:
        """
        Decorates a predicate that determines if the button should display.

        This predicate takes this button instance as the only parameter. Access
        the owner navigation state via the button's ``owner`` attribute.

        Unless all predicates return True, then we do not display the
        button. It is not recommended to alter this condition a lot, as we
        """
        coro = funcmods.ensure_coroutine_function(predicate)
        self._display_conditions.append(coro)
        return predicate

    async def should_show(self) -> bool:
        """Return true if the button should display."""
        for coro in self._display_conditions:
            if not await coro(self):
                return False
        return True

    async def invoke(self, reaction: discord.Reaction, user: discord.User) -> None:
        """Invokes the callback if all predicates for invocation are true."""
        for coro in self._invoke_conditions:
            if not await coro(self, reaction, user):
                return
        await self.callback(self, reaction, user)


def button(*, emoji: str, name=None):
    """Shorthand decorator for ``Button``."""

    def decorator(coro):
        """Decorates a coroutine to make it into a button."""
        return Button(coro, emoji=emoji, name=name)

    return decorator


def button_class(*, name=None, emoji):
    """
    A button class factory method. This is used to create stateful custom button
    definitions in this file. If you want, you can use it elsewhere if it suits
    your design use case.

    Keyword Args:
         name: Optional button name.
         emoji: Required emoji to react with.
    Returns:
        A class for a button.
    """

    def decorator(coro):
        """Decorates a coroutine."""

        class __MetaButton(Button):
            __name__ = 'Button'
            __qualname__ = 'Button'

            _proto_display_ifs = []
            _proto_invoke_ifs = []

            def __init__(self):
                super().__init__(coro, name=name, emoji=emoji)
                for coro_ in self._proto_display_ifs:
                    self.display_if(coro_)
                for coro_ in self._proto_invoke_ifs:
                    self.invoke_if(coro_)

            @classmethod
            def proto_display_if(cls, coro_):
                """Adds a callback to be added to each instance of the button created."""
                cls._proto_display_ifs.append(coro_)
                return coro_

            @classmethod
            def proto_invoke_if(cls, coro_):
                """Adds a callback to be added to each instance of the button created."""
                cls._proto_invoke_ifs.append(coro_)
                return coro_

        return __MetaButton

    return decorator


@button_class(emoji='\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
async def first_page(btn: Button, _react: discord.Reaction, _user: discord.User):
    """Navigates to the first page."""
    btn.owner.page_index = 0


@first_page.proto_display_if
async def first_page_display_if(button):
    return len(button.owner) > 3


@button_class(emoji='\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}')
async def back_10_pages(btn: Button, _react: discord.Reaction, _user: discord.User):
    """Navigates back 10 pages."""
    btn.owner.page_index -= 10
    
    
@back_10_pages.proto_display_if
async def back_10_pages_display_if(button):
    return len(button.owner) > 10


@button_class(emoji='\N{BLACK LEFT-POINTING TRIANGLE}')
async def previous_page(btn: Button, _react: discord.Reaction, _user: discord.User):
    """Navigates back one page."""
    btn.owner.page_index -= 1
    
    
@previous_page.proto_display_if
async def previous_page_display_if(button):
    return len(button.owner) > 1


@button_class(emoji='\N{BLACK SQUARE FOR STOP}')
async def close(_btn: Button, _react: discord.Reaction, _user: discord.User):
    """Closes the navigation, deletes all messages associated with it."""
    raise navigator.CancelIteration(navigator.CancelAction.REMOVE_ALL_MESSAGES)


@button_class(emoji='\N{BLACK RIGHT-POINTING TRIANGLE}')
async def next_page(btn: Button, _react: discord.Reaction, _user: discord.User):
    """Navigates to the next page."""
    btn.owner.page_index += 1


@next_page.proto_display_if
async def next_page_display_if(button):
    return len(button.owner) > 1


@button_class(emoji='\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}')
async def forward_10_pages(btn: Button, _react: discord.Reaction, _user: discord.User):
    """Navigates forward 10 pages."""
    btn.owner.page_index += 10


@forward_10_pages.proto_display_if
async def forward_10_pages_display_if(button):
    return len(button.owner) > 10


@button_class(emoji='\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
async def last_page(btn: Button, _react: discord.Reaction, _user: discord.User):
    """Navigates to the last page."""
    btn.owner.page_index = -1
    
    
@last_page.proto_display_if
async def last_page_display_if(button):
    return len(button.owner) > 3


@button_class(emoji='\N{INFORMATION SOURCE}')
async def information(_btn: Button, _react: discord.Reaction, _user: discord.User):
    """Shows info on what the buttons do."""
    pass


@button_class(emoji='\N{INPUT SYMBOL FOR NUMBERS}')
async def input_number(btn: Button, _react: discord.Reaction, _user: discord.User):
    """Allows you to enter a number and jump to that page."""
    await btn.owner.send('Not implemented.', delete_after=10, add_to_list=False)
    
    
@input_number.proto_display_if
async def input_number_display_if(button):
    return len(button.owner) > 3


@button_class(emoji='\N{BUSTS IN SILHOUETTE}')
async def lock_unlock(_btn: Button, _react: discord.Reaction, _user: discord.User):
    """
    Allows the author to specify who else can control the navigation.

    \N{BUST IN SILHOUETTE} - Restrict to only the author.
    \N{BUSTS IN SILHOUETTE} - Give someone else ownership.

    Specify `everyone` to allow anyone to use it.
    """
    lock = _btn.__dict__.setdefault('_lock', asyncio.Lock())

    # Prevent spamming this button and causing weird stuff to happen.
    if lock.locked():
        return

    async with lock:
        if _btn.owner.owner == _btn.owner.invoked_by.author:
            prompt = None
            try:
                prompt = await _btn.owner.send(
                    'Enter the member to transfer the pagination ownership to.'
                    '\n'
                    'Reply with `*` to give everyone control; reply with a `.` to cancel.',
                    add_to_list=False
                )

                def check(message):
                    """Filters the message."""
                    return (
                            message.author == _btn.owner.invoked_by.author
                            and message.channel == _btn.owner.channel
                    )

                m = await _btn.owner.bot.wait_for('message', check=check, timeout=30)
                try:
                    await m.delete()
                finally:
                    m_content = m.content

                try:
                    await prompt.delete()
                except (discord.NotFound, discord.Forbidden):
                    pass

                if m_content == '*':
                    _btn.owner.owner = None
                elif m_content.lower() == '.':
                    return
                else:
                    # noinspection PyProtectedMember
                    root = _btn.owner._root
                    member = search.find(lambda m: m.mention == m_content
                                                   or m.name == m_content
                                                   or m.nick == m_content
                                                   or (m_content.isdigit() and int(m_content) == m.id),
                                         root.guild.members)
                    if not member:
                        raise commands.BadArgument
                        
                    if member.bot:
                        await _btn.owner.send('Cannot transfer to a bot.',
                                              delete_after=10, add_to_list=False)
                        return
                    else:
                        _btn.owner.owner = member

                await _btn.owner.send('\N{OK HAND SIGN}', delete_after=3, add_to_list=False)
            except commands.BadArgument:
                await _btn.owner.send('Invalid input.', delete_after=10, add_to_list=False)
                return
            else:
                # Adjust our button in the list in the owner, otherwise it will
                # no longer respond to us...
                del _btn.owner.buttons[_btn.emoji]
                _btn.emoji = '\N{BUST IN SILHOUETTE}'
                _btn.owner.buttons[_btn.emoji] = _btn
            finally:

                # Delete that response.
                if prompt is not None:
                    try:
                        await prompt.delete()
                    except (discord.NotFound, discord.Forbidden):
                        pass
        else:
            # Re-lock
            _btn.owner.owner = _btn.owner.invoked_by.author
            await _btn.owner.send('\N{OK HAND SIGN}: you have full control again', delete_after=10)
            # Adjust our button in the list in the owner, otherwise it will
            # no longer respond to us...
            del _btn.owner.buttons[_btn.emoji]
            _btn.emoji = '\N{BUSTS IN SILHOUETTE}'
            _btn.owner.buttons[_btn.emoji] = _btn


@lock_unlock.proto_invoke_if
async def lock_unlock_invoke_if(b, _, u):
    """This button is special in that it will only respond to the author."""
    return u == b.owner.invoked_by.author


@lock_unlock.proto_display_if
async def lock_unlock_display_if(btn):
    # noinspection PyProtectedMember
    return btn.owner._root.guild is not None


def default_buttons():
    """Generates a bunch of default button instances."""
    return (
        first_page(),
        back_10_pages(),
        previous_page(),
        close(),
        next_page(),
        forward_10_pages(),
        last_page(),
        lock_unlock()
    )
