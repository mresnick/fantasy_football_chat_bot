"""
A bot message in structured form.

The bot sends the same content to GroupMe, Slack and Discord, but only Discord
can render a rich embed. A Report holds the content once and renders it either
way: to_text() produces the plain string GroupMe and Slack have always received,
and to_embed() produces a Discord embed of the same material.

Reports built with from_text() round-trip exactly, so wrapping an existing
report function changes nothing for the text platforms.
"""

from datetime import datetime, timezone

# Discord's documented embed limits.
MAX_TITLE = 256
MAX_DESCRIPTION = 4096
MAX_FIELDS = 25
MAX_FIELD_NAME = 256
MAX_FIELD_VALUE = 1024
MAX_FOOTER = 2048
MAX_EMBED_TOTAL = 6000

# Colour of the accent bar, chosen per report type so a busy channel is scannable.
GOLD = 0xFFD700
BLUE = 0x3498DB
GREEN = 0x2ECC71
RED = 0xE74C3C
PURPLE = 0x9B59B6
ORANGE = 0xE67E22
GREY = 0x95A5A6


class Report:
    """
    Structured content for one bot message.

    Parameters
    ----------
    title : str
        Headline. Becomes the embed title and the first text line.
    body : list of str, optional
        Lines that belong together, such as a scoreboard or standings table.
        Rendered inside a code fence in the embed so columns stay aligned.
    fields : list, optional
        (name, value) or (name, value, inline) tuples. Each becomes an embed
        field, and a name/value line pair in the text rendering.
    description : str, optional
        A short line under the title.
    color : int, optional
        Embed accent colour.
    footer : str, optional
        Small print under the embed. Omitted from the text rendering, which has
        nowhere sensible to put it.
    monospace_body : bool, optional
        Whether to wrap body lines in a code fence in the embed, default True.
    """

    def __init__(self, title=None, body=None, fields=None, description=None,
                 color=None, footer=None, monospace_body=True):
        self.title = title
        self.body = list(body) if body else []
        self.fields = list(fields) if fields else []
        self.description = description
        self.color = color
        self.footer = footer
        self.monospace_body = monospace_body

    def _normalised_fields(self):
        """Fields as uniform (name, value, inline) triples."""
        out = []
        for field in self.fields:
            if len(field) == 3:
                name, value, inline = field
            else:
                name, value = field
                inline = True
            out.append((str(name), str(value), bool(inline)))
        return out

    def to_text(self):
        """
        Render as the plain string used by GroupMe and Slack.

        Fields become alternating name/value lines, which is the shape the bot's
        messages have always had.
        """
        lines = []
        if self.title:
            lines.append(self.title)
        if self.description:
            lines.append(self.description)
        lines.extend(self.body)
        for name, value, _ in self._normalised_fields():
            lines.append(name)
            lines.append(value)
        return '\n'.join(lines)

    def _rendered_description(self):
        """Description text before any truncation."""
        parts = []
        if self.description:
            parts.append(self.description)
        if self.body:
            block = chr(10).join(self.body)
            parts.append('```' + chr(10) + block + chr(10) + '```'
                         if self.monospace_body else block)
        return chr(10).join(parts)

    def to_embed(self):
        """Render as a Discord embed payload."""
        embed = {}

        if self.title:
            embed['title'] = self.title[:MAX_TITLE]

        description = self._rendered_description()
        if description:
            embed['description'] = description[:MAX_DESCRIPTION]

        if self.color is not None:
            embed['color'] = self.color

        fields = []
        for name, value, inline in self._normalised_fields()[:MAX_FIELDS]:
            if not name or not value:
                # Discord rejects an embed with an empty field name or value.
                continue
            fields.append({'name': name[:MAX_FIELD_NAME],
                           'value': value[:MAX_FIELD_VALUE],
                           'inline': inline})
        if fields:
            embed['fields'] = fields

        if self.footer:
            embed['footer'] = {'text': self.footer[:MAX_FOOTER]}

        embed['timestamp'] = datetime.now(timezone.utc).isoformat()
        return embed

    def embed_size(self):
        """
        Characters Discord counts against the 6000 limit, before truncation.

        Measured on the untruncated content on purpose: measuring what to_embed()
        already clamped would report every oversized report as fitting, and the
        content would be silently cut instead of falling back to text.
        """
        size = len(self.title or '') + len(self._rendered_description())
        size += len(self.footer or '')
        for name, value, _ in self._normalised_fields():
            size += len(name) + len(value)
        return size

    def fits_embed(self):
        """
        Whether this renders as a Discord embed with nothing lost.

        False for anything that would need clamping, so the caller falls back to
        the plain text path (which splits cleanly) rather than truncating.
        """
        if not (self.title or self.body or self.fields):
            return False

        fields = self._normalised_fields()
        if len(fields) > MAX_FIELDS:
            return False
        if len(self.title or '') > MAX_TITLE:
            return False
        if len(self.footer or '') > MAX_FOOTER:
            return False
        if len(self._rendered_description()) > MAX_DESCRIPTION:
            return False
        for name, value, _ in fields:
            if len(name) > MAX_FIELD_NAME or len(value) > MAX_FIELD_VALUE:
                return False

        return self.embed_size() <= MAX_EMBED_TOTAL


def from_text(text, color=None, footer=None, monospace=True):
    """
    Wrap an existing plain-text report.

    The first line becomes the title and the rest the body, so to_text()
    reproduces the input exactly while Discord still gets a titled, coloured,
    timestamped card.

    Parameters
    ----------
    text : str
        The report as one of the get_* functions returns it.
    color : int, optional
        Embed accent colour.
    footer : str, optional
        Small print for the embed.
    monospace : bool, optional
        Whether the body is a table that needs a code fence, default True.

    Returns
    -------
    Report or None
        None for empty input, so callers can treat it the same as an empty string.
    """
    if not text:
        return None
    lines = text.split('\n')
    return Report(title=lines[0], body=lines[1:], color=color, footer=footer,
                  monospace_body=monospace)


# Accent colour per bot function, so a busy channel is scannable at a glance.
FUNCTION_COLORS = {
    'get_matchups': BLUE,
    'get_scoreboard_short': BLUE,
    'get_projected_scoreboard': GREY,
    'get_close_scores': ORANGE,
    'get_monitor': RED,
    'get_power_rankings': PURPLE,
    'get_trophies': GOLD,
    'get_final': GOLD,
    'get_standings': BLUE,
    'get_playoff_picture': BLUE,
    'get_waiver_report': GREEN,
    'get_draft_report': ORANGE,
    'get_draft_reminder': ORANGE,
    'win_matrix': PURPLE,
    'trophy_recap': GOLD,
    'get_cmc_still_injured': RED,
    'init': GREY,
    'broadcast': GREY,
}
